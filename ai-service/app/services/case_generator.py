"""
Case Generator — LangChain-powered procedural mystery case generation.

Uses HuggingFace Inference API for LLM-based generation with a multi-step
pipeline. Falls back to template-based generation when no API token is configured.
"""

import json
import logging
import random
import threading
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.config import settings
from app.models.db_models import (
    CaseDB,
    CaseFileDB,
    CaseGenerationRequestDB,
    EvidenceDB,
    SuspectDB,
    VictimDB,
)

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────

VALID_MOODS = [
    "dark", "foggy", "melancholic", "neon", "sterile", "paranoid",
    "eerie", "nostalgic", "warm", "cold", "urban", "rural",
    "industrial", "coastal", "small-town",
]

VALID_ERAS = ["1950s", "1960s", "1970s", "1980s", "1990s", "2000s", "2010s"]

CRIME_TYPES = [
    "Murder", "Disappearance", "Poisoning", "Arson / Murder",
    "Theft / Murder", "Kidnapping / Suspected Murder",
]

EVIDENCE_TYPES = ["PHYSICAL", "TESTIMONIAL", "FORENSIC", "DOCUMENTARY"]

CASE_FILE_TYPES = [
    "CRIME_SCENE_REPORT", "WITNESS_STATEMENT", "FORENSIC_ANALYSIS",
    "NEWSPAPER_CLIPPING", "POLICE_NOTES",
]

# ── Template pools for fallback generation ─────────────

TITLE_TEMPLATES = [
    ("The {adjective} {place}", ["dark", "silent", "forgotten", "burning", "hollow"],
     ["Chapel", "Motel", "Bridge", "Diner", "Lighthouse", "Orchard", "Mansion", "Ferry", "Cannery", "Mill"]),
    ("{possessive}'s {noun}", ["Widow", "Judge", "Doctor", "Priest", "Stranger", "Collector", "Mayor", "Sailor"],
     ["Secret", "Confession", "Alibi", "Silence", "Shadow", "Debt", "Reckoning", "Promise"]),
    ("The {event} at {place}", ["Incident", "Affair", "Vanishing", "Fire", "Drowning", "Murder"],
     ["Blackwood Manor", "Pier 17", "the Rail Yard", "Cedar Falls", "the Old Mill", "Skeleton Key Inn"]),
]

VICTIM_NAMES = [
    ("Harold Mercer", 62, "Retired judge"),
    ("Catherine Byrne", 38, "Investigative journalist"),
    ("Dominic Russo", 45, "Restaurant owner"),
    ("Margaret Linden", 71, "Philanthropist"),
    ("Tyler Okafor", 29, "Marine biologist"),
    ("Elena Vasquez", 33, "Civil engineer"),
    ("Robert Crane", 55, "High school principal"),
    ("Nadia Petrov", 41, "Antique dealer"),
    ("Samuel Ashworth", 67, "Former police chief"),
    ("Grace Tanaka", 36, "Gallery curator"),
]

CAUSES_OF_DEATH = [
    "Blunt force trauma to the head",
    "Strangulation with a ligature",
    "Poisoning — arsenic detected in blood toxicology",
    "Single gunshot wound to the chest",
    "Drowning — injuries suggest victim was unconscious when submerged",
    "Stabbing — single wound to the abdomen with a serrated blade",
    "Hypothermia — found outdoors in freezing conditions, signs of restraint on wrists",
    "Fall from height — pushed from an elevated structure",
]

OCCUPATIONS = [
    "Mechanic", "Lawyer", "Nurse", "Banker", "Teacher", "Bartender",
    "Real estate agent", "Retired military officer", "Librarian",
    "Local politician", "Contractor", "Pharmacist", "Church deacon",
    "Fishing boat captain", "Inn owner", "Journalist", "Doctor",
    "Social worker", "County clerk", "Rancher",
]

PERSONALITY_POOLS = [
    ["charming", "evasive", "calculating"],
    ["nervous", "loyal", "easily rattled"],
    ["stoic", "secretive", "meticulous"],
    ["hot-tempered", "impulsive", "regretful"],
    ["cold", "intelligent", "manipulative"],
    ["warm", "protective", "hiding guilt"],
    ["bitter", "sarcastic", "observant"],
    ["jovial", "dishonest", "self-serving"],
]

RELATIONSHIP_TYPES = [
    "Spouse of the victim", "Business partner", "Neighbor",
    "Former lover", "Employee of the victim", "Close friend",
    "Rival", "Family member (sibling)", "Tenant", "Colleague",
]

# ── LLM prompt templates ──────────────────────────────

STEP1_CONCEPT_PROMPT = """\
You are a mystery writer. Generate a cold case concept as valid JSON.

Parameters:
- Mood: {mood_tags}
- Era: {era}
- Difficulty: {difficulty}/5
- Crime type: {crime_type}

Return ONLY a JSON object (no markdown, no extra text):
{{
  "title": "case title",
  "setting_description": "2-3 sentence atmospheric description of the location",
  "synopsis": "one punchy sentence teaser",
  "victim_name": "full name",
  "victim_age": number,
  "victim_occupation": "occupation",
  "victim_cause_of_death": "cause of death",
  "victim_background": "2-3 sentence background"
}}"""

STEP2_SUSPECTS_PROMPT = """\
You are a mystery writer creating suspects for: "{title}" — {synopsis}
Victim: {victim_name}, {victim_occupation}. {victim_background}
Mood: {mood_tags}. Era: {era}. Crime: {crime_type}.

Create {num_suspects} suspects. One MUST be guilty.
Return ONLY a JSON array (no markdown):
[
  {{
    "name": "full name",
    "age": number,
    "occupation": "occupation",
    "relationship_to_victim": "relationship",
    "personality_traits": ["trait1", "trait2", "trait3"],
    "alibi": "their stated alibi",
    "hidden_knowledge": "what they know but won't reveal",
    "is_guilty": true/false
  }}
]"""

STEP3_EVIDENCE_PROMPT = """\
You are a mystery writer creating evidence for: "{title}"
Suspects: {suspect_names}. Guilty: {guilty_suspect}. Crime: {crime_type}. Era: {era}.

Create {num_evidence} evidence items. Include {num_red_herrings} red herrings.
Types: PHYSICAL, TESTIMONIAL, FORENSIC, DOCUMENTARY.

Return ONLY a JSON array:
[
  {{
    "type": "EVIDENCE_TYPE",
    "title": "short title",
    "description": "2-3 sentence description",
    "linked_suspect_indices": [0],
    "is_red_herring": false
  }}
]"""

STEP4_FILES_PROMPT = """\
You are a mystery writer creating case files for: "{title}" — {synopsis}
Set in the {era}. Location: {setting_description}
Victim: {victim_name}. Suspects: {suspect_names}.

Create {num_files} case files of these types: CRIME_SCENE_REPORT, WITNESS_STATEMENT, FORENSIC_ANALYSIS, NEWSPAPER_CLIPPING, POLICE_NOTES.

Return ONLY a JSON array:
[
  {{
    "type": "CASE_FILE_TYPE",
    "title": "document title",
    "content": "full text content (4-8 paragraphs)",
    "classification_level": "STANDARD or CONFIDENTIAL"
  }}
]"""


class CaseGenerator:
    """Generates complete mystery cases using LLM or template fallback."""

    def __init__(self):
        self._llm = None
        self._init_llm()

    def _init_llm(self):
        if settings.huggingface_api_token:
            try:
                from langchain_huggingface import HuggingFaceEndpoint
                self._llm = HuggingFaceEndpoint(
                    repo_id="mistralai/Mistral-7B-Instruct-v0.3",
                    huggingfacehub_api_token=settings.huggingface_api_token,
                    max_new_tokens=2000,
                    temperature=0.8,
                    top_p=0.9,
                )
                logger.info("HuggingFace LLM initialized for case generation")
            except Exception as e:
                logger.warning(f"LLM init failed, using template fallback: {e}")
                self._llm = None
        else:
            logger.info("No HuggingFace token — using template-based case generation")

    def _resolve_params(
        self,
        mood_tags: Optional[list[str]] = None,
        era: Optional[str] = None,
        difficulty: Optional[int] = None,
        crime_type: Optional[str] = None,
    ) -> dict:
        """Fill in missing params with random values."""
        if not mood_tags:
            mood_tags = random.sample(VALID_MOODS, k=random.randint(2, 3))
        if not era:
            era = random.choice(VALID_ERAS)
        if difficulty is None:
            difficulty = random.randint(2, 5)
        if not crime_type:
            crime_type = random.choice(CRIME_TYPES)
        return {
            "mood_tags": mood_tags,
            "era": era,
            "difficulty": max(1, min(5, difficulty)),
            "crime_type": crime_type,
        }

    async def _call_llm(self, prompt: str) -> Optional[str]:
        """Call LLM and return the raw text response."""
        if not self._llm:
            return None
        try:
            response = await self._llm.ainvoke(prompt)
            return response.strip()
        except Exception as e:
            logger.warning(f"LLM call failed: {e}")
            return None

    def _parse_json(self, text: str) -> Optional[any]:
        """Attempt to parse JSON from LLM response (handles markdown fences)."""
        if not text:
            return None
        # Strip markdown code fences
        cleaned = text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Try to find JSON in the response
            for start_char, end_char in [("{", "}"), ("[", "]")]:
                start = cleaned.find(start_char)
                end = cleaned.rfind(end_char)
                if start != -1 and end != -1 and end > start:
                    try:
                        return json.loads(cleaned[start:end + 1])
                    except json.JSONDecodeError:
                        continue
            logger.warning(f"Failed to parse JSON from LLM response: {text[:200]}")
            return None

    # ── Template-based fallback generators ──────────────

    def _generate_case_number(self, era: str) -> str:
        year = random.choice(range(int(era[:4]), int(era[:4]) + 10))
        letter = random.choice("ABCDEFGHJKLMNPRSTUVWXYZ")
        return f"CASE #{year}-{letter}"

    def _generate_title(self) -> str:
        template, adj_pool, noun_pool = random.choice(TITLE_TEMPLATES)
        if "{adjective}" in template:
            return template.format(
                adjective=random.choice(adj_pool).capitalize(),
                place=random.choice(noun_pool),
            )
        elif "{possessive}" in template:
            return template.format(
                possessive=f"The {random.choice(adj_pool)}'s" if random.random() > 0.5
                else random.choice(adj_pool),
                noun=random.choice(noun_pool),
            )
        else:
            return template.format(
                event=random.choice(adj_pool),
                place=random.choice(noun_pool),
            )

    def _generate_setting(self, mood_tags: list[str], era: str) -> str:
        mood_descriptors = {
            "dark": "dimly lit",
            "foggy": "perpetually shrouded in mist",
            "melancholic": "hauntingly quiet",
            "neon": "bathed in flickering neon light",
            "sterile": "clinically clean",
            "paranoid": "under constant surveillance",
            "eerie": "unnervingly still",
            "nostalgic": "frozen in time",
            "warm": "deceptively welcoming",
            "cold": "bitterly cold",
            "urban": "surrounded by concrete and steel",
            "rural": "miles from the nearest town",
            "industrial": "filled with the hum of machinery",
            "coastal": "overlooking a restless sea",
            "small-town": "where everyone knows everyone",
        }
        locations = [
            "a converted warehouse on the edge of town",
            "a crumbling Victorian estate",
            "a roadside motel along a forgotten highway",
            "a fishing village's abandoned cannery",
            "the basement of an old courthouse",
            "a lakeside cabin surrounded by dense pine forest",
            "a downtown apartment above a closed bookshop",
            "a lighthouse on a rocky promontory",
            "a once-grand theater now shuttered and decaying",
            "a farmstead at the end of a dirt road",
        ]
        loc = random.choice(locations)
        descs = [mood_descriptors.get(m, "") for m in mood_tags if m in mood_descriptors]
        atmosphere = " and ".join(descs[:2]) if descs else "heavy with secrets"
        return (
            f"The scene is {loc}, {atmosphere}. "
            f"Set in the {era}, the location carries the weight of its era — "
            f"every surface tells a story that no one wants to hear."
        )

    def _generate_victim(self) -> dict:
        name, age, occupation = random.choice(VICTIM_NAMES)
        cause = random.choice(CAUSES_OF_DEATH)
        backgrounds = [
            f"{name} was well-known in the community but had made quiet enemies over the years. "
            f"As a {occupation.lower()}, they had access to information that some preferred to keep buried.",
            f"{name} had recently returned to town after years away. Their return stirred up old tensions "
            f"and reopened wounds the community thought had healed.",
            f"{name} lived a seemingly ordinary life as a {occupation.lower()}, but beneath the surface "
            f"lay a web of debts, secrets, and broken promises that would prove fatal.",
        ]
        return {
            "name": name,
            "age": age,
            "occupation": occupation,
            "cause_of_death": cause,
            "background": random.choice(backgrounds),
        }

    def _generate_suspects(
        self, victim: dict, num_suspects: int, crime_type: str
    ) -> list[dict]:
        used_names = {victim["name"]}
        suspects = []
        guilty_idx = random.randint(0, num_suspects - 1)

        available_rels = list(RELATIONSHIP_TYPES)
        random.shuffle(available_rels)
        available_occs = list(OCCUPATIONS)
        random.shuffle(available_occs)

        first_names_m = ["Thomas", "Richard", "James", "William", "Michael", "David", "Robert", "Anthony"]
        first_names_f = ["Sarah", "Elizabeth", "Patricia", "Dorothy", "Helen", "Marie", "Margaret", "Alice"]
        last_names = ["Hayes", "Bishop", "Ward", "Cross", "Marsh", "Porter", "Quinn", "Flynn", "Hale", "Dunn"]
        random.shuffle(first_names_m)
        random.shuffle(first_names_f)
        random.shuffle(last_names)

        for i in range(num_suspects):
            is_guilty = (i == guilty_idx)
            first_pool = first_names_f if i % 2 == 0 else first_names_m
            name = f"{first_pool[i % len(first_pool)]} {last_names[i % len(last_names)]}"
            while name in used_names:
                name = f"{random.choice(first_pool)} {random.choice(last_names)}"
            used_names.add(name)

            age = random.randint(25, 65)
            occ = available_occs[i % len(available_occs)]
            rel = available_rels[i % len(available_rels)]
            traits = random.choice(PERSONALITY_POOLS)
            alibi = (
                f"Claims to have been at home alone that evening. No witnesses can confirm."
                if is_guilty else
                f"Claims to have been at a public location. One witness partially confirms their account."
            )
            if is_guilty:
                hidden = (
                    f"{name} went to meet the victim that night. A confrontation escalated — "
                    f"{name} committed the crime in a moment of rage and panic. "
                    f"Afterward, {name} attempted to clean the scene and establish a false alibi. "
                    f"{name} is the killer."
                )
            else:
                hidden = (
                    f"{name} was near the scene that night for unrelated reasons and fears being implicated. "
                    f"They saw something suspicious but have kept quiet to protect themselves."
                )

            suspects.append({
                "name": name,
                "age": age,
                "occupation": occ,
                "relationship_to_victim": rel,
                "personality_traits": traits,
                "alibi": alibi,
                "hidden_knowledge": hidden,
                "is_guilty": is_guilty,
            })

        return suspects

    def _generate_evidence(
        self, suspects: list[dict], num_evidence: int, num_red_herrings: int
    ) -> list[dict]:
        evidence = []
        guilty_idx = next(i for i, s in enumerate(suspects) if s["is_guilty"])

        evidence_templates = [
            ("PHYSICAL", "Footprints at the Scene",
             "Partial footprints found near the scene consistent with size {size} shoes. "
             "Tread pattern matches a common work boot brand."),
            ("FORENSIC", "Autopsy — Time of Death",
             "Medical examiner places time of death between 10 PM and 1 AM. "
             "Stomach contents suggest the victim ate approximately 3 hours before death."),
            ("TESTIMONIAL", "Neighbor's Statement",
             "A neighbor reports hearing raised voices around 11 PM. "
             "Could not identify the voices but noted one was 'clearly angry.'"),
            ("DOCUMENTARY", "Victim's Phone Records",
             "Phone records show the victim received three calls from an unlisted number "
             "on the day of the crime. The last call lasted 12 minutes."),
            ("PHYSICAL", "Fiber Evidence",
             "Textile fibers found on the victim's clothing do not match any of their own garments. "
             "The fibers are consistent with a dark wool coat."),
            ("FORENSIC", "Blood Spatter Analysis",
             "Blood spatter patterns indicate the attack occurred near the {location}. "
             "The pattern suggests a single assailant."),
            ("TESTIMONIAL", "Bartender's Account",
             "Local bartender confirms one suspect was drinking heavily that night "
             "and left the bar in an agitated state around 10:30 PM."),
            ("DOCUMENTARY", "Financial Records",
             "Bank records reveal the victim had recently changed the beneficiary on their "
             "life insurance policy. The new beneficiary was not yet public knowledge."),
            ("PHYSICAL", "Damaged Personal Item",
             "A broken personal item belonging to one of the suspects was found "
             "within 50 feet of the crime scene."),
            ("FORENSIC", "Toxicology Report",
             "Trace amounts of a sedative were found in the victim's blood. "
             "The substance is available by prescription only."),
            ("TESTIMONIAL", "Security Camera Footage",
             "Grainy security footage from a nearby building shows a figure "
             "matching the build of one suspect near the scene at 11:15 PM."),
            ("DOCUMENTARY", "Threatening Letter",
             "An unsigned letter found in the victim's desk drawer reads: "
             "'You've pushed too far. There will be consequences.' Undated."),
        ]

        random.shuffle(evidence_templates)

        for i in range(min(num_evidence, len(evidence_templates))):
            ev_type, title, desc = evidence_templates[i]
            is_red_herring = i >= (num_evidence - num_red_herrings)
            if is_red_herring:
                linked = [random.randint(0, len(suspects) - 1)]
                while linked[0] == guilty_idx:
                    linked = [random.randint(0, len(suspects) - 1)]
            elif i < 3:
                linked = [guilty_idx]
            else:
                linked = [random.randint(0, len(suspects) - 1)]

            desc = desc.format(size=random.randint(8, 12), location="entrance")

            evidence.append({
                "type": ev_type,
                "title": title,
                "description": desc,
                "linked_suspect_indices": linked,
                "is_red_herring": is_red_herring,
            })

        return evidence

    def _generate_case_files(
        self,
        title: str,
        case_number: str,
        era: str,
        setting: str,
        victim: dict,
        suspects: list[dict],
        num_files: int,
    ) -> list[dict]:
        suspect_names = ", ".join(s["name"] for s in suspects)
        year = case_number.split("#")[1].split("-")[0] if "#" in case_number else era[:4]

        files = []

        files.append({
            "type": "CRIME_SCENE_REPORT",
            "title": f"Initial Crime Scene Report — {title}",
            "classification_level": "STANDARD",
            "content": (
                f"LOCAL POLICE DEPARTMENT\n"
                f"CRIME SCENE REPORT — {case_number}\n"
                f"Date: {year}\n\n"
                f"Reporting officers arrived at the scene following a call from a local resident. "
                f"The victim, {victim['name']}, {victim['age']}, was found at the location described "
                f"as follows: {setting[:200]}\n\n"
                f"Cause of death has been preliminarily identified as: {victim['cause_of_death']}.\n\n"
                f"The scene showed signs of a struggle — overturned furniture, scuff marks on the floor, "
                f"and personal effects scattered near the entrance. No forced entry was observed, "
                f"suggesting the victim knew their attacker or the door was left unlocked.\n\n"
                f"Persons of interest identified in initial canvas: {suspect_names}.\n\n"
                f"Evidence collected from the scene has been logged and sent for forensic processing."
            ),
        })

        if num_files > 1:
            witness_suspect = random.choice(suspects)
            files.append({
                "type": "WITNESS_STATEMENT",
                "title": f"Statement of {witness_suspect['name']}",
                "classification_level": "STANDARD",
                "content": (
                    f"LOCAL POLICE DEPARTMENT\n"
                    f"WITNESS STATEMENT — {case_number}\n\n"
                    f"Witness: {witness_suspect['name']}, {witness_suspect['age']}, "
                    f"{witness_suspect['occupation']}\n"
                    f"Relationship to victim: {witness_suspect['relationship_to_victim']}\n\n"
                    f"{witness_suspect['name']} states: \"{witness_suspect['alibi']} "
                    f"I had no reason to want harm to come to {victim['name']}. "
                    f"We had our differences, as anyone does, but nothing that would lead to this.\"\n\n"
                    f"When pressed on the timeline, {witness_suspect['name']} became "
                    f"{'visibly uncomfortable and requested a break' if witness_suspect['is_guilty'] else 'cooperative but clearly shaken'}.\n\n"
                    f"NOTE: Interviewing officer observed that {witness_suspect['name']} "
                    f"{'avoided direct eye contact throughout and gave inconsistent details about the evening' if witness_suspect['is_guilty'] else 'appeared genuinely surprised by several details of the case'}."
                ),
            })

        if num_files > 2:
            files.append({
                "type": "FORENSIC_ANALYSIS",
                "title": f"Forensic Analysis Report — {case_number}",
                "classification_level": "CONFIDENTIAL",
                "content": (
                    f"FORENSICS DIVISION\n"
                    f"ANALYSIS REPORT — {case_number}\n\n"
                    f"VICTIM: {victim['name']}\n"
                    f"CAUSE OF DEATH: {victim['cause_of_death']}\n\n"
                    f"Estimated time of death: between 10:00 PM and 1:00 AM based on body temperature "
                    f"and lividity patterns.\n\n"
                    f"Key findings:\n"
                    f"- Defensive wounds noted on the victim's hands and forearms\n"
                    f"- Trace evidence collected from under the victim's fingernails — sent for DNA analysis\n"
                    f"- The instrument of death appears consistent with an object of opportunity "
                    f"rather than a premeditated weapon\n\n"
                    f"CONCLUSION: The evidence suggests a confrontation that escalated rapidly. "
                    f"The attacker likely knew the victim and gained entry without force."
                ),
            })

        if num_files > 3:
            paper_name = random.choice([
                "The Daily Herald", "The Morning Courier", "The Evening Standard",
                "The Local Gazette", "The Tribune", "The Observer",
            ])
            files.append({
                "type": "NEWSPAPER_CLIPPING",
                "title": f"{paper_name} — {year}",
                "classification_level": "STANDARD",
                "content": (
                    f"{paper_name.upper()}\n{year}\n\n"
                    f"LOCAL FIGURE FOUND DEAD IN SUSPICIOUS CIRCUMSTANCES\n\n"
                    f"{victim['name']}, {victim['age']}, a well-known {victim['occupation'].lower()} "
                    f"in the community, was found dead under circumstances police describe as suspicious.\n\n"
                    f"\"We are treating this as a potential homicide and pursuing all leads,\" said the "
                    f"lead investigator. \"We urge anyone with information to come forward.\"\n\n"
                    f"Those who knew {victim['name']} expressed shock. \"This is the kind of thing "
                    f"that doesn't happen here,\" said one resident who asked not to be named. "
                    f"\"Everyone is looking over their shoulder now.\"\n\n"
                    f"The investigation is ongoing."
                ),
            })

        if num_files > 4:
            files.append({
                "type": "POLICE_NOTES",
                "title": "Lead Investigator's Notes",
                "classification_level": "CONFIDENTIAL",
                "content": (
                    f"LEAD INVESTIGATOR — PERSONAL NOTES\n"
                    f"{case_number}\n\n"
                    f"Day 1: Scene secured. Victim is {victim['name']}, {victim['occupation'].lower()}. "
                    f"Cause of death: {victim['cause_of_death'].lower()}. No witnesses to the act itself.\n\n"
                    f"Day 2: Interviewed persons of interest: {suspect_names}. "
                    f"Everyone has an alibi. At least one of them is lying.\n\n"
                    f"Day 4: Forensics confirms this was no accident. Someone wanted {victim['name']} dead "
                    f"and went to considerable trouble to make it look otherwise.\n\n"
                    f"Day 7: Cross-referencing timelines. At least two suspects have gaps in their "
                    f"accounts that they can't explain. Pressing harder.\n\n"
                    f"Day 10: Getting pushback from above. 'Not enough for an arrest.' "
                    f"I know one of these people did it. Just need the one thread to pull.\n\n"
                    f"Day 14: Case is going cold. DA won't move. Every lead circles back to "
                    f"the same three people and the same brick wall."
                ),
            })

        return files[:num_files]

    # ── Main generation logic ─────────────────────────

    async def generate_case(
        self,
        db: Session,
        mood_tags: Optional[list[str]] = None,
        era: Optional[str] = None,
        difficulty: Optional[int] = None,
        crime_type: Optional[str] = None,
    ) -> CaseDB:
        """Generate a complete mystery case and store it in the database."""
        params = self._resolve_params(mood_tags, era, difficulty, crime_type)
        num_suspects = random.randint(3, 4)
        num_evidence = random.randint(8, 12)
        num_red_herrings = random.randint(2, 3)
        num_files = random.randint(4, 5)

        # Step 1: Generate concept & victim
        concept = await self._generate_concept(params)
        victim_data = concept["victim"]

        # Step 2: Generate suspects
        suspects_data = await self._generate_suspects_step(
            concept, params, num_suspects
        )

        # Step 3: Generate evidence
        evidence_data = await self._generate_evidence_step(
            concept, suspects_data, params, num_evidence, num_red_herrings
        )

        # Step 4: Generate case files
        files_data = await self._generate_files_step(
            concept, suspects_data, params, num_files
        )

        # Step 5: Validate and store
        case = self._store_case(
            db, concept, victim_data, suspects_data, evidence_data, files_data, params
        )
        return case

    async def _generate_concept(self, params: dict) -> dict:
        """Step 1: Generate case concept and victim."""
        if self._llm:
            prompt = STEP1_CONCEPT_PROMPT.format(**params)
            raw = await self._call_llm(prompt)
            parsed = self._parse_json(raw)
            if parsed and "title" in parsed:
                return {
                    "title": parsed["title"],
                    "setting_description": parsed.get("setting_description", ""),
                    "synopsis": parsed.get("synopsis", "A mystery waiting to be solved."),
                    "victim": {
                        "name": parsed.get("victim_name", "Unknown Victim"),
                        "age": parsed.get("victim_age", 40),
                        "occupation": parsed.get("victim_occupation", "Unknown"),
                        "cause_of_death": parsed.get("victim_cause_of_death", "Unknown"),
                        "background": parsed.get("victim_background", ""),
                    },
                }

        # Fallback
        title = self._generate_title()
        victim = self._generate_victim()
        setting = self._generate_setting(params["mood_tags"], params["era"])
        synopses = [
            "Everyone had a motive. No one has an alibi.",
            "The truth died with the victim — or did it?",
            "Three suspects. Three lies. One killer.",
            "A crime hidden in plain sight. Can you see what they missed?",
            "The evidence tells one story. The witnesses tell another.",
        ]
        return {
            "title": title,
            "setting_description": setting,
            "synopsis": random.choice(synopses),
            "victim": victim,
        }

    async def _generate_suspects_step(
        self, concept: dict, params: dict, num_suspects: int
    ) -> list[dict]:
        """Step 2: Generate suspects."""
        if self._llm:
            prompt = STEP2_SUSPECTS_PROMPT.format(
                title=concept["title"],
                synopsis=concept["synopsis"],
                victim_name=concept["victim"]["name"],
                victim_occupation=concept["victim"]["occupation"],
                victim_background=concept["victim"]["background"],
                mood_tags=", ".join(params["mood_tags"]),
                era=params["era"],
                crime_type=params["crime_type"],
                num_suspects=num_suspects,
            )
            raw = await self._call_llm(prompt)
            parsed = self._parse_json(raw)
            if parsed and isinstance(parsed, list) and len(parsed) >= 2:
                # Ensure at least one is guilty
                if not any(s.get("is_guilty") for s in parsed):
                    parsed[0]["is_guilty"] = True
                return parsed

        return self._generate_suspects(concept["victim"], num_suspects, params["crime_type"])

    async def _generate_evidence_step(
        self,
        concept: dict,
        suspects: list[dict],
        params: dict,
        num_evidence: int,
        num_red_herrings: int,
    ) -> list[dict]:
        """Step 3: Generate evidence."""
        if self._llm:
            guilty_name = next(
                (s["name"] for s in suspects if s.get("is_guilty")), "Unknown"
            )
            prompt = STEP3_EVIDENCE_PROMPT.format(
                title=concept["title"],
                suspect_names=", ".join(s["name"] for s in suspects),
                guilty_suspect=guilty_name,
                crime_type=params["crime_type"],
                era=params["era"],
                num_evidence=num_evidence,
                num_red_herrings=num_red_herrings,
            )
            raw = await self._call_llm(prompt)
            parsed = self._parse_json(raw)
            if parsed and isinstance(parsed, list) and len(parsed) >= 3:
                return parsed

        return self._generate_evidence(suspects, num_evidence, num_red_herrings)

    async def _generate_files_step(
        self,
        concept: dict,
        suspects: list[dict],
        params: dict,
        num_files: int,
    ) -> list[dict]:
        """Step 4: Generate case files."""
        if self._llm:
            prompt = STEP4_FILES_PROMPT.format(
                title=concept["title"],
                synopsis=concept["synopsis"],
                era=params["era"],
                setting_description=concept["setting_description"],
                victim_name=concept["victim"]["name"],
                suspect_names=", ".join(s["name"] for s in suspects),
                num_files=num_files,
            )
            raw = await self._call_llm(prompt)
            parsed = self._parse_json(raw)
            if parsed and isinstance(parsed, list) and len(parsed) >= 2:
                return parsed

        case_number = self._generate_case_number(params["era"])
        return self._generate_case_files(
            concept["title"],
            case_number,
            params["era"],
            concept["setting_description"],
            concept["victim"],
            suspects,
            num_files,
        )

    def _store_case(
        self,
        db: Session,
        concept: dict,
        victim_data: dict,
        suspects_data: list[dict],
        evidence_data: list[dict],
        files_data: list[dict],
        params: dict,
    ) -> CaseDB:
        """Validate and persist the generated case to the database."""
        # Generate unique case number
        case_number = self._generate_case_number(params["era"])
        existing = db.query(CaseDB).filter(CaseDB.case_number == case_number).first()
        while existing:
            case_number = self._generate_case_number(params["era"])
            existing = db.query(CaseDB).filter(CaseDB.case_number == case_number).first()

        case = CaseDB(
            title=concept["title"],
            case_number=case_number,
            classification="COLD",
            difficulty=params["difficulty"],
            setting_description=concept["setting_description"],
            era=params["era"],
            mood_tags=params["mood_tags"],
            crime_type=params["crime_type"],
            synopsis=concept["synopsis"],
        )
        db.add(case)
        db.flush()

        # Add victim
        db.add(VictimDB(
            case_id=case.id,
            name=victim_data["name"],
            age=victim_data.get("age", 40),
            occupation=victim_data.get("occupation", "Unknown"),
            cause_of_death=victim_data.get("cause_of_death", "Unknown"),
            background=victim_data.get("background", ""),
        ))

        # Add suspects and build ID map
        suspect_id_map = {}
        for idx, s in enumerate(suspects_data):
            suspect = SuspectDB(
                case_id=case.id,
                name=s["name"],
                age=s.get("age", 40),
                occupation=s.get("occupation", "Unknown"),
                relationship_to_victim=s.get("relationship_to_victim", "Unknown"),
                personality_traits=s.get("personality_traits", []),
                hidden_knowledge=s.get("hidden_knowledge", ""),
                is_guilty=s.get("is_guilty", False),
                alibi=s.get("alibi", "No alibi provided"),
            )
            db.add(suspect)
            db.flush()
            suspect_id_map[idx] = suspect.id

        # Add evidence
        for ev in evidence_data:
            linked_indices = ev.get("linked_suspect_indices", ev.get("linked_suspect_ids", []))
            linked_ids = [
                suspect_id_map[i]
                for i in linked_indices
                if i in suspect_id_map
            ]
            db.add(EvidenceDB(
                case_id=case.id,
                type=ev.get("type", "PHYSICAL"),
                title=ev.get("title", "Unknown Evidence"),
                description=ev.get("description", ""),
                discovered=False,
                linked_suspect_ids=linked_ids,
                is_red_herring=ev.get("is_red_herring", False),
            ))

        # Add case files
        for f in files_data:
            db.add(CaseFileDB(
                case_id=case.id,
                type=f.get("type", "POLICE_NOTES"),
                title=f.get("title", "Untitled Document"),
                content=f.get("content", ""),
                classification_level=f.get("classification_level", "STANDARD"),
            ))

        db.commit()
        db.refresh(case)
        logger.info(f"Generated case: {case.case_number} — {case.title}")
        return case


def run_generation_in_background(
    generation_id: int,
    db_session_factory,
    mood_tags: Optional[list[str]] = None,
    era: Optional[str] = None,
    difficulty: Optional[int] = None,
    crime_type: Optional[str] = None,
):
    """Run case generation in a background thread."""
    import asyncio

    async def _do_generate():
        db = db_session_factory()
        try:
            generator = CaseGenerator()
            case = await generator.generate_case(db, mood_tags, era, difficulty, crime_type)

            # Update generation request
            gen_req = db.query(CaseGenerationRequestDB).filter(
                CaseGenerationRequestDB.id == generation_id
            ).first()
            if gen_req:
                gen_req.status = "COMPLETE"
                gen_req.case_id = case.id
                gen_req.completed_at = datetime.now(timezone.utc)
                db.commit()

            logger.info(f"Background generation {generation_id} complete: {case.title}")
        except Exception as e:
            logger.error(f"Background generation {generation_id} failed: {e}")
            db = db_session_factory()
            gen_req = db.query(CaseGenerationRequestDB).filter(
                CaseGenerationRequestDB.id == generation_id
            ).first()
            if gen_req:
                gen_req.status = "FAILED"
                gen_req.completed_at = datetime.now(timezone.utc)
                db.commit()
        finally:
            db.close()

    def _thread_target():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_do_generate())
        finally:
            loop.close()

    thread = threading.Thread(target=_thread_target, daemon=True)
    thread.start()
    return thread


# Singleton
case_generator = CaseGenerator()
