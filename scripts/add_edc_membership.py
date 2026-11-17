import sqlite3

conn = sqlite3.connect('database/clubhub_app.db')
c = conn.cursor()
c.execute("""
    INSERT OR REPLACE INTO Memberships (membership_id, student_id, club_id, role, join_date, status) 
    VALUES ('MEM-EDC-CE250718', 'CE25-0718', 'EDC', 'Core Member', '2026-11-10', 'Active');
""")
c.execute("UPDATE Clubs SET member_count = (SELECT COUNT(*) FROM Memberships WHERE club_id = 'EDC' AND status = 'Active') WHERE club_id = 'EDC';")
conn.commit()

c.execute("SELECT * FROM Memberships WHERE student_id = 'CE25-0718'")
print("Hemanya rows:", c.fetchall())
c.execute("SELECT COUNT(*) FROM Memberships")
print("Total memberships count:", c.fetchone()[0])
conn.close()
