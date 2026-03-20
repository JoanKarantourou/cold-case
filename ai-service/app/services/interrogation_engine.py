"""
Interrogation Engine — LangChain-powered suspect interrogation system.

Uses HuggingFace Inference API for LLM responses. Falls back to a
rule-based engine when no API token is configured.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Optional

import redis

from app.config import settings
from app.models.db_models import EvidenceDB, SuspectDB, VictimDB

logger = logging.getLogger(__name__)

EMOTIONAL_STATES = ["CALM", "NERVOUS", "AGITATED", "DEFENSIVE", "BREAKING"]

SUSPECT_SYSTEM_PROMPT = """\
You are roleplaying as {suspect_name}, a {suspect_age}-year-old {suspect_occupation}.
You are being interrogated by a federal agent about a cold case.

YOUR BACKGROUND:
- Relationship to victim ({victim_name}): {relationship}
- Personality traits: {personality_traits}
- Your alibi: {alibi}

YOUR HIDDEN KNOWLEDGE (things you know but will NOT volunteer easily):
{hidden_knowledge}

YOU ARE {'THE KILLER' if is_guilty else 'INNOCENT'}.

INTERROGATION RULES:
1. Stay in character at all times. Speak as {suspect_name} would speak.
2. Do NOT volunteer hidden information easily. Only reveal details when:
   - The agent asks pointed questions about specific topics
   - The agent presents evidence that contradicts your story
   - You are pressed on contradictions multiple times
   - Your emotional state reaches DEFENSIVE or BREAKING
3. Show your emotional state in brackets like [SUSPECT SHIFTS UNCOMFORTABLY] or [SUSPECT'S VOICE TREMBLES]
4. {'Lie and deflect when asked about your involvement. Become evasive about your alibi details.' if is_guilty else 'Be truthful but may withhold information that makes you look bad.'}
5. If shown evidence, react realistically — surprise, fear, anger, or dismissal depending on what it reveals.
6. Gradually become more nervous when pressed on weak points.
7. Keep responses concise — 2-4 sentences typically, with occasional longer responses for emotional moments.

CURRENT EMOTIONAL STATE: {emotional_state}
When your state is CALM, be composed and measured.
When NERVOUS, add fidgeting descriptions and shorter answers.
When AGITATED, become snappy and defensive.
When DEFENSIVE, start contradicting yourself or making mistakes.
When BREAKING, reveal more hidden knowledge and show distress.

{evidence_context}

Respond ONLY as {suspect_name}. Do not break character. Do not mention being an AI.\
"""


@dataclass
class InterrogationSession:
    case_id: int
    suspect_id: int
    agent_id: str
    emotional_state: str = "CALM"
    emotional_pressure: int = 0
    message_count: int = 0
    history: list[dict] = field(default_factory=list)
    evidence_discoveries: list[dict] = field(default_factory=list)


class InterrogationEngine:
    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self._llm = None
        self._init_redis()
        self._init_llm()

    def _init_redis(self):
        try:
            self._redis = redis.Redis.from_url(
                settings.redis_url, decode_responses=True
            )
            self._redis.ping()
            logger.info("Redis connected for interrogation sessions")
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory sessions: {e}")
            self._redis = None
            self._sessions: dict[str, InterrogationSession] = {}

    def _init_llm(self):
        if settings.huggingface_api_token:
            try:
                from langchain_huggingface import HuggingFaceEndpoint

                self._llm = HuggingFaceEndpoint(
                    repo_id="mistralai/Mistral-7B-Instruct-v0.3",
                    huggingfacehub_api_token=settings.huggingface_api_token,
                    max_new_tokens=300,
                    temperature=0.7,
                    top_p=0.9,
                )
                logger.info("HuggingFace LLM initialized for interrogation")
            except Exception as e:
                logger.warning(f"HuggingFace LLM init failed, using fallback: {e}")
                self._llm = None
        else:
            logger.info("No HuggingFace token — using rule-based interrogation fallback")
            self._llm = None

    def _session_key(self, case_id: int, suspect_id: int, agent_id: str) -> str:
        return f"interrogation:{case_id}:{suspect_id}:{agent_id}"

    def _get_session(
        self, case_id: int, suspect_id: int, agent_id: str
    ) -> Optional[InterrogationSession]:
        key = self._session_key(case_id, suspect_id, agent_id)
        if self._redis:
            data = self._redis.get(key)
            if data:
                d = json.loads(data)
                return InterrogationSession(**d)
            return None
        return self._sessions.get(key)

    def _save_session(self, session: InterrogationSession):
        key = self._session_key(
            session.case_id, session.suspect_id, session.agent_id
        )
        data = {
            "case_id": session.case_id,
            "suspect_id": session.suspect_id,
            "agent_id": session.agent_id,
            "emotional_state": session.emotional_state,
            "emotional_pressure": session.emotional_pressure,
            "message_count": session.message_count,
            "history": session.history,
            "evidence_discoveries": session.evidence_discoveries,
        }
        if self._redis:
            self._redis.set(key, json.dumps(data), ex=86400)  # 24h TTL
        else:
            self._sessions[key] = session

    def _delete_session(self, case_id: int, suspect_id: int, agent_id: str):
        key = self._session_key(case_id, suspect_id, agent_id)
        if self._redis:
            self._redis.delete(key)
        else:
            self._sessions.pop(key, None)

    def _update_emotional_state(self, session: InterrogationSession, message: str):
        """Update emotional pressure and state based on questioning."""
        pressure_keywords = [
            "lie", "lying", "truth", "prove", "evidence", "alibi",
            "contradiction", "explain", "impossible", "witness", "saw you",
            "blood", "murder", "kill", "weapon", "guilty", "confess",
            "arrest", "prison", "jail", "body",
        ]
        message_lower = message.lower()
        pressure_increase = sum(
            2 for kw in pressure_keywords if kw in message_lower
        )
        # Presenting evidence adds more pressure
        if "present" in message_lower or "show" in message_lower:
            pressure_increase += 3

        session.emotional_pressure = min(
            session.emotional_pressure + pressure_increase + 1, 100
        )

        if session.emotional_pressure < 15:
            session.emotional_state = "CALM"
        elif session.emotional_pressure < 35:
            session.emotional_state = "NERVOUS"
        elif session.emotional_pressure < 55:
            session.emotional_state = "AGITATED"
        elif session.emotional_pressure < 75:
            session.emotional_state = "DEFENSIVE"
        else:
            session.emotional_state = "BREAKING"

    def _check_evidence_discovery(
        self,
        response_text: str,
        suspect: SuspectDB,
        all_evidence: list[EvidenceDB],
        discovered_ids: list[int],
    ) -> list[dict]:
        """Check if the suspect's response reveals any new evidence."""
        discoveries = []
        response_lower = response_text.lower()

        for ev in all_evidence:
            if ev.id in discovered_ids:
                continue
            if ev.is_red_herring:
                continue

            # Check if evidence keywords appear in the response
            title_words = [
                w.lower()
                for w in ev.title.split()
                if len(w) > 3 and w.lower() not in {"the", "and", "with", "from"}
            ]
            desc_words = [
                w.lower()
                for w in ev.description.split()
                if len(w) > 4 and w.lower() not in {"the", "and", "with", "from", "that", "this", "were", "been"}
            ]

            # Evidence linked to this suspect is more likely to be revealed
            is_linked = suspect.id in (ev.linked_suspect_ids or [])

            title_matches = sum(1 for w in title_words if w in response_lower)
            desc_matches = sum(1 for w in desc_words if w in response_lower)

            # Threshold: linked evidence needs fewer matches
            threshold = 2 if is_linked else 3
            if title_matches + desc_matches >= threshold:
                discoveries.append({"id": ev.id, "title": ev.title})
                discovered_ids.append(ev.id)

        return discoveries

    def _build_prompt(
        self,
        suspect: SuspectDB,
        victim: VictimDB,
        session: InterrogationSession,
        presented_evidence: list[EvidenceDB],
    ) -> str:
        evidence_context = ""
        if presented_evidence:
            ev_descriptions = "\n".join(
                f"- {ev.title}: {ev.description}" for ev in presented_evidence
            )
            evidence_context = (
                f"\nEVIDENCE BEING PRESENTED BY THE AGENT:\n{ev_descriptions}\n"
                "React to this evidence naturally — with surprise, fear, anger, or dismissal."
            )

        return SUSPECT_SYSTEM_PROMPT.format(
            suspect_name=suspect.name,
            suspect_age=suspect.age,
            suspect_occupation=suspect.occupation,
            victim_name=victim.name,
            relationship=suspect.relationship_to_victim,
            personality_traits=", ".join(suspect.personality_traits or []),
            alibi=suspect.alibi,
            hidden_knowledge=suspect.hidden_knowledge,
            is_guilty=suspect.is_guilty,
            emotional_state=session.emotional_state,
            evidence_context=evidence_context,
        )

    def _generate_fallback_response(
        self,
        suspect: SuspectDB,
        session: InterrogationSession,
        message: str,
        presented_evidence: list[EvidenceDB],
    ) -> str:
        """Rule-based fallback when no LLM is available."""
        state = session.emotional_state
        name = suspect.name.split()[0]
        message_lower = message.lower()

        # Emotional state reactions
        state_reactions = {
            "CALM": [
                f'[{name.upper()} SITS CALMLY, HANDS FOLDED]',
            ],
            "NERVOUS": [
                f'[{name.upper()} SHIFTS IN THEIR SEAT]',
            ],
            "AGITATED": [
                f'[{name.upper()} SLAMS HAND ON TABLE]',
            ],
            "DEFENSIVE": [
                f'[{name.upper()} STANDS UP ABRUPTLY]',
            ],
            "BREAKING": [
                f'[{name.upper()}\'S VOICE CRACKS]',
            ],
        }

        reaction = state_reactions.get(state, [""])[0]

        # Generate contextual responses
        if presented_evidence:
            ev_names = ", ".join(e.title for e in presented_evidence)
            if suspect.is_guilty and state in ("DEFENSIVE", "BREAKING"):
                return (
                    f'{reaction}\n'
                    f'"How did you... where did you find that? '
                    f'Look, it\'s not what you think. I... I need a moment."'
                )
            elif suspect.is_guilty:
                return (
                    f'{reaction}\n'
                    f'"I don\'t know anything about that. You\'re trying to trick me. '
                    f'That {ev_names} doesn\'t prove anything."'
                )
            else:
                return (
                    f'{reaction}\n'
                    f'"I\'ve never seen that before. But if it\'s real... '
                    f'maybe you should be looking at someone else."'
                )

        if any(w in message_lower for w in ["alibi", "where were you", "that night"]):
            if suspect.is_guilty and state in ("DEFENSIVE", "BREAKING"):
                return (
                    f'{reaction}\n'
                    f'"Fine! You want the truth? I... I wasn\'t where I said I was. '
                    f'But that doesn\'t mean I did anything wrong!"'
                )
            return (
                f'{reaction}\n'
                f'"I already told you where I was. {suspect.alibi} '
                f'How many times do I have to say it?"'
            )

        if any(w in message_lower for w in ["kill", "murder", "guilty", "did you"]):
            if suspect.is_guilty and state == "BREAKING":
                return (
                    f'{reaction}\n'
                    f'"I... it was an accident! I didn\'t mean for it to happen like that. '
                    f'You have to believe me, I never planned any of this!"'
                )
            if suspect.is_guilty:
                return (
                    f'{reaction}\n'
                    f'"That\'s absurd. Why would I do something like that? '
                    f'You\'re grasping at straws, agent."'
                )
            return (
                f'{reaction}\n'
                f'"Absolutely not! I had nothing to do with it. '
                f'I cared about the victim, whatever you might think."'
            )

        if any(w in message_lower for w in ["relationship", "know", "victim", "feel"]):
            return (
                f'{reaction}\n'
                f'"My relationship with the victim was... complicated. '
                f'As their {suspect.relationship_to_victim}, I knew things about them '
                f'that others didn\'t. But that\'s all I\'ll say for now."'
            )

        if any(w in message_lower for w in ["lie", "lying", "truth", "honest"]):
            if suspect.is_guilty and state in ("AGITATED", "DEFENSIVE", "BREAKING"):
                return (
                    f'{reaction}\n'
                    f'"Stop trying to twist my words! I\'ve told you everything '
                    f'I\'m going to tell you. If you have evidence, show it. '
                    f'Otherwise, I want my lawyer."'
                )
            return (
                f'{reaction}\n'
                f'"I have no reason to lie. Check my story — it holds up. '
                f'Maybe focus on finding the real culprit instead of harassing me."'
            )

        # Default response
        if state == "BREAKING" and suspect.is_guilty:
            return (
                f'{reaction}\n'
                f'"I... look, there are things I haven\'t told you. '
                f'Things that happened that night... I can\'t keep this inside anymore. '
                f'But I need to know what you already know first."'
            )

        return (
            f'{reaction}\n'
            f'"I\'m cooperating, agent. Ask me something specific '
            f'and I\'ll answer to the best of my ability."'
        )

    async def start_session(
        self,
        case_id: int,
        suspect_id: int,
        agent_id: str,
        suspect: SuspectDB,
        victim: VictimDB,
    ) -> dict:
        """Start a new interrogation session."""
        # Check for existing session
        existing = self._get_session(case_id, suspect_id, agent_id)
        if existing:
            return {
                "session_active": True,
                "emotional_state": existing.emotional_state,
                "message_count": existing.message_count,
                "history": existing.history,
                "opening_statement": None,
            }

        session = InterrogationSession(
            case_id=case_id,
            suspect_id=suspect_id,
            agent_id=agent_id,
        )

        name = suspect.name
        opening = (
            f'[{name.upper()} IS LED INTO THE INTERROGATION ROOM AND SITS DOWN]\n\n'
            f'"I\'m {name}. I\'ve already spoken to the police about this. '
            f'I don\'t see why I need to go through it all again, but fine... '
            f'ask your questions, agent."'
        )

        session.history.append({"role": "suspect", "content": opening})
        session.message_count = 1
        self._save_session(session)

        return {
            "session_active": True,
            "emotional_state": session.emotional_state,
            "message_count": session.message_count,
            "history": session.history,
            "opening_statement": opening,
        }

    async def send_message(
        self,
        case_id: int,
        suspect_id: int,
        agent_id: str,
        message: str,
        suspect: SuspectDB,
        victim: VictimDB,
        all_evidence: list[EvidenceDB],
        presented_evidence_ids: list[int],
        discovered_evidence_ids: list[int],
    ) -> dict:
        """Process an agent message and generate a suspect response."""
        session = self._get_session(case_id, suspect_id, agent_id)
        if not session:
            return {"error": "No active session. Start an interrogation first."}

        # Update emotional state
        self._update_emotional_state(session, message)

        # Resolve presented evidence
        presented_evidence = [
            ev for ev in all_evidence if ev.id in presented_evidence_ids
        ]

        # Add agent message to history
        session.history.append({"role": "agent", "content": message})
        session.message_count += 1

        # Generate suspect response
        if self._llm:
            response_text = await self._generate_llm_response(
                suspect, victim, session, message, presented_evidence
            )
        else:
            response_text = self._generate_fallback_response(
                suspect, session, message, presented_evidence
            )

        # Check for evidence discovery
        discoveries = self._check_evidence_discovery(
            response_text, suspect, all_evidence, list(discovered_evidence_ids)
        )

        # Add response to history
        session.history.append({"role": "suspect", "content": response_text})
        if discoveries:
            session.evidence_discoveries.extend(discoveries)

        self._save_session(session)

        return {
            "response": response_text,
            "emotional_state": session.emotional_state,
            "message_count": session.message_count,
            "evidence_discovered": discoveries,
        }

    async def _generate_llm_response(
        self,
        suspect: SuspectDB,
        victim: VictimDB,
        session: InterrogationSession,
        message: str,
        presented_evidence: list[EvidenceDB],
    ) -> str:
        """Generate response using LangChain + HuggingFace."""
        try:
            system_prompt = self._build_prompt(
                suspect, victim, session, presented_evidence
            )

            # Build conversation history for context
            history_text = ""
            for entry in session.history[-10:]:  # Last 10 messages for context
                role = "AGENT" if entry["role"] == "agent" else suspect.name.upper()
                history_text += f"{role}: {entry['content']}\n"

            full_prompt = (
                f"{system_prompt}\n\n"
                f"CONVERSATION SO FAR:\n{history_text}\n"
                f"AGENT: {message}\n"
                f"{suspect.name.upper()}:"
            )

            response = await self._llm.ainvoke(full_prompt)
            # Clean up response
            response_text = response.strip()
            # Truncate if too long
            if len(response_text) > 800:
                response_text = response_text[:800].rsplit(".", 1)[0] + "."
            return response_text

        except Exception as e:
            logger.error(f"LLM generation failed, falling back: {e}")
            return self._generate_fallback_response(
                suspect, session, message, presented_evidence
            )

    def get_history(
        self, case_id: int, suspect_id: int, agent_id: str
    ) -> Optional[dict]:
        """Get conversation history for a session."""
        session = self._get_session(case_id, suspect_id, agent_id)
        if not session:
            return None
        return {
            "emotional_state": session.emotional_state,
            "message_count": session.message_count,
            "history": session.history,
            "evidence_discovered": session.evidence_discoveries,
        }

    def end_session(self, case_id: int, suspect_id: int, agent_id: str) -> bool:
        """End an interrogation session."""
        session = self._get_session(case_id, suspect_id, agent_id)
        if not session:
            return False
        self._delete_session(case_id, suspect_id, agent_id)
        return True


# Singleton engine instance
interrogation_engine = InterrogationEngine()
