import sqlite3

conn = sqlite3.connect("supportpilot.db")
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT * FROM tickets").fetchall()

print("Total tickets stored:", len(rows))
for r in rows:
    print("-" * 50)
    for key in r.keys():
        print(f"{key:16}: {r[key]}")