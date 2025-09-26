# backend/app/recommendation/engine.py
import hashlib
import time
from typing import Dict, List, Any

# Small helpers --------------------------------------------------------------

def _make_id(prefix: str) -> str:
    """Create short deterministic id for a recommendation (useful for reproducibility)."""
    return f"{prefix}_{int(time.time() * 1000)}"

def _clamp(x: float) -> float:
    return max(0.0, min(1.0, float(x)))

# Recommendation logic -------------------------------------------------------

def _extract_flags(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inspect agents and txn to create boolean flags and reason codes.
    Expected context keys:
      - agents: list of {"name","verdict","score", ...}
      - txn: optional transaction dict
    """
    agents = context.get("agents", []) or []
    txn = context.get("txn", {}) or {}

    flags = {
        "fraud_votes": sum(1 for a in agents if a.get("verdict") == "fraud"),
        "agent_count": max(1, len(agents)),
        "unanimous_fraud": all(a.get("verdict") == "fraud" for a in agents) if agents else False,
        "unanimous_legit": all(a.get("verdict") == "legit" for a in agents) if agents else False,
        "max_agent_score": max((a.get("score", 0.0) for a in agents), default=0.0),
        "avg_agent_score": (sum(a.get("score", 0.0) for a in agents) / len(agents)) if agents else 0.0,
        "rule_high_amount": False,
        "rule_device_risk": False,
    }

    # rules from txn if any
    amount = float(txn.get("amount", 0.0)) if txn else float(context.get("amount", 0.0))
    device_risk = float(txn.get("device_risk_score", 0.0)) if txn else float(context.get("device_risk_score", 0.0))

    if amount and amount > 50000:
        flags["rule_high_amount"] = True
    if device_risk and device_risk > 0.8:
        flags["rule_device_risk"] = True

    # produce minimal reason list
    reasons = []
    if flags["rule_high_amount"]:
        reasons.append("high_amount")
    if flags["rule_device_risk"]:
        reasons.append("device_risk")
    flags["rule_reasons"] = reasons

    return flags

def _base_confidence(consensus_score: float, flags: Dict[str, Any]) -> float:
    """
    Compute baseline confidence from consensus/avg score and adjust with flags.
    - consensus_score expected 0..1
    - flags may include unanimous_fraud/legit and rule flags
    """
    conf = float(consensus_score or 0.0)

    # If unanimous fraud, add 10%
    if flags.get("unanimous_fraud"):
        conf += 0.10

    # If unanimous legit, small boost for legit recs
    if flags.get("unanimous_legit"):
        conf += 0.05

    # Rule-based boosts
    if flags.get("rule_high_amount"):
        conf += 0.08
    if flags.get("rule_device_risk"):
        conf += 0.10

    # If only one agent and high score, be slightly cautious
    if flags.get("agent_count", 0) == 1 and flags.get("max_agent_score", 0.0) > 0.9:
        conf -= 0.05

    return _clamp(conf)

# Recommendation templates ---------------------------------------------------

_RECOMM_TEMPLATES = {
    "block": {
        "category": "block",
        "text": "Block the transaction and notify the customer. High probability of fraud.",
        "min_confidence": 0.5
    },
    "hold_review": {
        "category": "manual_review",
        "text": "Hold transaction for manual review by fraud analyst; request additional verification.",
        "min_confidence": 0.25
    },
    "allow_monitor": {
        "category": "monitoring",
        "text": "Allow transaction but increase monitoring for the customer and device.",
        "min_confidence": 0.0
    },
    "require_2fa": {
        "category": "remediation_user",
        "text": "Require step-up authentication (2FA) before completing high-risk transaction.",
        "min_confidence": 0.3
    },
    "advise_user_education": {
        "category": "education",
        "text": "Send user education tips: enable 2FA, avoid unknown devices/merchants.",
        "min_confidence": 0.0
    },
    "escalate_ops": {
        "category": "escalation",
        "text": "Escalate to fraud operations team for investigation; correlated patterns detected.",
        "min_confidence": 0.6
    },
    "analyst_suggest": {
        "category": "analyst_action",
        "text": "Analyst suggestions: check device fingerprint, confirm recent account changes, verify merchant.",
        "min_confidence": 0.0
    },
}

# Public API -----------------------------------------------------------------

def generate_recommendations(verdict: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate an ordered list of recommendations for a transaction.
    Inputs:
      - verdict: "fraud" or "legit"
      - context: { "agents": [...], "txn": {...}, "consensus_score": float (optional) }
    Returns:
      - list of recommendation dicts with fields:
         id, category, text, confidence, reason_codes, meta
    """
    # Normalize inputs
    consensus_score = float(context.get("consensus_score") or 0.0)
    # If not provided, try to derive from agents
    if consensus_score == 0.0 and context.get("agents"):
        consensus_score = float(sum(a.get("score", 0.0) for a in context["agents"]) / len(context["agents"]))

    flags = _extract_flags(context)
    base_conf = _base_confidence(consensus_score, flags)
    txn = context.get("txn", {})

    recs: List[Dict[str, Any]] = []
    reason_codes = list(flags.get("rule_reasons", []))

    # Build a few prioritized rules:
    # 1) High certainty fraud -> block, notify, escalate
    if verdict == "fraud":
        # block recommendation
        c_block = _clamp(base_conf + (0.05 if flags.get("unanimous_fraud") else 0.0))
        if c_block >= _RECOMM_TEMPLATES["block"]["min_confidence"]:
            recs.append({
                "id": _make_id("block"),
                "category": _RECOMM_TEMPLATES["block"]["category"],
                "text": _RECOMM_TEMPLATES["block"]["text"],
                "confidence": c_block,
                "reason_codes": reason_codes + ["consensus_fraud"],
                "meta": {"agents": context.get("agents", []), "txn": txn}
            })

        # require 2FA if medium confidence
        c_2fa = _clamp(base_conf - 0.10 + (0.08 if flags.get("rule_device_risk") else 0.0))
        if c_2fa >= _RECOMM_TEMPLATES["require_2fa"]["min_confidence"]:
            recs.append({
                "id": _make_id("2fa"),
                "category": _RECOMM_TEMPLATES["require_2fa"]["category"],
                "text": _RECOMM_TEMPLATES["require_2fa"]["text"],
                "confidence": c_2fa,
                "reason_codes": reason_codes + (["device_risk"] if flags.get("rule_device_risk") else []),
                "meta": {"agents": context.get("agents", []), "txn": txn}
            })

        # escalation
        c_escalate = _clamp(base_conf + 0.12 if flags.get("rule_high_amount") else base_conf + 0.05)
        if c_escalate >= _RECOMM_TEMPLATES["escalate_ops"]["min_confidence"]:
            recs.append({
                "id": _make_id("escalate"),
                "category": _RECOMM_TEMPLATES["escalate_ops"]["category"],
                "text": _RECOMM_TEMPLATES["escalate_ops"]["text"],
                "confidence": c_escalate,
                "reason_codes": reason_codes + ["escalation_rule"],
                "meta": {"agents": context.get("agents", []), "txn": txn}
            })

        # analyst suggestions (always useful)
        recs.append({
            "id": _make_id("analyst"),
            "category": _RECOMM_TEMPLATES["analyst_suggest"]["category"],
            "text": _RECOMM_TEMPLATES["analyst_suggest"]["text"],
            "confidence": _clamp(base_conf),
            "reason_codes": reason_codes,
            "meta": {"agents": context.get("agents", []), "txn": txn}
        })

    # 2) If legit -> monitoring + user education
    else:  # verdict == "legit"
        c_monitor = _clamp(base_conf * 0.6 + (0.1 if flags.get("rule_high_amount") else 0.0))
        recs.append({
            "id": _make_id("monitor"),
            "category": _RECOMM_TEMPLATES["allow_monitor"]["category"],
            "text": _RECOMM_TEMPLATES["allow_monitor"]["text"],
            "confidence": c_monitor,
            "reason_codes": reason_codes,
            "meta": {"agents": context.get("agents", []), "txn": txn}
        })

        # gentle user education
        recs.append({
            "id": _make_id("edu"),
            "category": _RECOMM_TEMPLATES["advise_user_education"]["category"],
            "text": _RECOMM_TEMPLATES["advise_user_education"]["text"],
            "confidence": _clamp(base_conf * 0.4),
            "reason_codes": reason_codes,
            "meta": {"agents": context.get("agents", []), "txn": txn}
        })

        # analyst suggestions if odd mix of agents
        if flags.get("fraud_votes", 0) >= 1 and flags.get("agent_count", 1) > 1:
            recs.append({
                "id": _make_id("analyst"),
                "category": _RECOMM_TEMPLATES["analyst_suggest"]["category"],
                "text": _RECOMM_TEMPLATES["analyst_suggest"]["text"],
                "confidence": _clamp(base_conf * 0.5 + 0.1),
                "reason_codes": reason_codes + ["mixed_agent_votes"],
                "meta": {"agents": context.get("agents", []), "txn": txn}
            })

    # sort recommendations by confidence desc
    recs = sorted(recs, key=lambda r: r["confidence"], reverse=True)

    return recs
