-- ======================================================================================
-- FILE: hem-trigger.sql
-- AUTHOR: Hemanya Gillurkar (Member 1)
-- PROJECT: College Club Management System (ClubHub DBMS)
-- PURPOSE: Live Demonstration of 2 Completely Different Triggers in MySQL Editor / Workbench
--
-- THE TWO DISTINCT TRIGGERS DEMONSTRATED:
--   TRIGGER 1: trg_after_membership_insert_sync_count (AFTER INSERT - Data Propagation)
--              Automatically increments Clubs.member_count by +1 when a student enrolls.
--   TRIGGER 2: trg_prevent_multiple_presidents (BEFORE INSERT - Integrity Constraint)
--              Enforces College Bylaws: Aborts transaction via SIGNAL SQLSTATE '45000'
--              if anyone attempts to insert a second active President for the same club.
-- ======================================================================================

-- STEP 0: Select the database
USE trial_club;
SET autocommit = 1;


-- ======================================================================================
-- [SECTION A] TRIGGER CREATION (Run this section once before demo)
-- ======================================================================================

-- --------------------------------------------------------------------------------------
-- TRIGGER 1 DEFINITION: DML Data Sync Trigger (AFTER INSERT ON Memberships -> Modifies Clubs)
-- --------------------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_after_membership_insert_sync_count;

DELIMITER $$
CREATE TRIGGER trg_after_membership_insert_sync_count
AFTER INSERT ON Memberships
FOR EACH ROW
BEGIN
    IF NEW.status = 'Active' THEN
        UPDATE Clubs
        SET member_count = member_count + 1
        WHERE club_id = NEW.club_id;
    END IF;
END$$
DELIMITER ;


-- --------------------------------------------------------------------------------------
-- TRIGGER 2 DEFINITION: Business Integrity Rule (BEFORE INSERT ON Memberships -> Aborts with Error)
-- --------------------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_prevent_multiple_presidents;

DELIMITER $$
CREATE TRIGGER trg_prevent_multiple_presidents
BEFORE INSERT ON Memberships
FOR EACH ROW
BEGIN
    DECLARE v_pres_count INT DEFAULT 0;

    IF NEW.role = 'President' AND NEW.status = 'Active' THEN
        SELECT COUNT(*) INTO v_pres_count
        FROM Memberships
        WHERE club_id = NEW.club_id
          AND role = 'President'
          AND status = 'Active';

        IF v_pres_count > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Integrity Violation: A club cannot have more than ONE active President simultaneously.';
        END IF;
    END IF;
END$$
DELIMITER ;




-- ======================================================================================
-- [SECTION B] HOW TO SET UP YOUR 2 TABS IN MYSQL WORKBENCH / EDITOR
-- ======================================================================================
-- 1. In MySQL Workbench, click "File" -> "New Query Tab" (or press Ctrl + T).
--    Name this first tab: [TAB 1: ORIGINAL TABLES].
--    Paste the following two verification queries in TAB 1:
--       SELECT club_id, club_name, member_count FROM Clubs WHERE club_id = 'CSI';
--       SELECT membership_id, student_id, club_id, role, status FROM Memberships WHERE club_id = 'CSI' AND role = 'President';
--
-- 2. Keep this current file open in the second tab: [TAB 2: hem-trigger.sql].
--
-- 3. HOW TO HOP BETWEEN TABS DURING DEMO:
--    - Simply click the tab header at the top, OR
--    - Press [Ctrl + Tab] on Windows to jump back and forth instantly!
--
-- 4. HOW TO RUN SINGLE LINES:
--    - Put your blinking text cursor inside the specific query line.
--    - Press [Ctrl + Enter] (executes ONLY the line where cursor is blinking).
-- ======================================================================================




-- ======================================================================================
-- PART 1: DEMONSTRATING TRIGGER 1 (AUTOMATED BASE TABLE DATA SYNC)
-- Demonstrates: AFTER INSERT trigger automatically modifying the original 'Clubs' table.
-- ======================================================================================

-- --------------------------------------------------------------------------------------
-- STEP 1.1: [HOP TO TAB 1] -> CHECK ORIGINAL CLUBS TABLE BASELINE COUNT
-- Action: Switch to TAB 1 (or place cursor on line 96 below) and press [Ctrl + Enter].
-- What to show: Note current member_count for 'CSI' (e.g., 22).
-- Spoken Cue: "Sir, in our original base table Clubs, CSI currently has 22 members."
-- --------------------------------------------------------------------------------------
SELECT club_id, club_name, member_count FROM Clubs WHERE club_id = 'CSI';


-- --------------------------------------------------------------------------------------
-- STEP 1.2: [HOP TO TAB 2] -> FIRE TRIGGER 1 BY ENROLLING A NEW MEMBER
-- Action: Switch to this tab (TAB 2), place cursor on line 106 below, and press [Ctrl + Enter].
-- What to show: Action Output pane shows a green checkmark: 1 row(s) affected.
-- Spoken Cue: "Now I enroll a new student ME25-0898 into CSI inside Memberships."
-- --------------------------------------------------------------------------------------
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('HEM-DEMO-01', 'ME25-0898', 'CSI', 'Member', CURRENT_DATE, 'Active');


-- --------------------------------------------------------------------------------------
-- STEP 1.3: [HOP TO TAB 1] -> SHOW AUTOMATIC +1 CHANGE IN ORIGINAL CLUBS TABLE!
-- Action: Switch to TAB 1 (or place cursor on line 117 below), press [Ctrl + Enter] (or click Refresh).
-- What to show: member_count has automatically changed from 22 to 23!
-- Spoken Cue: "Look at the original Clubs table! member_count automatically incremented to 23.
--              We never ran an UPDATE on Clubs; Trigger 1 synchronized it in real time!"
-- --------------------------------------------------------------------------------------
SELECT club_id, club_name, member_count FROM Clubs WHERE club_id = 'CSI';


-- --------------------------------------------------------------------------------------
-- STEP 1.4: CLEANUP ROW FROM TRIGGER 1 DEMO
-- Action: Place cursor on line 124 below and press [Ctrl + Enter].
-- --------------------------------------------------------------------------------------
DELETE FROM Memberships WHERE membership_id = 'HEM-DEMO-01';




-- ======================================================================================
-- PART 2: DEMONSTRATING TRIGGER 2 (BUSINESS RULE & INTEGRITY ENFORCEMENT)
-- Demonstrates: BEFORE INSERT trigger rejecting duplicate President via SIGNAL SQLSTATE.
-- ======================================================================================

-- --------------------------------------------------------------------------------------
-- STEP 2.1: [HOP TO TAB 1] -> SHOW EXISTING PRESIDENT IN ORIGINAL MEMBERSHIPS TABLE
-- Action: Switch to TAB 1 (or place cursor on line 138 below) and press [Ctrl + Enter].
-- What to show: 'Hitaishi Bodele' (CE25-0369) is already the active President of CSI.
-- Spoken Cue: "Sir, in our original Memberships table, CSI already has an active President."
-- --------------------------------------------------------------------------------------
SELECT membership_id, student_id, club_id, role, status 
FROM Memberships 
WHERE club_id = 'CSI' AND role = 'President';


-- --------------------------------------------------------------------------------------
-- STEP 2.2: [HOP TO TAB 2] -> ATTEMPT TO INSERT A 2ND PRESIDENT (FAILS WITH ERROR!)
-- Action: Switch to this tab (TAB 2), place cursor on line 150 below, and press [Ctrl + Enter].
-- What to show: Action Output pane shows RED 'X' with exact custom error message:
--   "Error Code: 1644. Integrity Violation: A club cannot have more than ONE active President simultaneously."
-- Spoken Cue: "Now an unauthorized user tries to insert a 2nd President for CSI.
--              Notice the transaction immediately FAILS with our custom SQLSTATE 45000!"
-- --------------------------------------------------------------------------------------
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('HEM-ILLEGAL-PRES', 'ME25-0898', 'CSI', 'President', CURRENT_DATE, 'Active');


-- --------------------------------------------------------------------------------------
-- STEP 2.3: [HOP TO TAB 1] -> SHOW ORIGINAL TABLE WAS NOT CORRUPTED!
-- Action: Switch to TAB 1 (or place cursor on line 161 below) and press [Ctrl + Enter].
-- What to show: There is still ONLY ONE President in CSI. The bad row was rejected!
-- Spoken Cue: "When we re-query the original Memberships table, the illegal row was never added.
--              Trigger 2 prevented database corruption at the storage engine level!"
-- --------------------------------------------------------------------------------------
SELECT membership_id, student_id, club_id, role, status 
FROM Memberships 
WHERE club_id = 'CSI' AND role = 'President';


-- --------------------------------------------------------------------------------------
-- STEP 2.4: PROVE THAT LEGITIMATE ENROLLMENT OF THE SAME STUDENT SUCCEEDS
-- Action: Place cursor on line 171 below and press [Ctrl + Enter].
-- What to show: The same student ME25-0898 can easily be enrolled as an ordinary 'Member'!
-- Spoken Cue: "If we enroll this same student as an ordinary Member, it succeeds instantly."
-- --------------------------------------------------------------------------------------
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('HEM-VALID-02', 'ME25-0898', 'CSI', 'Member', CURRENT_DATE, 'Active');

-- Cleanup demo row:
DELETE FROM Memberships WHERE membership_id = 'HEM-VALID-02';

-- ======================================================================================
-- SUMMARY OF BOTH TRIGGERS TO STATE TO EXAMINER:
-- "Sir, Trigger 1 demonstrates declarative data propagation (incrementing member_count),
--  while Trigger 2 demonstrates defensive constraint enforcement (stopping duplicate presidents).
--  Together, they demonstrate both affirmative automation and defensive data integrity."
-- ======================================================================================
