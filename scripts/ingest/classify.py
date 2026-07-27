#!/usr/bin/env python3
"""Conversation classifier v2 — topic and mode as separate axes.

Why v2: v1 collapsed everything into one label and 80% of a journal corpus came
back "technical". Two flaws:
  1. Topic and mode were conflated. "FAITHH architecture updates" is technical in
     TOPIC but can be journal in MODE. Forcing one label destroys the distinction
     the day-by-day timeline actually needs.
  2. Raw hit counts favoured long conversations, and broad technical patterns
     (api, git, config, ```) match incidentally in almost anything.

v2 fixes both:
  * TOPIC  — single best label, what the conversation is about.
  * MODE   — multi-label, how it is written. This is the axis journals live on.
  * Scores are DENSITY (hits per 1k chars), so length stops deciding outcomes.
  * Structural features (who writes more, message rhythm, code presence) carry
    real weight — a journal has the human writing long passages, a troubleshooting
    session has short human turns and long assistant ones.
  * Below MIN_DENSITY nothing is asserted; it returns empty rather than guessing.

Deterministic and inspectable on purpose — no model call, and every result
carries the evidence that produced it.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

MIN_DENSITY = 0.15   # hits per 1k chars required before a mode is asserted
MIN_HITS = 2         # ...and this many raw hits, so one stray phrase cannot decide
DENOM_FLOOR = 3.0    # treat anything under 3k chars as 3k: short chats were scoring
                     # 1 hit / 0.5k = 2.0 density and dominating everything
TOPIC_MIN = 0.10

TOPIC_SIGNALS: Dict[str, List[str]] = {
    "infrastructure": [
        r"\bdocker\b", r"\bproxmox\b", r"\bcontainer\b", r"\bserver\b", r"\bnas\b",
        r"\bnetwork\b", r"\bssh\b", r"\btailscale\b", r"\bvm\b", r"\bgpu\b",
        r"\bpassthrough\b", r"\bbios\b", r"\bdriver\b", r"\bplex\b",
    ],
    "software": [
        r"\bpython\b", r"\bfunction\b", r"\bapi\b", r"\bgit\b", r"\bcommit\b",
        r"\brepo\b", r"\bdebug", r"\btraceback\b", r"\bexception\b", r"```",
        r"\brefactor", r"\bendpoint\b",
    ],
    "research": [
        r"\bconstella\b", r"\bgovernance\b", r"\balife\b", r"\battestation\b",
        r"\bconfirmab", r"\bcivic\b", r"\bexperiment\b", r"\bhypothes", r"\bcorpus\b",
        r"\bframework\b", r"\bdoctrine\b",
    ],
    "business": [
        r"\btom ?cat\b", r"\bllc\b", r"\btax\b", r"\binvoice\b", r"\bclient\b",
        r"\bcontract\b", r"\brevenue\b", r"\bpricing\b", r"\bcpa\b", r"\bmember\b",
    ],
    "audio": [
        r"\bmix(?:ing|down)?\b", r"\bmaster(?:ing)?\b", r"\bdaw\b", r"\bplugin\b",
        r"\baudio\b", r"\bstudio\b", r"\btrack\b", r"\bwavelab\b", r"\bluna\b",
    ],
    # Kept deliberately specific. Generic verbs like move/buy/car match "move the
    # file" and "buy a license" constantly and stole infrastructure conversations.
    "personal": [
        r"\bdoctor\b", r"\bdentist\b", r"\bprescription\b", r"\binsurance\b",
        r"\bapartment\b", r"\blandlord\b", r"\brent\b", r"\bgroceries\b",
        r"\bmy (?:wife|partner|mom|dad|brother|sister|family)\b",
        r"\b4runner\b", r"\bvehicle\b", r"\bmy car\b", r"\bmy truck\b",
    ],
}

MODE_SIGNALS: Dict[str, List[str]] = {
    "journal": [
        r"\bi feel\b", r"\bi'm feeling\b", r"\bi've been\b", r"\bi realized\b",
        r"\bi noticed\b", r"\blooking back\b", r"\bi keep\b", r"\bi tend to\b",
        r"\bhonestly\b", r"\bi'm trying to\b", r"\bmy goal\b", r"\bi struggle\b",
        r"\bfrustrat", r"\bi'm worried\b", r"\bi want to be\b", r"\bfor me\b",
    ],
    "speculative": [
        r"\bwhat if\b", r"\bsuppose\b", r"\bhypothetical", r"\bin theory\b",
        r"\bcould we\b", r"\bwould it be possible\b", r"\bthought experiment\b",
        r"\bimagine (?:if|a|that)\b", r"\bconjecture\b", r"\bunproven\b",
        r"\bspeculat", r"\bdown the road\b", r"\beventually (?:we|i)\b",
    ],
    "idea": [
        r"\bproposal\b", r"\bi want to build\b", r"\bwe should build\b", r"\bdesign for\b",
        r"\bconcept\b", r"\bbrainstorm", r"\bwhat should (?:we|i)\b", r"\bplan(?:ning)? to\b",
        r"\broadmap\b", r"\bblueprint\b", r"\bapproach (?:would|could)\b",
    ],
    # Bare \berror\b was catastrophic: "margin of error" / "prediction error" gave a
    # zebra-stripe biology chat 126 hits and ranked it top runbook candidate. Every
    # pattern here must imply someone is actually stuck on something.
    "troubleshooting": [
        r"\b(?:an?|the|this|getting an?|got an?) error\b", r"error:", r"\berrors?\s+(?:when|while|on)\b",
        r"\bnot working\b", r"\bdoesn'?t work\b", r"\bwon'?t (?:start|boot|run|connect|load|build)\b",
        r"\bfailed to\b", r"\bunable to\b", r"\bcan'?t (?:get|connect|run|access|find)\b",
        r"\bbroken\b", r"\bstuck (?:on|at|with)\b", r"\bcrash(?:ed|ing|es)?\b",
        r"\btraceback\b", r"\bstack trace\b", r"\bexit code\b", r"\bpermission denied\b",
        r"\bconnection refused\b", r"\btimed? ?out\b", r"\bwhy (?:does|is|isn'?t|won'?t|can'?t)\b",
        r"\bhow do i fix\b", r"\btroubleshoot",
    ],
    "reference": [
        r"\bwhat is\b", r"\bhow do i\b", r"\bhow does\b", r"\bcan you explain\b",
        r"\bwhich (?:one|is better)\b", r"\bdifference between\b", r"\brecommend",
        r"\bbest (?:way|option|practice)\b",
    ],
    "decision": [
        r"\bshould i\b", r"\bdecided?\b", r"\bpros and cons\b", r"\btrade-?off",
        r"\bversus\b", r"\bvs\.?\b", r"\bgo with\b", r"\bchoose\b", r"\bworth it\b",
    ],
}

TOPIC_RE = {k: [re.compile(p, re.I) for p in v] for k, v in TOPIC_SIGNALS.items()}
MODE_RE = {k: [re.compile(p, re.I) for p in v] for k, v in MODE_SIGNALS.items()}
CODE_FENCE = re.compile(r"```")
QUESTION = re.compile(r"\?")


@dataclass
class Structure:
    """Shape of the exchange — often more telling than vocabulary."""
    human_chars: int = 0
    assistant_chars: int = 0
    messages: int = 0
    code_blocks: int = 0
    questions: int = 0

    @property
    def human_ratio(self) -> float:
        total = self.human_chars + self.assistant_chars
        return self.human_chars / total if total else 0.0

    @property
    def avg_human_msg(self) -> float:
        turns = max(self.messages / 2, 1)
        return self.human_chars / turns


@dataclass
class Result:
    topic: str
    modes: List[str]
    topic_scores: Dict[str, float] = field(default_factory=dict)
    mode_scores: Dict[str, float] = field(default_factory=dict)
    structure: Dict[str, float] = field(default_factory=dict)
    evidence: List[str] = field(default_factory=list)

    @property
    def primary_mode(self) -> str:
        return self.modes[0] if self.modes else "unclassified"


def _density(patterns, text: str, per: int) -> Tuple[float, int]:
    hits = sum(len(p.findall(text)) for p in patterns)
    return (hits / per if per else 0.0), hits


def classify(title: str, messages: List[dict]) -> Result:
    """messages: [{sender, text}] in order. Title is weighted but never decisive."""
    st = Structure(messages=len(messages))
    human_parts, all_parts = [], []
    for m in messages:
        text = m.get("text") or ""
        sender = (m.get("sender") or "").lower()
        all_parts.append(text)
        if sender in ("human", "user"):
            st.human_chars += len(text)
            human_parts.append(text)
        else:
            st.assistant_chars += len(text)
        st.code_blocks += len(CODE_FENCE.findall(text))
    full = "\n".join(all_parts)
    human_text = "\n".join(human_parts)
    st.questions = len(QUESTION.findall(human_text))

    per_human = max(len(human_text) / 1000, DENOM_FLOOR)

    # Topic reads what the HUMAN asked about, not the whole exchange. Reading the
    # assistant's prose made everything "software": Claude's replies are full of
    # api/function/config and fenced code even when the subject is a hole punch.
    topic_scores = {}
    for label, pats in TOPIC_RE.items():
        d, _ = _density(pats, human_text, per_human)
        topic_scores[label] = round(d, 3)
    for label in topic_scores:
        if re.search(rf"\b{re.escape(label[:6])}", title or "", re.I):
            topic_scores[label] = round(topic_scores[label] + 0.15, 3)

    best_topic, best_val = max(topic_scores.items(), key=lambda kv: kv[1])
    topic = best_topic if best_val >= TOPIC_MIN else "general"

    # Mode reads ONLY what the human wrote — how *they* engaged, not how the
    # assistant replied. This is what v1 got wrong: assistant prose swamped it.
    mode_scores, mode_hits, evidence = {}, {}, []
    for label, pats in MODE_RE.items():
        d, hits = _density(pats, human_text, per_human)
        mode_scores[label] = round(d, 3)
        mode_hits[label] = hits
        if hits:
            sample = next((p.pattern for p in pats if p.search(human_text)), "")
            evidence.append(f"{label}:{hits}x:{sample[:22]}")

    # Structural adjustments — the shape of the conversation, not its words.
    if st.human_ratio > 0.42 and st.avg_human_msg > 700:
        mode_hits["journal"] = mode_hits.get("journal", 0) + MIN_HITS
        mode_scores["journal"] = round(mode_scores.get("journal", 0) + 0.35, 3)
        evidence.append("struct:long-human-turns")
    if st.human_ratio < 0.18 and st.messages > 6:
        mode_hits["troubleshooting"] = mode_hits.get("troubleshooting", 0) + MIN_HITS
        mode_scores["troubleshooting"] = round(mode_scores.get("troubleshooting", 0) + 0.20, 3)
        evidence.append("struct:short-human-turns")
    if st.messages <= 2:
        mode_scores["reference"] = round(mode_scores.get("reference", 0) + 0.25, 3)
        mode_hits["reference"] = mode_hits.get("reference", 0) + MIN_HITS
        evidence.append("struct:single-exchange")

    # Require BOTH density and a real hit count. Structural boosts carry their own
    # synthetic hits so they can still assert on their own.
    modes = [
        m
        for m, v in sorted(mode_scores.items(), key=lambda kv: -kv[1])
        if v >= MIN_DENSITY and mode_hits.get(m, 0) >= MIN_HITS
    ]

    return Result(
        topic=topic,
        modes=modes,
        topic_scores=topic_scores,
        mode_scores=mode_scores,
        structure={
            "human_ratio": round(st.human_ratio, 2),
            "avg_human_msg": round(st.avg_human_msg),
            "messages": st.messages,
            "code_blocks": st.code_blocks,
        },
        evidence=evidence[:6],
    )
