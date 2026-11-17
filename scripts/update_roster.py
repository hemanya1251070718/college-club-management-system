import sqlite3

conn = sqlite3.connect('database/clubhub_app.db')
c = conn.cursor()

c.execute("PRAGMA foreign_keys=OFF;")

# Recreate Memberships with Lead in CHECK constraint
c.execute("""
CREATE TABLE Memberships_new (
    membership_id VARCHAR(30) PRIMARY KEY,
    student_id    VARCHAR(20) NOT NULL,
    club_id       VARCHAR(20) NOT NULL,
    role          VARCHAR(30) NOT NULL DEFAULT 'Member',
    join_date     DATE,
    status        VARCHAR(20) DEFAULT 'Active',
    UNIQUE (student_id, club_id),
    FOREIGN KEY (student_id) REFERENCES Students(student_id),
    FOREIGN KEY (club_id) REFERENCES Clubs(club_id),
    CHECK (role IN ('President','Secretary','Treasurer','Event Coordinator','Core Member','Volunteer','Member','Lead'))
);
""")

c.execute("INSERT INTO Memberships_new SELECT * FROM Memberships;")
c.execute("DROP TABLE Memberships;")
c.execute("ALTER TABLE Memberships_new RENAME TO Memberships;")

# Recreate triggers
c.execute("""
CREATE TRIGGER trg_after_membership_insert_sync_count
    AFTER INSERT ON Memberships
    FOR EACH ROW
    WHEN NEW.status = 'Active'
    BEGIN
        UPDATE Clubs
        SET member_count = member_count + 1
        WHERE club_id = NEW.club_id;
    END;
""")

c.execute("""
CREATE TRIGGER trg_after_membership_delete_sync_count
    AFTER DELETE ON Memberships
    FOR EACH ROW
    WHEN OLD.status = 'Active'
    BEGIN
        UPDATE Clubs
        SET member_count = member_count - 1
        WHERE club_id = OLD.club_id;
    END;
""")

c.execute("""
CREATE TRIGGER trg_adjust_member_count_on_status_change
    AFTER UPDATE OF status ON Memberships
    FOR EACH ROW
    BEGIN
        UPDATE Clubs
        SET member_count = member_count + 
            CASE 
                WHEN OLD.status != 'Active' AND NEW.status = 'Active' THEN 1
                WHEN OLD.status = 'Active' AND NEW.status != 'Active' THEN -1
                ELSE 0
            END
        WHERE club_id = NEW.club_id;
    END;
""")

# 1. Update CSA President
c.execute("""
    INSERT OR REPLACE INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
    VALUES ('CSA-0573', 'CE25-0573', 'CSA', 'President', '2026-11-01', 'Active');
""")
c.execute("UPDATE Clubs SET member_count = 1 WHERE club_id = 'CSA';")

# 2. CSI updates
c.execute("UPDATE Memberships SET role = 'Lead' WHERE membership_id = 'CSI-0541';")
c.execute("UPDATE Memberships SET role = 'Lead' WHERE membership_id = 'CSI-0998';")
c.execute("UPDATE Memberships SET role = 'Event Coordinator' WHERE membership_id = 'CSI-0804';")
c.execute("UPDATE Memberships SET role = 'Event Coordinator' WHERE membership_id = 'CSI-1053';")

# 3. SWD updates
c.execute("UPDATE Memberships SET role = 'Lead' WHERE membership_id = 'SWD-0407';")
c.execute("UPDATE Memberships SET role = 'Lead' WHERE membership_id = 'SWD-0898';")
c.execute("UPDATE Memberships SET role = 'Event Coordinator' WHERE membership_id = 'SWD-1059';")
c.execute("UPDATE Memberships SET role = 'Event Coordinator' WHERE membership_id = 'SWD-0757';")

# 4. EDC updates
c.execute("UPDATE Memberships SET role = 'Lead' WHERE membership_id = 'EDC-0315';")
c.execute("UPDATE Memberships SET role = 'Lead' WHERE membership_id = 'EDC-0815';")
c.execute("UPDATE Memberships SET role = 'Event Coordinator' WHERE membership_id = 'EDC-0747';")
c.execute("UPDATE Memberships SET role = 'Event Coordinator' WHERE membership_id = 'EDC-0992';")

# 5. ZEPHYR updates
c.execute("UPDATE Memberships SET role = 'Lead' WHERE membership_id = 'ZEPHYR-0112';")
c.execute("UPDATE Memberships SET role = 'Lead' WHERE membership_id = 'ZEPHYR-0307';")
c.execute("UPDATE Memberships SET role = 'Event Coordinator' WHERE membership_id = 'ZEPHYR-0424';")
c.execute("UPDATE Memberships SET role = 'Event Coordinator' WHERE membership_id = 'ZEPHYR-0541';")

c.execute("PRAGMA foreign_keys=ON;")

conn.commit()
conn.close()
print("Roster updated successfully!")
