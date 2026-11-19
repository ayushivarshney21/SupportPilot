"""Store tickets (SQLite) + Work 2 ingestion into the standard JSON format.
init_db() upgrades an older supportpilot.db automatically - no data is lost."""
import json
import sqlite3
from datetime import datetime
import config

COLUMNS = {"ticket_id": "TEXT PRIMARY KEY", "employee": "TEXT", "email": "TEXT", "title": "TEXT",
           "description": "TEXT", "department": "TEXT", "category": "TEXT", "severity": "TEXT",
           "severity_score": "REAL", "business_impact": "TEXT", "priority": "TEXT", "confidence": "REAL",
           "indicators": "TEXT", "top_categories": "TEXT", "created_at": "TEXT"}


def _conn():
    c = sqlite3.connect(config.DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with _conn() as c:
        cols = ", ".join(f"{k} {v}" for k, v in COLUMNS.items())
        c.execute(f"CREATE TABLE IF NOT EXISTS tickets ({cols})")
        existing = {r["name"] for r in c.execute("PRAGMA table_info(tickets)")}
        for name, typ in COLUMNS.items():           # add columns missing in an old database
            if name not in existing:
                c.execute(f"ALTER TABLE tickets ADD COLUMN {name} {typ.replace(' PRIMARY KEY', '')}")
        # backfill the severity score for tickets saved before this upgrade
        from severity import analyze_severity
        for r in c.execute("SELECT ticket_id, title, description FROM tickets WHERE severity_score IS NULL").fetchall():
            a = analyze_severity(f"{r['title']}. {r['description']}")
            c.execute("UPDATE tickets SET severity_score=?, indicators=? WHERE ticket_id=?",
                      (a["score"], json.dumps(a["indicators"]), r["ticket_id"]))


def next_ticket_id():
    with _conn() as c:
        n = c.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
    return f"T{1001 + n}"


def ingest(employee, email, title, description, department) -> dict:
    """Work 2 - convert the web-form request into the standard ticket JSON."""
    return {"ticket_id": next_ticket_id(), "employee": employee, "email": email,
            "title": title, "description": description, "department": department}


def save_ticket(ticket: dict, result: dict):
    row = {**ticket, **{k: result[k] for k in ("category", "severity", "severity_score", "business_impact",
                                               "priority", "confidence")},
           "indicators": json.dumps(result["indicators"]),
           "top_categories": json.dumps(result["top_categories"]),
           "created_at": datetime.now().isoformat(timespec="seconds")}
    names = list(COLUMNS)
    with _conn() as c:
        c.execute(f"INSERT INTO tickets ({','.join(names)}) VALUES ({','.join('?' * len(names))})",
                  [row[n] for n in names])


def _decode(r):
    d = dict(r)
    d["indicators"] = json.loads(d["indicators"]) if d.get("indicators") else []
    d["top_categories"] = json.loads(d["top_categories"]) if d.get("top_categories") else []
    d["severity_score"] = d.get("severity_score") or 0
    d["created_at"] = (d.get("created_at") or "").replace("T", " ")
    return d


def get_ticket(ticket_id):
    with _conn() as c:
        r = c.execute("SELECT * FROM tickets WHERE ticket_id=?", (ticket_id,)).fetchone()
    return _decode(r) if r else None


def all_tickets():
    """Queue order: most urgent priority first, newest first within a priority."""
    with _conn() as c:
        rows = c.execute("SELECT * FROM tickets ORDER BY priority ASC, created_at DESC").fetchall()
    return [_decode(r) for r in rows]


def stats():
    t = all_tickets()
    return {"total": len(t), **{p: sum(1 for x in t if x["priority"] == p) for p in ("P1", "P2", "P3", "P4")}}
