"""Work 5 - Severity (score + level) and Work 6 - Priority.
Severity is rule-based: weighted indicator phrases found in the ticket give a
Severity Score (0-100%), which maps to Critical / High / Medium / Low.
Priority = Severity level + Business Impact level (matrix at the bottom)."""
import re

CRITICAL_INDICATORS = ["outage", "down for everyone", "all users", "production", "data loss", "ransomware",
                       "security breach", "hacked", "server down", "system down", "cannot work",
                       "unable to work", "entire team"]
HIGH_INDICATORS = ["urgent", "not working", "not connecting", "cannot connect", "unable", "failed", "crash",
                   "blocked", "cannot login", "locked", "blue screen", "important", "deadline", "immediately"]
MEDIUM_INDICATORS = ["slow", "intermittent", "disconnect", "error", "issue", "problem", "flicker", "freeze",
                     "freezes"]

HIGH_IMPACT = ["client", "customer", "meeting", "presentation", "production", "revenue", "deadline",
               "all users", "entire team", "demo", "board", "audit", "today"]
MEDIUM_IMPACT = ["team", "project", "manager", "tomorrow", "this week", "department"]

# Score bands: Critical >= 80, High 50-79, Medium 30-49, Low < 30
TIER_BASE = {"Critical": 80, "High": 50, "Medium": 30, "Low": 10}
TIER_MAX = {"Critical": 100, "High": 79, "Medium": 49, "Low": 10}
EXTRA_HIT_POINTS = 5     # each additional indicator adds 5 points (max 3 extra)


def _found(text, words):
    t = text.lower()
    return [w for w in words if re.search(r"\b" + re.escape(w) + r"\b", t)]


def analyze_severity(ticket: str) -> dict:
    crit, high, med = (_found(ticket, CRITICAL_INDICATORS), _found(ticket, HIGH_INDICATORS),
                       _found(ticket, MEDIUM_INDICATORS))
    level = "Critical" if crit else "High" if high else "Medium" if med else "Low"
    indicators = crit + high + med
    extra = max(len(indicators) - 1, 0)
    score = TIER_BASE[level] + min(extra, 3) * EXTRA_HIT_POINTS if indicators else TIER_BASE["Low"]
    return {"level": level, "score": min(score, TIER_MAX[level]), "indicators": indicators}


def analyze_impact(ticket: str) -> dict:
    high, med = _found(ticket, HIGH_IMPACT), _found(ticket, MEDIUM_IMPACT)
    level = "High" if high else "Medium" if med else "Low"
    return {"level": level, "indicators": high + med}


def predict_severity(ticket: str) -> str:
    return analyze_severity(ticket)["level"]


def predict_business_impact(ticket: str) -> str:
    return analyze_impact(ticket)["level"]


def calculate_priority(severity: str, impact: str) -> str:
    if severity == "Critical":
        return "P1"
    if severity == "High":
        return "P1" if impact == "High" else "P2"
    if severity == "Medium":
        return "P2" if impact == "High" else "P3"
    return "P3" if impact == "High" else "P4"
