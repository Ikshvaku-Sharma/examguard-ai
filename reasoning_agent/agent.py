"""
ExamGuard AI — Reasoning Agent
────────────────────────────────
Subscribes to the Redis 'anomalies' channel, maintains a session-level
context window of events, and uses an LLM to compute an Integrity Score
and produce a human-readable reasoning trace.

The agent decides:
  - Updated Integrity Score (0–100)
  - Whether to trigger the Action Agent
  - A plain-English explanation of the verdict
"""

import asyncio
import json
import logging
import os
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Deque, Dict

import redis.asyncio as aioredis

from scorer import IntegrityScorer
from prompts import REASONING_SYSTEM_PROMPT, build_reasoning_prompt

logging.basicConfig(level=logging.INFO, format="%(asctime)s [REASON] %(message)s")
log = logging.getLogger(__name__)

REDIS_URL            = os.getenv("REDIS_URL", "redis://localhost:6379")
INTEGRITY_THRESHOLD  = int(os.getenv("INTEGRITY_THRESHOLD", 50))
CONTEXT_WINDOW       = 20    # last N events kept per session


@dataclass
class ReasoningResult:
    session_id:      str
    timestamp:       str
    integrity_score: int          # 0–100 (100 = fully honest)
    verdict:         str          # CLEAR | SUSPICIOUS | COMPROMISED
    reasoning:       str          # LLM-written explanation
    should_alert:    bool
    triggered_by:    list


class ReasoningAgent:

    def __init__(self):
        self.redis          = None
        self.scorer         = IntegrityScorer()
        self._session_ctx:  Dict[str, Deque] = defaultdict(lambda: deque(maxlen=CONTEXT_WINDOW))
        self._session_scores: Dict[str, int] = defaultdict(lambda: 100)

    async def start(self):
        log.info("Reasoning Agent starting …")
        self.redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
        pubsub     = self.redis.pubsub()
        await pubsub.subscribe("anomalies")
        log.info("Subscribed to Redis channel 'anomalies'")

        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            try:
                event = json.loads(message["data"])
                await self._handle_event(event)
            except Exception as exc:
                log.error("Error processing event: %s", exc)

    async def _handle_event(self, event: dict):
        sid = event["session_id"]
        self._session_ctx[sid].append(event)

        # Rule-based fast score update
        new_score = self.scorer.update(
            current_score=self._session_scores[sid],
            event=event,
        )
        self._session_scores[sid] = new_score

        # LLM deep reasoning (only when score crosses threshold or HIGH severity)
        if new_score <= INTEGRITY_THRESHOLD or event.get("severity") == "HIGH":
            result = await self._llm_reason(sid, new_score)
            await self._publish_result(result)

            if result.should_alert:
                await self.redis.publish("alerts", json.dumps(asdict(result)))
                log.warning("[ALERT] Session %s — Score: %d — %s", sid, new_score, result.verdict)
        else:
            log.info("[OK] Session %s — Score: %d", sid, new_score)

    async def _llm_reason(self, session_id: str, current_score: int) -> ReasoningResult:
        """
        Calls the LLM with the recent event context and asks for a
        structured integrity verdict.
        """
        from langchain_core.output_parsers import JsonOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_openai import ChatOpenAI

        events_summary = list(self._session_ctx[session_id])

        prompt   = ChatPromptTemplate.from_messages([
            ("system", REASONING_SYSTEM_PROMPT),
            ("human",  build_reasoning_prompt(events_summary, current_score)),
        ])

        llm_provider = os.getenv("LLM_PROVIDER", "openai")
        if llm_provider == "groq":
            from langchain_groq import ChatGroq
            llm = ChatGroq(model="llama3-8b-8192", temperature=0)
        else:
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

        parser = JsonOutputParser()
        chain  = prompt | llm | parser

        try:
            raw = await chain.ainvoke({})
            score   = int(raw.get("integrity_score", current_score))
            verdict = raw.get("verdict", "SUSPICIOUS")
            reason  = raw.get("reasoning", "Unable to generate reasoning.")
            events  = raw.get("triggered_by", [])
        except Exception as exc:
            log.error("LLM call failed: %s — using rule-based score", exc)
            score   = current_score
            verdict = "SUSPICIOUS" if current_score < 70 else "CLEAR"
            reason  = f"Rule-based assessment. Integrity score: {current_score}/100."
            events  = [e["event_type"] for e in events_summary[-3:]]

        self._session_scores[session_id] = score

        return ReasoningResult(
            session_id      = session_id,
            timestamp       = datetime.utcnow().isoformat(),
            integrity_score = score,
            verdict         = verdict,
            reasoning       = reason,
            should_alert    = score <= INTEGRITY_THRESHOLD or verdict == "COMPROMISED",
            triggered_by    = events,
        )

    async def _publish_result(self, result: ReasoningResult):
        await self.redis.publish("reasoning_results", json.dumps(asdict(result)))


if __name__ == "__main__":
    agent = ReasoningAgent()
    asyncio.run(agent.start())
