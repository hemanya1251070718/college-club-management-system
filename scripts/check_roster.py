import sqlite3

conn = sqlite3.connect('database/clubhub_app.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("""
    SELECT m.membership_id, m.student_id, s.name, s.prn_number, s.email, m.club_id, c.club_name, m.role, m.status 
    FROM Memberships m 
    JOIN Students s ON m.student_id = s.student_id 
    JOIN Clubs c ON m.club_id = c.club_id 
    WHERE m.role IN ('President', 'Lead', 'Event Coordinator', 'Secretary') 
    ORDER BY m.club_id, m.role, s.name
""")
rows = cursor.fetchall()
for r in rows:
    print(f"[{r['club_id']}] {r['role']:18} | {r['name']:20} | SID: {r['student_id']} | PRN: {r['prn_number']} | Email: {r['email']}")
print("Total leadership rows:", len(rows))
