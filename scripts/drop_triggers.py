import sqlite3

conn = sqlite3.connect("database/clubhub_app.db")
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='trigger'")
triggers = [r[0] for r in cur.fetchall()]
print("Current triggers in DB:", triggers)

for trg in ["trg_adjust_member_count_on_status_change", "trg_auto_progress_event_on_attendance"]:
    cur.execute(f"DROP TRIGGER IF EXISTS {trg}")
    print(f"Dropped {trg}")

conn.commit()
conn.close()
