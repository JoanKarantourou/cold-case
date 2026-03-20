"""
Seed data for ColdCase AI — 3 fully written starter cases.
Each case includes suspects, evidence, victims, and case files.
"""

STARTER_CASES = [
    # ================================================================
    # CASE #1977-B — THE LAKE HOUSE
    # ================================================================
    {
        "title": "The Lake House",
        "case_number": "CASE #1977-B",
        "classification": "COLD",
        "difficulty": 3,
        "setting_description": (
            "A sprawling lakeside estate in upstate New York, shrouded in perpetual fog. "
            "The Whitmore family mansion sits on a cliff overlooking Mirror Lake, its windows "
            "dark and watchful. The local town of Ravenford has whispered about the family "
            "for decades. In November 1977, the body of Victor Whitmore was pulled from the "
            "lake, and the case has haunted investigators ever since."
        ),
        "era": "1970s",
        "mood_tags": ["dark", "foggy", "melancholic"],
        "crime_type": "Murder",
        "synopsis": "Three witnesses. Three stories. One body in the lake.",
        "victims": [
            {
                "name": "Victor Whitmore",
                "age": 54,
                "occupation": "Real estate magnate",
                "cause_of_death": "Drowning with blunt force trauma to the back of the skull",
                "background": (
                    "Victor Whitmore built his fortune buying lakefront properties across "
                    "upstate New York in the 1960s. Known for ruthless business tactics, he "
                    "made many enemies. His marriage to Eleanor was strained — rumors of "
                    "affairs on both sides circulated through Ravenford for years. Victor was "
                    "last seen alive at the family's annual autumn gala on November 12, 1977."
                ),
            }
        ],
        "suspects": [
            {
                "name": "Eleanor Whitmore",
                "age": 49,
                "occupation": "Socialite and art collector",
                "relationship_to_victim": "Wife of the victim",
                "personality_traits": ["composed", "calculating", "graceful under pressure"],
                "hidden_knowledge": (
                    "Eleanor discovered Victor's plan to change his will and leave everything "
                    "to his mistress, Margaret Holloway. She confronted him the night of the "
                    "gala on the dock. They argued, but she insists she left him alive. She "
                    "saw James near the boathouse afterward but has never told police."
                ),
                "is_guilty": False,
                "alibi": (
                    "Claims she retired to the library after the gala ended around 11 PM "
                    "and did not leave the house until morning."
                ),
            },
            {
                "name": "James Whitmore",
                "age": 27,
                "occupation": "Graduate student and aspiring writer",
                "relationship_to_victim": "Son of the victim",
                "personality_traits": ["brooding", "resentful", "intelligent", "volatile"],
                "hidden_knowledge": (
                    "James owed gambling debts totaling $40,000. His father refused to bail "
                    "him out and threatened to cut him off entirely. James went to the dock "
                    "at midnight to confront his father one last time. In a rage, he struck "
                    "Victor with an oar. Victor fell into the lake. James panicked and fled. "
                    "He is the killer."
                ),
                "is_guilty": True,
                "alibi": (
                    "Claims he left the gala early, around 10 PM, drove to a bar in town "
                    "called The Rusty Anchor, and returned after 1 AM."
                ),
            },
            {
                "name": "Margaret Holloway",
                "age": 34,
                "occupation": "Local gallery owner",
                "relationship_to_victim": "Victim's mistress",
                "personality_traits": ["charming", "evasive", "ambitious"],
                "hidden_knowledge": (
                    "Margaret was at the estate that night, uninvited. She arrived around "
                    "11:30 PM to meet Victor at the boathouse as planned. She found the dock "
                    "empty with a broken oar on the ground. She took Victor's briefcase from "
                    "the boathouse — it contained the draft of his new will naming her as "
                    "primary beneficiary. She has hidden the briefcase ever since."
                ),
                "is_guilty": False,
                "alibi": (
                    "Claims she was at her gallery in town all evening, preparing for "
                    "an exhibition opening the following week."
                ),
            },
        ],
        "evidence": [
            {
                "type": "PHYSICAL",
                "title": "Broken Wooden Oar",
                "description": (
                    "A splintered wooden oar found on the dock near the boathouse. Blood "
                    "residue on the blade matches Victor Whitmore's blood type (O+). The "
                    "oar belongs to the Whitmore family's rowboat."
                ),
                "discovered": False,
                "linked_suspect_ids": [2],
                "is_red_herring": False,
            },
            {
                "type": "TESTIMONIAL",
                "title": "Bartender's Statement",
                "description": (
                    "Tommy Reeves, bartender at The Rusty Anchor, states James Whitmore "
                    "arrived at the bar around 12:30 AM, not 10 PM as James claims. James "
                    "appeared agitated and ordered three whiskeys in quick succession."
                ),
                "discovered": False,
                "linked_suspect_ids": [2],
                "is_red_herring": False,
            },
            {
                "type": "DOCUMENTARY",
                "title": "Draft Will",
                "description": (
                    "A handwritten draft of a new will found in Victor's study, leaving "
                    "the majority of his estate to 'M. Holloway.' The document is unsigned "
                    "and undated."
                ),
                "discovered": False,
                "linked_suspect_ids": [1, 3],
                "is_red_herring": False,
            },
            {
                "type": "FORENSIC",
                "title": "Autopsy Report Extract",
                "description": (
                    "Cause of death: drowning. A single blunt force wound to the occipital "
                    "region of the skull, consistent with being struck by a flat, heavy "
                    "object. Estimated time of death: between 11 PM and 1 AM."
                ),
                "discovered": False,
                "linked_suspect_ids": [],
                "is_red_herring": False,
            },
            {
                "type": "PHYSICAL",
                "title": "Muddy Footprints",
                "description": (
                    "Two sets of muddy footprints on the dock — one matching men's size 11 "
                    "dress shoes (Victor wore size 11), another matching men's size 9 boots. "
                    "James Whitmore wears size 9."
                ),
                "discovered": False,
                "linked_suspect_ids": [2],
                "is_red_herring": False,
            },
            {
                "type": "PHYSICAL",
                "title": "Monogrammed Cigarette Case",
                "description": (
                    "A silver cigarette case engraved with 'M.H.' found near the boathouse. "
                    "Margaret Holloway's initials. Contains two unsmoked cigarettes of a "
                    "French brand sold only at one shop in Ravenford."
                ),
                "discovered": False,
                "linked_suspect_ids": [3],
                "is_red_herring": False,
            },
            {
                "type": "TESTIMONIAL",
                "title": "Gardener's Account",
                "description": (
                    "Old Pete, the estate gardener, claims he saw a woman's figure near the "
                    "boathouse around midnight. He assumed it was Eleanor. However, Pete is "
                    "known to drink heavily and his eyesight is poor."
                ),
                "discovered": False,
                "linked_suspect_ids": [1, 3],
                "is_red_herring": True,
            },
            {
                "type": "DOCUMENTARY",
                "title": "Life Insurance Policy",
                "description": (
                    "A $2 million life insurance policy on Victor Whitmore, with Eleanor "
                    "as sole beneficiary. Taken out in 1975. This seems suspicious but "
                    "Eleanor had no direct involvement in Victor's death."
                ),
                "discovered": False,
                "linked_suspect_ids": [1],
                "is_red_herring": True,
            },
        ],
        "case_files": [
            {
                "type": "CRIME_SCENE_REPORT",
                "title": "Initial Crime Scene Report — Mirror Lake Dock",
                "classification_level": "STANDARD",
                "content": (
                    "RAVENFORD POLICE DEPARTMENT\n"
                    "CRIME SCENE REPORT — CASE #1977-B\n"
                    "Date: November 13, 1977\n"
                    "Reporting Officer: Det. Harold Crane\n\n"
                    "At approximately 06:45 AM, groundskeeper Peter 'Old Pete' Mulvaney "
                    "discovered the body of Victor Whitmore floating face-down in Mirror "
                    "Lake, approximately 15 feet from the private dock of the Whitmore "
                    "estate.\n\n"
                    "The dock showed signs of a struggle: a wooden railing was cracked, "
                    "and a broken oar was found near the boathouse entrance. Two sets of "
                    "muddy footprints were identified on the dock surface. Water temperature "
                    "was 42°F. The victim was wearing formal evening attire consistent with "
                    "the gala held the previous night.\n\n"
                    "No witnesses to the actual incident have come forward. The estate gates "
                    "were unlocked throughout the night per the gala arrangement. Weather "
                    "conditions: heavy fog, temperature 38°F, light rain after midnight.\n\n"
                    "Items recovered from the scene: 1x broken wooden oar, 1x silver "
                    "cigarette case (monogrammed M.H.), 1x men's leather glove (left hand, "
                    "size L)."
                ),
            },
            {
                "type": "WITNESS_STATEMENT",
                "title": "Statement of Eleanor Whitmore",
                "classification_level": "STANDARD",
                "content": (
                    "RAVENFORD POLICE DEPARTMENT\n"
                    "WITNESS STATEMENT — CASE #1977-B\n"
                    "Date: November 13, 1977\n"
                    "Witness: Eleanor Whitmore\n"
                    "Interviewer: Det. Harold Crane\n\n"
                    "Mrs. Whitmore states that the annual autumn gala concluded at "
                    "approximately 11:00 PM. She last saw her husband Victor on the terrace, "
                    "speaking with several guests. She describes his mood as 'agitated but "
                    "not unusual for him after hosting.'\n\n"
                    "Mrs. Whitmore retired to the library where she read until approximately "
                    "1:00 AM. She did not hear any disturbance. She was not aware of her "
                    "husband's absence until morning when the groundskeeper raised the alarm.\n\n"
                    "When asked about the state of her marriage, Mrs. Whitmore became "
                    "visibly uncomfortable and stated: 'Victor and I had an understanding. "
                    "Our marriage was... practical. But I did not wish him harm.'\n\n"
                    "NOTE: Mrs. Whitmore's hands trembled throughout the interview. She "
                    "requested legal counsel after the question about the draft will."
                ),
            },
            {
                "type": "FORENSIC_ANALYSIS",
                "title": "Forensic Analysis — Broken Oar",
                "classification_level": "CONFIDENTIAL",
                "content": (
                    "RAVENFORD POLICE DEPARTMENT — FORENSICS DIVISION\n"
                    "ANALYSIS REPORT — CASE #1977-B\n"
                    "Date: November 18, 1977\n"
                    "Analyst: Dr. Miriam Foster\n\n"
                    "ITEM: Wooden oar, broken approximately 18 inches from the blade.\n\n"
                    "FINDINGS:\n"
                    "- Blood residue on the flat surface of the blade. Type: O+ (consistent "
                    "with victim Victor Whitmore).\n"
                    "- Splinter pattern indicates a forceful lateral strike, not accidental "
                    "breakage.\n"
                    "- Two partial fingerprints recovered from the handle. One matches Victor "
                    "Whitmore (right thumb). The second is smudged but appears consistent "
                    "with a smaller hand — could not be conclusively matched.\n"
                    "- Hair fibers found embedded in blood residue match victim's hair "
                    "samples.\n\n"
                    "CONCLUSION: The oar was used to strike the victim in the back of the "
                    "head. The force was sufficient to cause disorientation or "
                    "unconsciousness, after which the victim likely fell into the water "
                    "and drowned."
                ),
            },
            {
                "type": "NEWSPAPER_CLIPPING",
                "title": "Ravenford Gazette — November 14, 1977",
                "classification_level": "STANDARD",
                "content": (
                    "RAVENFORD GAZETTE\n"
                    "November 14, 1977\n\n"
                    "PROMINENT BUSINESSMAN FOUND DEAD IN MIRROR LAKE\n\n"
                    "Victor Whitmore, 54, one of the most influential property developers "
                    "in upstate New York, was found dead in Mirror Lake early Sunday morning. "
                    "Police are treating the death as suspicious.\n\n"
                    "Whitmore had hosted his annual autumn gala at the family estate the "
                    "previous evening, attended by over 60 guests. 'Everyone loved Victor,' "
                    "said family friend Richard Dane. 'This is a tremendous shock.'\n\n"
                    "However, not all sentiment in Ravenford is mournful. 'Whitmore drove "
                    "three families off their land to build that resort on Pine Hill,' said "
                    "one local who asked not to be named. 'Some chickens come home to roost.'\n\n"
                    "Police are asking anyone with information to contact the Ravenford "
                    "Police Department."
                ),
            },
            {
                "type": "POLICE_NOTES",
                "title": "Detective Crane's Investigation Notes",
                "classification_level": "CONFIDENTIAL",
                "content": (
                    "DET. HAROLD CRANE — PERSONAL INVESTIGATION NOTES\n"
                    "CASE #1977-B\n\n"
                    "Nov 14: Three persons of interest identified. Eleanor (wife), James "
                    "(son), Margaret Holloway (rumored mistress). All three had motive. All "
                    "three have shaky alibis.\n\n"
                    "Nov 15: James claims he was at The Rusty Anchor from 10 PM. Need to "
                    "verify with bartender. Something about the kid doesn't sit right — too "
                    "calm for someone who just lost his father.\n\n"
                    "Nov 16: Bartender confirms James was there, but says he arrived MUCH "
                    "later than 10 PM. 'Closer to 12:30, maybe later.' James's story has "
                    "a two-and-a-half hour gap.\n\n"
                    "Nov 17: Margaret Holloway interview. She's hiding something. Said she "
                    "was at her gallery all night, but her assistant says the gallery was "
                    "dark by 9 PM. Cigarette case at the scene has her initials.\n\n"
                    "Nov 20: Forensics came back on the oar. It's the murder weapon. Second "
                    "fingerprint couldn't be matched — too smudged. Frustrating.\n\n"
                    "Nov 22: Case stalling. DA wants more before pressing charges. Every "
                    "suspect points at the others. This one might go cold."
                ),
            },
        ],
    },
    # ================================================================
    # CASE #2003-K — DIGITAL GHOST
    # ================================================================
    {
        "title": "Digital Ghost",
        "case_number": "CASE #2003-K",
        "classification": "COLD",
        "difficulty": 4,
        "setting_description": (
            "A minimalist apartment in downtown Seattle, 14th floor of the Meridian Tower. "
            "The walls are bare except for server rack diagrams and sticky notes with "
            "cryptic code snippets. Three monitors on the desk, all wiped clean. The digital "
            "life of Marcus Webb has been erased — but his body remains, slumped in his "
            "ergonomic chair, a half-empty energy drink still cold on the desk."
        ),
        "era": "2000s",
        "mood_tags": ["sterile", "neon", "paranoid"],
        "crime_type": "Murder",
        "synopsis": "A dead programmer. A wiped laptop. And code that someone wanted buried.",
        "victims": [
            {
                "name": "Marcus Webb",
                "age": 31,
                "occupation": "Senior software engineer at Nexion Technologies",
                "cause_of_death": "Potassium chloride injection disguised as insulin overdose",
                "background": (
                    "Marcus Webb was a brilliant but paranoid programmer who worked on "
                    "Nexion Technologies' flagship data analytics platform. Colleagues "
                    "described him as obsessive and secretive. In the weeks before his death, "
                    "Marcus had become increasingly agitated, telling friends he had 'found "
                    "something big' in Nexion's codebase. He was found dead on March 15, "
                    "2003. His laptop, external drives, and cloud accounts had all been "
                    "wiped clean within an hour of his estimated time of death."
                ),
            }
        ],
        "suspects": [
            {
                "name": "Diana Reeves",
                "age": 35,
                "occupation": "VP of Engineering at Nexion Technologies",
                "relationship_to_victim": "Direct supervisor",
                "personality_traits": ["corporate", "controlled", "ruthlessly efficient"],
                "hidden_knowledge": (
                    "Diana knew Marcus had discovered that Nexion's analytics platform was "
                    "secretly harvesting and selling personal health data from hospital "
                    "clients — a massive federal crime. She reported this to CEO Alan Forster, "
                    "who told her to 'handle it.' She hired a contractor to wipe Marcus's "
                    "machines after Alan dealt with Marcus. She did not know Alan planned to "
                    "kill him — she thought they would just discredit him."
                ),
                "is_guilty": False,
                "alibi": (
                    "Claims she was at a late dinner with Nexion's board members at "
                    "Palazzo restaurant until 11 PM, then went directly home."
                ),
            },
            {
                "name": "Alan Forster",
                "age": 42,
                "occupation": "CEO and co-founder of Nexion Technologies",
                "relationship_to_victim": "Company CEO",
                "personality_traits": ["charismatic", "narcissistic", "dangerous when cornered"],
                "hidden_knowledge": (
                    "Alan personally went to Marcus's apartment at 10:30 PM. He brought a "
                    "syringe of potassium chloride obtained through a black-market contact. "
                    "He told Marcus he wanted to 'talk things over' and offered him a drink "
                    "laced with a sedative. Once Marcus was drowsy, Alan injected him. He "
                    "then triggered the remote wipe protocol Diana had prepared. Alan is "
                    "the killer."
                ),
                "is_guilty": True,
                "alibi": (
                    "Claims he was at home all evening. His wife confirms he was home by "
                    "9 PM and did not leave. However, his wife is a co-owner of Nexion "
                    "and has a financial interest in protecting him."
                ),
            },
            {
                "name": "Yuki Tanaka",
                "age": 28,
                "occupation": "Software engineer at Nexion Technologies",
                "relationship_to_victim": "Close colleague and friend",
                "personality_traits": ["anxious", "loyal", "technically brilliant"],
                "hidden_knowledge": (
                    "Yuki was the one who first pointed Marcus toward the suspicious code. "
                    "She and Marcus had been secretly investigating Nexion's data practices "
                    "for two months. After Marcus's death, Yuki received a USB drive in the "
                    "mail — Marcus had set up a dead man's switch to send her a copy of all "
                    "the evidence if he didn't check in for 48 hours. Yuki has the evidence "
                    "but is terrified to come forward."
                ),
                "is_guilty": False,
                "alibi": (
                    "Claims she was at home playing an online game. Her game activity log "
                    "shows continuous play from 8 PM to 2 AM."
                ),
            },
            {
                "name": "Derek Nash",
                "age": 38,
                "occupation": "Private security consultant",
                "relationship_to_victim": "No direct relationship — hired by Nexion",
                "personality_traits": ["cold", "professional", "meticulous"],
                "hidden_knowledge": (
                    "Derek was hired by Diana Reeves to perform 'digital sanitation' — "
                    "wiping Marcus's devices. He executed the remote wipe from a van parked "
                    "outside the Meridian Tower at 11:15 PM. He did not enter the apartment "
                    "and did not know Marcus was dead at the time. He realized afterward "
                    "that he had helped cover up a murder."
                ),
                "is_guilty": False,
                "alibi": (
                    "Claims he was at his office doing paperwork. Security cameras at his "
                    "office building show him leaving at 9:45 PM and not returning until "
                    "12:30 AM."
                ),
            },
        ],
        "evidence": [
            {
                "type": "FORENSIC",
                "title": "Toxicology Report",
                "description": (
                    "Blood analysis reveals elevated potassium levels consistent with "
                    "potassium chloride injection. A small injection mark was found on the "
                    "left inner elbow. Also detected: trace amounts of midazolam (a sedative) "
                    "in the stomach contents."
                ),
                "discovered": False,
                "linked_suspect_ids": [2],
                "is_red_herring": False,
            },
            {
                "type": "FORENSIC",
                "title": "Digital Forensics — Wipe Timestamp",
                "description": (
                    "Analysis of the apartment's router logs shows a large outbound data "
                    "transfer at 11:15 PM, followed by a remote wipe command sent to all "
                    "connected devices. The wipe originated from an IP address traced to "
                    "a mobile hotspot registered to 'Granite Security Solutions.'"
                ),
                "discovered": False,
                "linked_suspect_ids": [4],
                "is_red_herring": False,
            },
            {
                "type": "PHYSICAL",
                "title": "Security Camera Footage — Lobby",
                "description": (
                    "Meridian Tower lobby camera shows a man in a dark coat entering at "
                    "10:28 PM and leaving at 11:05 PM. Face partially obscured by a "
                    "baseball cap. Build and height consistent with Alan Forster (6'1\")."
                ),
                "discovered": False,
                "linked_suspect_ids": [2],
                "is_red_herring": False,
            },
            {
                "type": "DOCUMENTARY",
                "title": "Marcus's Encrypted Email",
                "description": (
                    "A partially recovered encrypted email from Marcus to an unknown "
                    "recipient, dated March 13: 'I have proof. The patient data pipeline "
                    "feeds directly to Meridian Analytics LLC — a shell company. If I "
                    "disappear, check the dead drop.'"
                ),
                "discovered": False,
                "linked_suspect_ids": [],
                "is_red_herring": False,
            },
            {
                "type": "PHYSICAL",
                "title": "Empty Syringe",
                "description": (
                    "An empty medical syringe found in the dumpster behind Meridian Tower. "
                    "Residue tests positive for potassium chloride. No fingerprints — wiped "
                    "clean."
                ),
                "discovered": False,
                "linked_suspect_ids": [2],
                "is_red_herring": False,
            },
            {
                "type": "DOCUMENTARY",
                "title": "Nexion Internal Memo",
                "description": (
                    "An internal memo from Diana Reeves to Alan Forster, dated March 10: "
                    "'Webb is becoming a liability. He's accessed restricted database "
                    "partitions 47 times this month. We need to contain this immediately. "
                    "I recommend termination and NDA enforcement.'"
                ),
                "discovered": False,
                "linked_suspect_ids": [1, 2],
                "is_red_herring": False,
            },
            {
                "type": "TESTIMONIAL",
                "title": "Neighbor's Statement",
                "description": (
                    "Apartment 14C resident Sarah Lin reports hearing Marcus's door open "
                    "and close twice between 10 PM and 11 PM. She heard muffled conversation "
                    "but no arguing. 'It sounded friendly, like he knew the person.'"
                ),
                "discovered": False,
                "linked_suspect_ids": [2],
                "is_red_herring": False,
            },
            {
                "type": "PHYSICAL",
                "title": "Energy Drink with Sedative",
                "description": (
                    "The half-empty energy drink on Marcus's desk tested positive for "
                    "midazolam. Someone added the sedative to the drink — likely while "
                    "Marcus was distracted."
                ),
                "discovered": False,
                "linked_suspect_ids": [2],
                "is_red_herring": False,
            },
            {
                "type": "TESTIMONIAL",
                "title": "Anonymous Tip — Offshore Accounts",
                "description": (
                    "An anonymous caller claimed Marcus was embezzling from Nexion and "
                    "funneling money to offshore accounts. Internal audit found no evidence "
                    "of this. The tip was made from a burner phone. Likely planted to "
                    "discredit Marcus."
                ),
                "discovered": False,
                "linked_suspect_ids": [],
                "is_red_herring": True,
            },
            {
                "type": "PHYSICAL",
                "title": "Gaming Mouse Activity Log",
                "description": (
                    "Yuki Tanaka's gaming mouse shows continuous input from 8 PM to 2 AM "
                    "on the night of the murder. However, sophisticated scripts can simulate "
                    "mouse movements — this alibi is technically spoofable."
                ),
                "discovered": False,
                "linked_suspect_ids": [3],
                "is_red_herring": True,
            },
            {
                "type": "DOCUMENTARY",
                "title": "Granite Security Invoice",
                "description": (
                    "An invoice from Granite Security Solutions to Nexion Technologies for "
                    "'Digital Asset Sanitization Services' dated March 14. Amount: $15,000. "
                    "Approved by D. Reeves."
                ),
                "discovered": False,
                "linked_suspect_ids": [1, 4],
                "is_red_herring": False,
            },
        ],
        "case_files": [
            {
                "type": "CRIME_SCENE_REPORT",
                "title": "Initial Crime Scene Report — Meridian Tower Apt 14B",
                "classification_level": "STANDARD",
                "content": (
                    "SEATTLE POLICE DEPARTMENT\n"
                    "CRIME SCENE REPORT — CASE #2003-K\n"
                    "Date: March 16, 2003\n"
                    "Reporting Officer: Det. Karen Vasquez\n\n"
                    "At 09:15 AM, building management entered apartment 14B of Meridian "
                    "Tower after the tenant, Marcus Webb, failed to respond to maintenance "
                    "requests for 18 hours. The victim was found seated in his desk chair, "
                    "slumped forward.\n\n"
                    "The apartment was undisturbed — no signs of forced entry or struggle. "
                    "Three computer monitors on the desk displayed factory reset screens. "
                    "An external hard drive dock was empty. A half-consumed energy drink "
                    "was on the desk. The victim's phone was missing.\n\n"
                    "Initial assessment suggested natural death (cardiac event), but the "
                    "injection mark on the left arm and the wiped computers raised "
                    "suspicion. Scene was secured for forensic processing.\n\n"
                    "Items recovered: 1x energy drink can, 1x empty syringe (dumpster), "
                    "3x wiped hard drives, 1x sticky note reading 'THEY KNOW.'"
                ),
            },
            {
                "type": "WITNESS_STATEMENT",
                "title": "Statement of Yuki Tanaka",
                "classification_level": "STANDARD",
                "content": (
                    "SEATTLE POLICE DEPARTMENT\n"
                    "WITNESS STATEMENT — CASE #2003-K\n"
                    "Date: March 17, 2003\n"
                    "Witness: Yuki Tanaka\n"
                    "Interviewer: Det. Karen Vasquez\n\n"
                    "Ms. Tanaka states she last spoke with Marcus Webb on March 14 at "
                    "approximately 6:30 PM at the office. He seemed 'more paranoid than "
                    "usual' and told her to 'be careful.' She asked what he meant but he "
                    "shook his head and left.\n\n"
                    "When asked about Marcus's work, Ms. Tanaka said: 'Marcus was brilliant. "
                    "He saw patterns in code that nobody else could. Lately he'd been "
                    "staying late, running queries against production databases. I think "
                    "he found something wrong.'\n\n"
                    "Ms. Tanaka denies knowledge of any wrongdoing at Nexion. She appeared "
                    "genuinely distressed during the interview.\n\n"
                    "NOTE: Ms. Tanaka's alibi checks out via game server logs, though "
                    "digital alibis should be treated with appropriate skepticism."
                ),
            },
            {
                "type": "FORENSIC_ANALYSIS",
                "title": "Forensic Analysis — Digital Devices",
                "classification_level": "CONFIDENTIAL",
                "content": (
                    "SEATTLE PD — CYBER CRIMES UNIT\n"
                    "DIGITAL FORENSICS REPORT — CASE #2003-K\n"
                    "Date: March 22, 2003\n"
                    "Analyst: Sgt. Paul Richter\n\n"
                    "DEVICES EXAMINED:\n"
                    "- 3x desktop hard drives (Seagate Barracuda 120GB)\n"
                    "- 1x external HDD dock (empty)\n"
                    "- Apartment router (Linksys WRT54G)\n\n"
                    "FINDINGS:\n"
                    "All three internal drives were subjected to a DoD-grade 7-pass wipe. "
                    "Recovery is impossible. The wipe was initiated remotely at 23:15:42 on "
                    "March 15 via a script that triggered on network command.\n\n"
                    "Router logs show:\n"
                    "- 22:28 — Front door smart lock opened (code: primary tenant)\n"
                    "- 22:31 — Visitor connected device to WiFi (MAC: 4A:3B:7C:DE:F1:22)\n"
                    "- 23:05 — Visitor device disconnected\n"
                    "- 23:15 — Remote wipe command received from external IP (traced to "
                    "mobile hotspot, Granite Security Solutions account)\n"
                    "- 23:16 — Wipe process began on all connected storage\n\n"
                    "The visitor device MAC address is associated with an iPhone model "
                    "consistent with phones issued to Nexion C-suite executives."
                ),
            },
            {
                "type": "NEWSPAPER_CLIPPING",
                "title": "Seattle Post-Intelligencer — March 18, 2003",
                "classification_level": "STANDARD",
                "content": (
                    "SEATTLE POST-INTELLIGENCER\n"
                    "March 18, 2003\n\n"
                    "TECH WORKER FOUND DEAD IN DOWNTOWN APARTMENT\n\n"
                    "Marcus Webb, 31, a software engineer at Seattle-based Nexion "
                    "Technologies, was found dead in his Meridian Tower apartment on "
                    "Sunday. Police have not confirmed the cause of death but say foul "
                    "play has not been ruled out.\n\n"
                    "Nexion Technologies, which develops data analytics platforms for "
                    "healthcare providers, issued a brief statement: 'We are deeply "
                    "saddened by the loss of our colleague. Marcus was a valued member "
                    "of our team.'\n\n"
                    "Neighbors describe Webb as quiet and reclusive. 'He kept odd hours,' "
                    "said one resident. 'Lights on at 3 AM, typing away. Nice enough when "
                    "you ran into him, but clearly lived in his own world.'"
                ),
            },
            {
                "type": "POLICE_NOTES",
                "title": "Detective Vasquez's Investigation Notes",
                "classification_level": "CONFIDENTIAL",
                "content": (
                    "DET. KAREN VASQUEZ — PERSONAL INVESTIGATION NOTES\n"
                    "CASE #2003-K\n\n"
                    "Mar 16: Initial scene looks clean. Too clean. Someone went to great "
                    "lengths to erase this man's digital life. Why?\n\n"
                    "Mar 17: Interviewed colleagues. Everyone at Nexion is saying the right "
                    "things but something's off. The VP of Engineering, Diana Reeves, was "
                    "overly cooperative. That usually means something.\n\n"
                    "Mar 19: Toxicology came back. Potassium chloride and midazolam. This "
                    "was no accident — this was a professional hit disguised as a medical "
                    "event. Someone drugged him, then injected him.\n\n"
                    "Mar 21: Traced the wipe to Granite Security. Owner is Derek Nash, "
                    "ex-military, runs 'digital security' services. Invoice paid by Nexion. "
                    "Diana Reeves authorized it. But did she know about the murder?\n\n"
                    "Mar 24: Lobby camera footage is grainy but the visitor matches Alan "
                    "Forster's build. His wife alibis him — but she's a co-owner. That "
                    "alibi is worthless.\n\n"
                    "Mar 28: DA says circumstantial. Need the murder weapon or a confession. "
                    "The syringe was wiped clean. This one's slipping away."
                ),
            },
        ],
    },
    # ================================================================
    # CASE #1992-R — THE LAST BROADCAST
    # ================================================================
    {
        "title": "The Last Broadcast",
        "case_number": "CASE #1992-R",
        "classification": "COLD",
        "difficulty": 3,
        "setting_description": (
            "The cramped broadcast booth of WKRV 98.7 FM, a small-town radio station in "
            "Millhaven, Ohio. Wood-paneled walls covered in concert posters and faded "
            "photographs. A single microphone, a mixing board, and racks of vinyl records "
            "and CDs. The ON AIR light is still glowing red. On the night of October 3, "
            "1992, host Danny Callahan vanished during a live broadcast. The recording "
            "captured everything — except an explanation."
        ),
        "era": "1990s",
        "mood_tags": ["eerie", "nostalgic", "small-town"],
        "crime_type": "Disappearance / Suspected Murder",
        "synopsis": "A radio host vanishes mid-show. The recording holds the clues.",
        "victims": [
            {
                "name": "Danny Callahan",
                "age": 37,
                "occupation": "Radio host — 'The Night Owl Show' on WKRV 98.7 FM",
                "cause_of_death": "Unknown — body never recovered. Presumed dead.",
                "background": (
                    "Danny Callahan was Millhaven's favorite voice. His late-night show, "
                    "'The Night Owl,' blended music, local stories, and Danny's dry humor. "
                    "He'd hosted the show for 12 years. Beneath the charm, Danny was dealing "
                    "with a messy divorce, financial trouble, and a secret he'd been sitting "
                    "on for months — he had witnessed the town's mayor accepting a bribe from "
                    "a development company. On October 3, 1992, during a live broadcast, "
                    "Danny stopped mid-sentence. The recording captured a door opening, a "
                    "brief exchange, and then silence. Danny was never seen again."
                ),
            }
        ],
        "suspects": [
            {
                "name": "Mayor Frank Deluca",
                "age": 55,
                "occupation": "Mayor of Millhaven",
                "relationship_to_victim": "Public figure Danny was investigating",
                "personality_traits": ["jovial facade", "deeply corrupt", "intimidating in private"],
                "hidden_knowledge": (
                    "Deluca knew Danny had seen the bribe. He hired Boyd Greer to 'scare' "
                    "Danny into silence. When Boyd reported that Danny was about to go public "
                    "on air, Deluca told Boyd: 'Do whatever you have to do.' He did not "
                    "directly order the killing, but he knew it was likely. Deluca destroyed "
                    "all records of payments to Boyd."
                ),
                "is_guilty": False,
                "alibi": (
                    "Claims he was at home watching the baseball playoffs with his wife. "
                    "His wife confirms this."
                ),
            },
            {
                "name": "Boyd Greer",
                "age": 41,
                "occupation": "Construction foreman for Heartland Development",
                "relationship_to_victim": "No direct relationship — hired enforcer",
                "personality_traits": ["quiet", "physically imposing", "follows orders without question"],
                "hidden_knowledge": (
                    "Boyd went to the radio station at 11:42 PM during Danny's live show. "
                    "He entered through the unlocked back door. He confronted Danny, who "
                    "refused to stay quiet. Boyd struck Danny with a heavy flashlight, "
                    "knocking him unconscious. He carried Danny's body to his truck and "
                    "drove to an abandoned quarry outside town, where he disposed of the "
                    "body. Boyd is the killer."
                ),
                "is_guilty": True,
                "alibi": (
                    "Claims he was at home asleep. Lives alone, so no one can confirm "
                    "or deny this."
                ),
            },
            {
                "name": "Lisa Callahan",
                "age": 34,
                "occupation": "Elementary school teacher",
                "relationship_to_victim": "Estranged wife — divorce pending",
                "personality_traits": ["bitter", "emotional", "protective of her children"],
                "hidden_knowledge": (
                    "Lisa visited Danny at the station earlier that evening, around 8 PM, "
                    "before the show started. They argued about custody arrangements. She "
                    "slapped him and left. She felt guilty about it for years and never told "
                    "police about the visit because she feared it would make her a suspect. "
                    "She had nothing to do with his disappearance."
                ),
                "is_guilty": False,
                "alibi": (
                    "Claims she was at home with her two children all evening. Her neighbor "
                    "confirms seeing her car in the driveway."
                ),
            },
        ],
        "evidence": [
            {
                "type": "PHYSICAL",
                "title": "The Broadcast Recording",
                "description": (
                    "The WKRV broadcast recording from October 3, 1992. At 11:42 PM, Danny "
                    "stops mid-sentence. A door is heard opening. Danny says: 'Hey — you "
                    "can't be in here, we're live—' A deeper voice responds: 'We need to "
                    "talk. Now.' Sound of a chair scraping. Then the microphone picks up a "
                    "dull thud and a grunt. Then silence. Dead air for 14 minutes before the "
                    "automated system kicked in."
                ),
                "discovered": False,
                "linked_suspect_ids": [2],
                "is_red_herring": False,
            },
            {
                "type": "PHYSICAL",
                "title": "Blood Stain on Broadcast Desk",
                "description": (
                    "A small blood stain found on the corner of the broadcast desk, "
                    "consistent with someone's head striking the surface. Blood type matches "
                    "Danny Callahan (A+). The stain was partially cleaned — someone attempted "
                    "to wipe it away."
                ),
                "discovered": False,
                "linked_suspect_ids": [2],
                "is_red_herring": False,
            },
            {
                "type": "TESTIMONIAL",
                "title": "Gas Station Attendant's Statement",
                "description": (
                    "Billy Pratt, night attendant at the Millhaven Texaco, reports seeing "
                    "a dark pickup truck heading north on Route 9 toward the old quarry at "
                    "approximately midnight. He couldn't identify the driver but noted the "
                    "truck had a Heartland Development sticker on the bumper."
                ),
                "discovered": False,
                "linked_suspect_ids": [2],
                "is_red_herring": False,
            },
            {
                "type": "DOCUMENTARY",
                "title": "Danny's Notes — Hidden Envelope",
                "description": (
                    "An envelope found taped under Danny's desk at the station, containing "
                    "handwritten notes: 'Oct 1 — Saw Deluca take envelope from Hartley at "
                    "the Elks Lodge. Cash. Lots of it. Heartland Development deal. Deluca "
                    "is selling the town park for kickbacks. I'm going to talk about it on "
                    "air. If anything happens to me, look at the mayor.'"
                ),
                "discovered": False,
                "linked_suspect_ids": [1],
                "is_red_herring": False,
            },
            {
                "type": "PHYSICAL",
                "title": "Heavy-Duty Flashlight",
                "description": (
                    "A large metal Maglite flashlight found in the station parking lot, "
                    "partially under a dumpster. Traces of blood (type A+) on the barrel. "
                    "No fingerprints — wiped clean."
                ),
                "discovered": False,
                "linked_suspect_ids": [2],
                "is_red_herring": False,
            },
            {
                "type": "TESTIMONIAL",
                "title": "Station Intern's Account",
                "description": (
                    "Tommy Chu, part-time station intern, states Danny was 'really worked "
                    "up' before the show. Danny told him: 'Tonight's going to be different, "
                    "Tommy. I'm going to say what needs to be said.' Tommy left at 10 PM "
                    "and did not witness the incident."
                ),
                "discovered": False,
                "linked_suspect_ids": [],
                "is_red_herring": False,
            },
            {
                "type": "FORENSIC",
                "title": "Voice Analysis of Recording",
                "description": (
                    "Audio forensics analysis of the unidentified voice on the recording. "
                    "The voice is male, estimated age 35-50, with a regional Ohio accent. "
                    "Vocal patterns could not be conclusively matched to any suspect due to "
                    "recording quality limitations."
                ),
                "discovered": False,
                "linked_suspect_ids": [1, 2],
                "is_red_herring": False,
            },
            {
                "type": "DOCUMENTARY",
                "title": "Phone Records — Payphone Call",
                "description": (
                    "Phone records show a call from a payphone outside Millhaven Town Hall "
                    "to the WKRV station at 11:30 PM — 12 minutes before the incident. The "
                    "call lasted 45 seconds. Someone was checking if Danny was live on air."
                ),
                "discovered": False,
                "linked_suspect_ids": [1, 2],
                "is_red_herring": False,
            },
            {
                "type": "TESTIMONIAL",
                "title": "Divorce Lawyer's Statement",
                "description": (
                    "Danny's divorce lawyer, Patricia Webb, states that Danny was under "
                    "significant financial pressure. Lisa was seeking the house and full "
                    "custody. 'Danny was desperate. He told me he might have to leave town.' "
                    "This suggests Danny might have simply fled — but contradicts the "
                    "physical evidence at the scene."
                ),
                "discovered": False,
                "linked_suspect_ids": [3],
                "is_red_herring": True,
            },
            {
                "type": "PHYSICAL",
                "title": "Danny's Car — Found at Station",
                "description": (
                    "Danny's 1988 Honda Civic was found in the station parking lot the next "
                    "morning. Keys in the ignition. If Danny had fled voluntarily, he would "
                    "have taken his car. This suggests he did not leave willingly."
                ),
                "discovered": False,
                "linked_suspect_ids": [],
                "is_red_herring": True,
            },
        ],
        "case_files": [
            {
                "type": "CRIME_SCENE_REPORT",
                "title": "Initial Scene Report — WKRV Radio Station",
                "classification_level": "STANDARD",
                "content": (
                    "MILLHAVEN POLICE DEPARTMENT\n"
                    "MISSING PERSONS / CRIME SCENE REPORT — CASE #1992-R\n"
                    "Date: October 4, 1992\n"
                    "Reporting Officer: Chief Robert Harlan\n\n"
                    "At 08:00 AM, station manager Phil Driscoll arrived at WKRV to find the "
                    "broadcast booth empty and the ON AIR light still illuminated. Danny "
                    "Callahan was not present. The automated system had been running since "
                    "approximately 11:56 PM the previous night.\n\n"
                    "The booth showed minor signs of disturbance: Danny's chair was pushed "
                    "back from the desk at an angle, a coffee mug was knocked over (cold, "
                    "stain dried), and a small blood stain was found on the desk corner. "
                    "The back door of the station was unlocked — it is normally locked after "
                    "10 PM.\n\n"
                    "Danny's car was in the lot. His jacket, wallet, and keys were in the "
                    "booth. His personal notebook was found in a desk drawer. An envelope "
                    "was taped under the desk.\n\n"
                    "Recovered items: 1x heavy flashlight (parking lot), 1x sealed envelope, "
                    "1x broadcast recording tape."
                ),
            },
            {
                "type": "WITNESS_STATEMENT",
                "title": "Statement of Phil Driscoll — Station Manager",
                "classification_level": "STANDARD",
                "content": (
                    "MILLHAVEN POLICE DEPARTMENT\n"
                    "WITNESS STATEMENT — CASE #1992-R\n"
                    "Date: October 4, 1992\n"
                    "Witness: Phil Driscoll\n"
                    "Interviewer: Chief Robert Harlan\n\n"
                    "Mr. Driscoll states he last saw Danny Callahan at approximately 7:30 PM "
                    "on October 3 when he dropped off the next day's programming schedule. "
                    "Danny seemed 'energized but nervous,' which Driscoll attributed to the "
                    "divorce proceedings.\n\n"
                    "'Danny was the heart of this station. Twelve years he did that show. "
                    "Never missed a night, not once. For him to just... stop... something "
                    "bad happened. I know it.'\n\n"
                    "Driscoll confirmed the back door should have been locked. 'I always "
                    "lock it before I leave. Someone either unlocked it from inside or "
                    "had a key. Only four people have keys: me, Danny, Tommy the intern, "
                    "and old Mr. Webb who owns the building.'\n\n"
                    "When played the broadcast recording, Driscoll said: 'That voice... "
                    "I don't recognize it. But it's not someone asking for a song request.'"
                ),
            },
            {
                "type": "POLICE_NOTES",
                "title": "Chief Harlan's Investigation Notes",
                "classification_level": "CONFIDENTIAL",
                "content": (
                    "CHIEF ROBERT HARLAN — INVESTIGATION NOTES\n"
                    "CASE #1992-R\n\n"
                    "Oct 4: Danny's gone. Blood on the desk. Back door unlocked. Recording "
                    "is chilling. This isn't a missing person — this is foul play.\n\n"
                    "Oct 5: Found the envelope under Danny's desk. He was going after "
                    "Deluca. Jesus. Danny, what were you thinking?\n\n"
                    "Oct 6: Interviewed Mayor Deluca. Smooth as always. Says he barely knew "
                    "Danny. 'I listen to the show sometimes. Tragic business.' Alibi is his "
                    "wife — useless.\n\n"
                    "Oct 7: Lisa Callahan interview. She's a wreck. Says Danny was acting "
                    "strange for weeks. Keeps asking if he might have just run away. I don't "
                    "think she believes that either.\n\n"
                    "Oct 10: Gas station kid saw a truck heading to the quarry. Heartland "
                    "Development sticker. Deluca's pet project. Boyd Greer runs their local "
                    "crew. Need to talk to Greer.\n\n"
                    "Oct 12: Greer lawyered up immediately. Won't say a word. That tells me "
                    "plenty.\n\n"
                    "Oct 15: Searched the quarry. Nothing. If Danny's down there, he's under "
                    "100 feet of water. We don't have the equipment or the budget.\n\n"
                    "Oct 20: DA won't move without a body. Deluca's playing golf with the "
                    "county commissioner. This town protects its own. Case is going nowhere."
                ),
            },
            {
                "type": "NEWSPAPER_CLIPPING",
                "title": "Millhaven Courier — October 5, 1992",
                "classification_level": "STANDARD",
                "content": (
                    "THE MILLHAVEN COURIER\n"
                    "October 5, 1992\n\n"
                    "BELOVED RADIO HOST MISSING — FOUL PLAY SUSPECTED\n\n"
                    "Danny Callahan, the voice of WKRV's popular 'Night Owl Show,' has "
                    "been reported missing after failing to finish his broadcast Saturday "
                    "night. Police found signs of a disturbance at the station.\n\n"
                    "'Danny is family to this town,' said longtime listener Martha Bridges. "
                    "'Everyone tuned in to hear him. This doesn't make any sense.'\n\n"
                    "Police Chief Robert Harlan confirmed that the case is being treated as "
                    "a potential abduction. 'We are pursuing all leads and ask anyone with "
                    "information to come forward.'\n\n"
                    "Callahan, 37, was in the midst of divorce proceedings. His estranged "
                    "wife, Lisa, released a statement through her attorney asking for "
                    "privacy and praying for Danny's safe return.\n\n"
                    "The Night Owl Show has been on the air since 1980. WKRV has suspended "
                    "programming in the time slot pending the investigation."
                ),
            },
        ],
    },
]
