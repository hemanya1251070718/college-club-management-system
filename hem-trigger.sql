-- ======================================================================================
-- FILE: hem-trigger.sql
-- AUTHOR: Hemanya Gillurkar (Member 1)
-- PROJECT: College Club Management System (ClubHub DBMS)
-- PURPOSE: Live Demonstration of 2 Core Production Triggers in MySQL Editor / Workbench
--
-- THE TWO TRIGGERS:
--   1. trg_after_membership_insert_sync_count (AFTER INSERT ON Memberships)
--   2. trg_after_membership_delete_sync_count (AFTER DELETE ON Memberships)
--
-- TARGET BASE TABLE MODIFIED: Clubs (column: member_count)
-- MONITORED TABLE:           Memberships
-- ======================================================================================

-- STEP 0: Select the database
USE trial_club;
SET autocommit = 1;


-- ======================================================================================
-- [SECTION A] TRIGGER DEFINITIONS (Run these once to ensure triggers are loaded)
-- ======================================================================================

-- --------------------------------------------------------------------------------------
-- TRIGGER 1: Automatically increments Clubs.member_count by +1 when a member joins
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
-- TRIGGER 2: Automatically decrements Clubs.member_count by -1 when a member leaves/deleted
-- --------------------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_after_membership_delete_sync_count;

DELIMITER $$
CREATE TRIGGER trg_after_membership_delete_sync_count
AFTER DELETE ON Memberships
FOR EACH ROW
BEGIN
    IF OLD.status = 'Active' THEN
        UPDATE Clubs
        SET member_count = member_count - 1
        WHERE club_id = OLD.club_id;
    END IF;
END$$
DELIMITER ;



-- ======================================================================================
-- [SECTION B] LIVE DEMO COMMANDS (CURSOR BY CURSOR / LINE BY LINE)
-- Follow the exact step sequence below. Put cursor on each line and press [Ctrl + Enter]
-- ======================================================================================

-- --------------------------------------------------------------------------------------
-- STEP 1: CHECK ORIGINAL TABLE BASELINE BEFORE FIRING TRIGGER 1
-- Place cursor on line 64 below and press [Ctrl + Enter].
-- Note down the current member_count for 'CSI' (e.g. 22). Show this to the examiner.
-- --------------------------------------------------------------------------------------
SELECT club_id, club_name, member_count FROM Clubs WHERE club_id = 'CSI';



-- --------------------------------------------------------------------------------------
-- STEP 2: FIRE TRIGGER 1 (INSERT A NEW ACTIVE MEMBERSHIP)
-- Place cursor on line 74 below and press [Ctrl + Enter].
-- This inserts student 'ME25-0898' into 'CSI'. Trigger 1 fires automatically!
-- --------------------------------------------------------------------------------------
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('HEM-DEMO-01', 'ME25-0898', 'CSI', 'Member', CURRENT_DATE, 'Active');



-- --------------------------------------------------------------------------------------
-- STEP 3: HOP BACK TO ORIGINAL TABLE AND SHOW +1 CHANGE!
-- Place cursor on line 84 below and press [Ctrl + Enter].
-- Look at member_count: It automatically incremented by 1 (e.g. 22 -> 23)!
-- --------------------------------------------------------------------------------------
SELECT club_id, club_name, member_count FROM Clubs WHERE club_id = 'CSI';



-- --------------------------------------------------------------------------------------
-- STEP 4: FIRE TRIGGER 2 (DELETE THE MEMBERSHIP RECORD)
-- Place cursor on line 94 below and press [Ctrl + Enter].
-- This deletes the membership 'HEM-DEMO-01'. Trigger 2 fires automatically!
-- --------------------------------------------------------------------------------------
DELETE FROM Memberships WHERE membership_id = 'HEM-DEMO-01';



-- --------------------------------------------------------------------------------------
-- STEP 5: HOP BACK TO ORIGINAL TABLE AND SHOW -1 REVERSAL!
-- Place cursor on line 104 below and press [Ctrl + Enter].
-- Look at member_count: It automatically decremented back by 1 (e.g. 23 -> 22)!
-- --------------------------------------------------------------------------------------
SELECT club_id, club_name, member_count FROM Clubs WHERE club_id = 'CSI';

-- ======================================================================================
-- END OF DEMONSTRATION: Both triggers proven live. Database returned to original state!
-- ======================================================================================
