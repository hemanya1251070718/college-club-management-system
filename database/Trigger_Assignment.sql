-- ======================================================================================
-- TRIGGER ASSIGNMENT - 8 NON-IDENTICAL TRIGGERS (STEP-BY-STEP DEMO)
-- Database: trial_club (College Club Management System)
-- Course: Database Management Systems (DBMS Mini Project Evaluation)
--
-- DISTRIBUTION FOR GROUP OF 4 MEMBERS (2 Unique Triggers per Member):
--   Member 1: Trigger 1 (Auto-Increment Member Count) & Trigger 2 (Auto-Decrement Member Count)
--   Member 2: Trigger 3 (Enforce Single President Rule) & Trigger 4 (Sync Count on Status Change)
--   Member 3: Trigger 5 (Block Registration on Completed Event) & Trigger 6 (Verify Attendance Before Feedback)
--   Member 4: Trigger 7 (Auto-Progress Event Status to Ongoing) & Trigger 8 (Auto-Provision Club Profile)
--
-- IMPORTANT EVALUATION RULES HONORED:
-- 1. All triggers operate EXCLUSIVELY on the 8 canonical domain tables:
--    Students, FacultyCoordinators, Clubs, ClubProfile, Memberships,
--    Events, EventRegistrations, Feedback.
-- 2. NO extra log/audit/history tables are created. The database schema strictly retains only 8 tables.
-- 3. Each trigger changes or enforces rules in the real base tables directly.
-- 4. Execute one banner at a time (Ctrl+Shift+Enter in MySQL Workbench / Editor).
-- ======================================================================================

USE trial_club;
SET autocommit = 1;


-- ######################################################################################
-- # MEMBER 1 - TRIGGERS 1 & 2
-- # Automated Club Size Synchronization on Membership Joins & Departures
-- ######################################################################################

-- ======================================================================================
-- TRIGGER 1: trg_after_membership_insert_sync_count
-- WHO USES IT: Student Affairs Office & Club Administration.
-- PURPOSE: When a student joins a club with status 'Active', the stored Clubs.member_count
--          must automatically increment by 1 in real time, preventing manual recount queries.
-- TABLE MONITORED: Memberships (AFTER INSERT)
-- TABLE MODIFIED:  Clubs (Updates member_count directly)
-- COMPLEXITY: O(1) single-row indexed primary key update on Clubs.
-- ======================================================================================

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


-- ----- STEP 1A: CHECK BASE TABLE BEFORE TRIGGER -----
-- Note the current member_count for club 'CSI'
SELECT club_id, club_name, member_count 
FROM Clubs 
WHERE club_id = 'CSI';

-- ----- STEP 1B: FIRE TRIGGER (INSERT A NEW MEMBERSHIP) -----
-- Student 'ME25-0898' joins 'CSI' as an Active Member
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('TRG1-DEMO-01', 'ME25-0898', 'CSI', 'Member', CURRENT_DATE, 'Active');

-- ----- STEP 1C: VERIFY CHANGE IN THE BASE CLUBS TABLE -----
-- The member_count for 'CSI' has automatically increased by 1!
SELECT club_id, club_name, member_count 
FROM Clubs 
WHERE club_id = 'CSI';

-- ----- STEP 1D: CLEANUP (RESTORE ORIGINAL STATE) -----
-- Deleting this demo row will be used to demonstrate Trigger 2 below, or clean up here:
DELETE FROM Memberships WHERE membership_id = 'TRG1-DEMO-01';



-- ======================================================================================
-- TRIGGER 2: trg_after_membership_delete_sync_count
-- WHO USES IT: Club Coordinator & System Auditor.
-- PURPOSE: When an active member leaves or is removed from a club, Clubs.member_count
--          must decrement by 1 automatically in the Clubs table.
-- TABLE MONITORED: Memberships (AFTER DELETE)
-- TABLE MODIFIED:  Clubs (Updates member_count directly)
-- COMPLEXITY: O(1) single-row indexed primary key update on Clubs.
-- ======================================================================================

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


-- ----- STEP 2A: CHECK BASE TABLE BEFORE TRIGGER -----
-- First add a temporary demo row so we can observe the decrement without disturbing base members
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('TRG2-DEMO-02', 'CE25-1062', 'SWD', 'Member', CURRENT_DATE, 'Active');

-- Check member_count for 'SWD' in Clubs
SELECT club_id, club_name, member_count 
FROM Clubs 
WHERE club_id = 'SWD';

-- ----- STEP 2B: FIRE TRIGGER (DELETE MEMBERSHIP) -----
-- Member departs from 'SWD'
DELETE FROM Memberships 
WHERE membership_id = 'TRG2-DEMO-02';

-- ----- STEP 2C: VERIFY CHANGE IN THE BASE CLUBS TABLE -----
-- SWD member_count has automatically decremented by 1 back to original!
SELECT club_id, club_name, member_count 
FROM Clubs 
WHERE club_id = 'SWD';



-- ######################################################################################
-- # MEMBER 2 - TRIGGERS 3 & 4
-- # Governance Integrity & Dynamic Membership State Adjustments
-- ######################################################################################

-- ======================================================================================
-- TRIGGER 3: trg_prevent_multiple_presidents
-- WHO USES IT: Student Council Election Commission & Faculty Advisors.
-- PURPOSE: VIT Pune Club Bylaws Rule: A club cannot have more than ONE active President
--          at any time. This trigger intercepts any INSERT into Memberships that attempts
--          to add a second President and aborts the transaction with a custom SQL error.
-- TABLE MONITORED: Memberships (BEFORE INSERT)
-- TABLE MODIFIED:  Enforces declarative constraint on Memberships via SIGNAL SQLSTATE.
-- COMPLEXITY: O(1) index-assisted count on (club_id, role, status).
-- ======================================================================================

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


-- ----- STEP 3A: CHECK CURRENT ACTIVE PRESIDENT IN CSI -----
-- Notice CE25-0369 is already the active President of CSI
SELECT membership_id, student_id, club_id, role, status 
FROM Memberships 
WHERE club_id = 'CSI' AND role = 'President';

-- ----- STEP 3B: FIRE TRIGGER (ATTEMPT TO INSERT A 2ND PRESIDENT) -----
-- Expected Result: FAILS with MySQL Error: "Integrity Violation: A club cannot have more than ONE active President simultaneously."
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('TRG3-FAIL-01', 'ME25-0898', 'CSI', 'President', CURRENT_DATE, 'Active');

-- ----- STEP 3C: VERIFY LEGITIMATE ROLE INSERTION SUCCEEDS -----
-- Inserting the same student as an ordinary 'Member' works completely fine:
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('TRG3-PASS-01', 'ME25-0898', 'CSI', 'Member', CURRENT_DATE, 'Active');

-- Clean up the passed demo row:
DELETE FROM Memberships WHERE membership_id = 'TRG3-PASS-01';



-- ======================================================================================
-- TRIGGER 4: trg_adjust_member_count_on_status_change
-- WHO USES IT: Club Secretary & Disciplinary Committee.
-- PURPOSE: When a member's status is toggled between 'Active' and 'Inactive' (e.g. medical
--          leave, academic probation, or reinstatement), Clubs.member_count must adjust
--          automatically (+1 when reactivated, -1 when deactivated).
-- TABLE MONITORED: Memberships (AFTER UPDATE)
-- TABLE MODIFIED:  Clubs (Updates member_count directly)
-- COMPLEXITY: O(1) conditional check and single-row indexed update on Clubs.
-- ======================================================================================

DROP TRIGGER IF EXISTS trg_adjust_member_count_on_status_change;

DELIMITER $$
CREATE TRIGGER trg_adjust_member_count_on_status_change
AFTER UPDATE ON Memberships
FOR EACH ROW
BEGIN
    -- Active -> Inactive : decrement count
    IF OLD.status = 'Active' AND NEW.status = 'Inactive' THEN
        UPDATE Clubs
        SET member_count = member_count - 1
        WHERE club_id = NEW.club_id;
    -- Inactive -> Active : increment count
    ELSEIF OLD.status = 'Inactive' AND NEW.status = 'Active' THEN
        UPDATE Clubs
        SET member_count = member_count + 1
        WHERE club_id = NEW.club_id;
    END IF;
END$$
DELIMITER ;


-- ----- STEP 4A: CHECK BASE TABLES BEFORE STATUS UPDATE -----
SELECT club_id, member_count FROM Clubs WHERE club_id = 'EDC';
SELECT membership_id, student_id, club_id, status FROM Memberships WHERE membership_id = 'EDC-1008';

-- ----- STEP 4B: FIRE TRIGGER (DEACTIVATE AN ACTIVE MEMBER) -----
-- Member EDC-1008 goes on sabbatical / inactive
UPDATE Memberships 
SET status = 'Inactive' 
WHERE membership_id = 'EDC-1008';

-- ----- STEP 4C: VERIFY DIRECT REDUCTION IN CLUBS TABLE -----
-- EDC member_count has automatically decreased by 1:
SELECT club_id, member_count FROM Clubs WHERE club_id = 'EDC';

-- ----- STEP 4D: RE-ACTIVATE MEMBER (RESTORE BASE TABLE) -----
-- Reinstating to 'Active' automatically increments member_count back to original:
UPDATE Memberships 
SET status = 'Active' 
WHERE membership_id = 'EDC-1008';

SELECT club_id, member_count FROM Clubs WHERE club_id = 'EDC';



-- ######################################################################################
-- # MEMBER 3 - TRIGGERS 5 & 6
-- # Event Registration & Authentic Student Feedback Protection
-- ######################################################################################

-- ======================================================================================
-- TRIGGER 5: trg_prevent_registration_for_completed_event
-- WHO USES IT: Event Operations Manager & Registration Portal.
-- PURPOSE: Disallow retrospective registration for events whose status is already
--          'Completed' or 'Cancelled'. Students cannot register after an event has ended.
-- TABLE MONITORED: EventRegistrations (BEFORE INSERT)
-- TABLE MODIFIED:  Enforces constraint on EventRegistrations via SIGNAL SQLSTATE.
-- COMPLEXITY: O(1) indexed status lookup on Events table.
-- ======================================================================================

DROP TRIGGER IF EXISTS trg_prevent_registration_for_completed_event;

DELIMITER $$
CREATE TRIGGER trg_prevent_registration_for_completed_event
BEFORE INSERT ON EventRegistrations
FOR EACH ROW
BEGIN
    DECLARE v_event_status VARCHAR(20);

    SELECT status INTO v_event_status
    FROM Events
    WHERE event_id = NEW.event_id;

    IF v_event_status IN ('Completed', 'Cancelled') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Registration Rejected: Cannot register for an event that is already Completed or Cancelled.';
    END IF;
END$$
DELIMITER ;


-- ----- STEP 5A: CHECK STATUS OF TARGET EVENTS IN EVENTS TABLE -----
-- EDC26-ES is 'Completed', while CSI26-TF is 'Planned'
SELECT event_id, event_name, status FROM Events WHERE event_id IN ('EDC26-ES', 'CSI26-TF');

-- ----- STEP 5B: FIRE TRIGGER (ATTEMPT REGISTRATION ON COMPLETED EVENT) -----
-- Expected Result: FAILS with MySQL Error: "Registration Rejected: Cannot register for an event that is already Completed or Cancelled."
INSERT INTO EventRegistrations (registration_id, event_id, student_id, registration_date, attendance_status)
VALUES ('TRG5-FAIL-01', 'EDC26-ES', 'ME25-0898', CURRENT_DATE, 'Registered');

-- ----- STEP 5C: VERIFY REGISTRATION ON PLANNED EVENT PASSES -----
-- Registering for upcoming 'CSI26-TF' succeeds smoothly:
INSERT INTO EventRegistrations (registration_id, event_id, student_id, registration_date, attendance_status)
VALUES ('TRG5-PASS-01', 'CSI26-TF', 'ME25-0898', CURRENT_DATE, 'Registered');

-- Clean up passed demo row:
DELETE FROM EventRegistrations WHERE registration_id = 'TRG5-PASS-01';



-- ======================================================================================
-- TRIGGER 6: trg_verify_feedback_registration
-- WHO USES IT: Quality Assurance Cell & Academic Review Committee.
-- PURPOSE: Authenticity Assurance: A student can ONLY submit Event Feedback if they were
--          actually registered for that event in EventRegistrations. Prevents ghost reviews.
-- TABLE MONITORED: Feedback (BEFORE INSERT)
-- TABLE MODIFIED:  Enforces cross-table referential integrity check via SIGNAL SQLSTATE.
-- COMPLEXITY: O(1) indexed lookup on EventRegistrations (event_id, student_id).
-- ======================================================================================

DROP TRIGGER IF EXISTS trg_verify_feedback_registration;

DELIMITER $$
CREATE TRIGGER trg_verify_feedback_registration
BEFORE INSERT ON Feedback
FOR EACH ROW
BEGIN
    DECLARE v_reg_count INT DEFAULT 0;

    IF NEW.feedback_type = 'Event' THEN
        SELECT COUNT(*) INTO v_reg_count
        FROM EventRegistrations
        WHERE event_id = NEW.event_id
          AND student_id = NEW.student_id;

        IF v_reg_count = 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Feedback Rejected: Student must be registered for the event before submitting event feedback.';
        END IF;
    END IF;
END$$
DELIMITER ;


-- ----- STEP 6A: CHECK STUDENT REGISTRATION STATUS -----
-- Verify student 'CE25-0100' is NOT registered for event 'CSI26-TF'
SELECT * FROM EventRegistrations 
WHERE event_id = 'CSI26-TF' AND student_id = 'CE25-0100';

-- ----- STEP 6B: FIRE TRIGGER (UNREGISTERED STUDENT SUBMITS FEEDBACK) -----
-- Expected Result: FAILS with MySQL Error: "Feedback Rejected: Student must be registered for the event before submitting event feedback."
INSERT INTO Feedback (feedback_id, student_id, club_id, event_id, feedback_type, rating, comments, feedback_date)
VALUES ('TRG6-FAIL-01', 'CE25-0100', NULL, 'CSI26-TF', 'Event', 5, 'Great workshop!', CURRENT_DATE);

-- ----- STEP 6C: REGISTERED STUDENT SUBMISSION SUCCEEDS -----
-- Student 'ME25-0893' IS registered for 'CSI26-TF', so their feedback inserts cleanly:
INSERT INTO Feedback (feedback_id, student_id, club_id, event_id, feedback_type, rating, comments, feedback_date)
VALUES ('TRG6-PASS-01', 'ME25-0893', NULL, 'CSI26-TF', 'Event', 4, 'Very engaging hands-on demonstration.', CURRENT_DATE);

-- Clean up passed demo feedback:
DELETE FROM Feedback WHERE feedback_id = 'TRG6-PASS-01';



-- ######################################################################################
-- # MEMBER 4 - TRIGGERS 7 & 8
-- # Automated Event Lifecycle Transition & Zero-Config Club Provisioning
-- ######################################################################################

-- ======================================================================================
-- TRIGGER 7: trg_auto_progress_event_on_attendance
-- WHO USES IT: Campus Venue In-Charge & Turnstile Attendance Desk.
-- PURPOSE: When attendance is marked ('Attended') for any registered student at an event,
--          if the event in the Events table is still in 'Planned' status, it automatically
--          progresses to 'Ongoing'. Eliminates manual status toggling by event managers.
-- TABLE MONITORED: EventRegistrations (AFTER UPDATE)
-- TABLE MODIFIED:  Events (Updates status directly)
-- COMPLEXITY: O(1) single-row indexed update on Events table.
-- ======================================================================================

DROP TRIGGER IF EXISTS trg_auto_progress_event_on_attendance;

DELIMITER $$
CREATE TRIGGER trg_auto_progress_event_on_attendance
AFTER UPDATE ON EventRegistrations
FOR EACH ROW
BEGIN
    IF NEW.attendance_status = 'Attended' AND OLD.attendance_status <> 'Attended' THEN
        UPDATE Events
        SET status = 'Ongoing'
        WHERE event_id = NEW.event_id
          AND status = 'Planned';
    END IF;
END$$
DELIMITER ;


-- ----- STEP 7A: CHECK CURRENT STATUS IN EVENTS TABLE -----
-- Notice event 'CSI26-TF' is currently 'Planned'
SELECT event_id, event_name, status FROM Events WHERE event_id = 'CSI26-TF';
SELECT registration_id, event_id, student_id, attendance_status FROM EventRegistrations WHERE registration_id = 'TF26-0893';

-- ----- STEP 7B: FIRE TRIGGER (MARK ATTENDANCE AT REGISTRATION DESK) -----
-- Mark attendee as 'Attended'
UPDATE EventRegistrations 
SET attendance_status = 'Attended' 
WHERE registration_id = 'TF26-0893';

-- ----- STEP 7C: VERIFY DIRECT CHANGE IN EVENTS BASE TABLE -----
-- The status of 'CSI26-TF' in the original Events table has automatically flipped to 'Ongoing'!
SELECT event_id, event_name, status FROM Events WHERE event_id = 'CSI26-TF';

-- ----- STEP 7D: RESET (RESTORE BASE TABLE STATE) -----
UPDATE Events SET status = 'Planned' WHERE event_id = 'CSI26-TF';
UPDATE EventRegistrations SET attendance_status = 'Registered' WHERE registration_id = 'TF26-0893';



-- ======================================================================================
-- TRIGGER 8: trg_auto_create_club_profile
-- WHO USES IT: Dean of Student Affairs & Club Registration Committee.
-- PURPOSE: Zero-Config Profile Provisioning: Whenever a new club is recognized and inserted
--          into the Clubs table, a matching baseline profile row (with standardized institutional
--          email and Instagram handle) is automatically provisioned in ClubProfile.
-- TABLE MONITORED: Clubs (AFTER INSERT)
-- TABLE MODIFIED:  ClubProfile (Inserts corresponding institutional profile directly)
-- COMPLEXITY: O(1) single-row insert on ClubProfile.
-- ======================================================================================

DROP TRIGGER IF EXISTS trg_auto_create_club_profile;

DELIMITER $$
CREATE TRIGGER trg_auto_create_club_profile
AFTER INSERT ON Clubs
FOR EACH ROW
BEGIN
    INSERT INTO ClubProfile (club_id, official_email, instagram_handle)
    VALUES (
        NEW.club_id,
        CONCAT(LOWER(NEW.club_id), '@vit.edu'),
        CONCAT('@vit_', LOWER(NEW.club_id))
    );
END$$
DELIMITER ;


-- ----- STEP 8A: CHECK CLUBPROFILE BASE TABLE BEFORE TRIGGER -----
-- Notice no profile exists for club 'ACM'
SELECT * FROM ClubProfile WHERE club_id = 'ACM';

-- ----- STEP 8B: FIRE TRIGGER (INSERT A NEW CLUB INTO CLUBS) -----
-- Faculty coordinator 'CE-AS' registers a new technical club 'ACM'
INSERT INTO Clubs (club_id, club_name, category, faculty_id, description, member_count)
VALUES ('ACM', 'Association for Computing Machinery', 'Technical', 'CE-AS', 
        'Student chapter for advanced computing research and competitive programming.', 0);

-- ----- STEP 8C: VERIFY DIRECT INSERTION IN CLUBPROFILE BASE TABLE -----
-- The corresponding profile row in ClubProfile was created automatically!
SELECT * FROM ClubProfile WHERE club_id = 'ACM';

-- ----- STEP 8D: CLEANUP (RESTORE BASE TABLES) -----
DELETE FROM ClubProfile WHERE club_id = 'ACM';
DELETE FROM Clubs WHERE club_id = 'ACM';


-- ======================================================================================
-- SUMMARY VERIFICATION: CONFIRM ONLY THE 8 CANONICAL TABLES EXIST
-- ======================================================================================
SHOW TABLES;
