-- ===========================================================
-- CURSOR ASSIGNMENT (2 cursors) - STEP BY STEP
-- Database: trial_club (Club Management System)
--
-- BEFORE YOU START: run Club_Management_System_BASE.sql (whole file)
-- in the BASE tab. Use THIS file in a SECOND tab. Do NOT run it all at once.
--
-- IN THIS VERSION THE CHANGES ARE REAL AND PERMANENT (no rollback), so you
-- can switch to the BASE tab and see them there. To look at a table in the
-- BASE tab: scroll to the 8 SELECT lines at the bottom of the base file,
-- select ONE line (e.g. SELECT * FROM Clubs ...) and press Ctrl+Shift+Enter.
-- !! Never run the whole base file during the demo - it resets everything.
-- For each step: select ONLY that step (banner to banner) and press
-- Ctrl+Shift+Enter. Do the steps in order.
--
-- A CURSOR reads a query result ONE ROW AT A TIME inside a stored
-- procedure, so we can take a decision for each row.
-- Every cursor: DECLARE -> OPEN -> FETCH in a LOOP -> LEAVE -> CLOSE
-- ===========================================================


-- ===========================================================
-- STEP 1A : CREATE CURSOR 1 = sp_audit_club_counts  (shows no tables)
-- WHO USES IT: the database admin.
-- WHY: Clubs.member_count is a stored number. If it is edited by mistake
-- it no longer matches the real Memberships rows. This cursor checks every
-- club, one by one. p_fix = 0 -> only report.  p_fix = 1 -> report and repair.
-- COMPLEXITY: loops over the 5 clubs, one COUNT on Memberships per club.
-- ===========================================================
USE trial_club;
ROLLBACK;
DROP PROCEDURE IF EXISTS sp_audit_club_counts;

DELIMITER $$
CREATE PROCEDURE sp_audit_club_counts(IN p_fix TINYINT)
BEGIN
    DECLARE v_done   INT DEFAULT 0;
    DECLARE v_club   VARCHAR(20);
    DECLARE v_stored INT;
    DECLARE v_actual INT;
    DECLARE v_result VARCHAR(20);

    -- the cursor: one row per club
    DECLARE cur_clubs CURSOR FOR
        SELECT club_id, member_count FROM Clubs ORDER BY club_id;
    -- when rows run out, set v_done = 1
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

    DROP TEMPORARY TABLE IF EXISTS tmp_audit;
    CREATE TEMPORARY TABLE tmp_audit (
        club_id VARCHAR(20), stored_count INT, actual_count INT, result VARCHAR(20)
    );

    OPEN cur_clubs;
    read_loop: LOOP
        FETCH cur_clubs INTO v_club, v_stored;
        IF v_done = 1 THEN
            LEAVE read_loop;
        END IF;

        -- real number of members of this club
        SELECT COUNT(*) INTO v_actual FROM Memberships WHERE club_id = v_club;

        IF v_stored <=> v_actual THEN
            SET v_result = 'OK';
        ELSEIF p_fix = 1 THEN
            UPDATE Clubs SET member_count = v_actual WHERE club_id = v_club;
            SET v_result = 'FIXED';
        ELSE
            SET v_result = 'MISMATCH';
        END IF;

        INSERT INTO tmp_audit VALUES (v_club, v_stored, v_actual, v_result);
    END LOOP;
    CLOSE cur_clubs;

    SELECT * FROM tmp_audit;
    DROP TEMPORARY TABLE tmp_audit;
END$$
DELIMITER ;


-- ===========================================================
-- STEP 1B : RUN THE AUDIT ON THE ORIGINAL DATA
-- BASE TAB first: show Clubs table -> CSI member_count = 17.
-- EXPECTED here: 5 rows, all OK.
-- Say: 'Stored counts equal the real counts, the database is healthy.'
-- ===========================================================
CALL sp_audit_club_counts(0);


-- ===========================================================
-- STEP 1C : BREAK THE REAL TABLE (permanent change)
-- Sets CSI member_count to 99 in the real Clubs table.
-- THEN GO TO THE BASE TAB and run: SELECT * FROM Clubs ORDER BY club_id;
-- EXPECTED in base tab: CSI member_count = 99.
-- ===========================================================
SET autocommit = 1;
UPDATE Clubs SET member_count = 99 WHERE club_id = 'CSI';


-- ===========================================================
-- STEP 1D : THE CURSOR DETECTS THE PROBLEM (report only)
-- EXPECTED: CSI row -> stored 99, actual 17, result MISMATCH. Others OK.
-- This step does not change any table.
-- ===========================================================
CALL sp_audit_club_counts(0);


-- ===========================================================
-- STEP 1E : THE CURSOR REPAIRS THE REAL TABLE (permanent change)
-- EXPECTED here: CSI row -> stored 99, actual 17, result FIXED.
-- THEN GO TO THE BASE TAB and run: SELECT * FROM Clubs ORDER BY club_id;
-- EXPECTED in base tab: CSI member_count = 17 again = original.
-- Repeat 1C-1E any time.
-- ===========================================================
CALL sp_audit_club_counts(1);


-- ===========================================================
-- STEP 2A : CREATE CURSOR 2 = sp_recruitment_leads  (shows no tables)
-- WHO USES IT: a club president.
-- WHY: students who are NOT members but keep joining club events are the
-- best people to invite. This gives a ready list + which club to invite
-- each one to. p_min_events = minimum events a non-member must have joined.
-- LOGIC: cursor = non-members who registered for events. For each student
-- an inner query finds the club whose events they joined the most.
-- COMPLEXITY: one pass over 7 students + one small grouped query per student.
-- ===========================================================
USE trial_club;
ROLLBACK;
DROP PROCEDURE IF EXISTS sp_recruitment_leads;

DELIMITER $$
CREATE PROCEDURE sp_recruitment_leads(IN p_min_events INT)
BEGIN
    DECLARE v_done   INT DEFAULT 0;
    DECLARE v_sid    VARCHAR(20);
    DECLARE v_name   VARCHAR(100);
    DECLARE v_events INT;
    DECLARE v_club   VARCHAR(100);

    -- the cursor: students with NO membership but at least p_min_events registrations
    DECLARE cur_leads CURSOR FOR
        SELECT s.student_id, s.name, COUNT(*) AS events_joined
        FROM Students s
        JOIN EventRegistrations er ON er.student_id = s.student_id
        WHERE NOT EXISTS (SELECT 1 FROM Memberships m WHERE m.student_id = s.student_id)
        GROUP BY s.student_id, s.name
        HAVING COUNT(*) >= p_min_events
        ORDER BY events_joined DESC, s.student_id;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

    DROP TEMPORARY TABLE IF EXISTS tmp_leads;
    CREATE TEMPORARY TABLE tmp_leads (
        student_id VARCHAR(20), name VARCHAR(100),
        events_joined INT, invite_to_club VARCHAR(100)
    );

    OPEN cur_leads;
    lead_loop: LOOP
        FETCH cur_leads INTO v_sid, v_name, v_events;
        IF v_done = 1 THEN
            LEAVE lead_loop;
        END IF;

        -- the club whose events this student joined the most
        SELECT c.club_name INTO v_club
        FROM EventRegistrations er
        JOIN Events e ON e.event_id = er.event_id
        JOIN Clubs  c ON c.club_id  = e.club_id
        WHERE er.student_id = v_sid
        GROUP BY c.club_id, c.club_name
        ORDER BY COUNT(*) DESC, c.club_id
        LIMIT 1;

        INSERT INTO tmp_leads VALUES (v_sid, v_name, v_events, v_club);
    END LOOP;
    CLOSE cur_leads;

    SELECT * FROM tmp_leads;
    DROP TEMPORARY TABLE tmp_leads;
END$$
DELIMITER ;


-- ===========================================================
-- STEP 2B : SHOW THE LEADS (original state)
-- EXPECTED: 7 rows (student, events joined, club to invite):
--   CE25-0314  2  Computer Society of India
--   CE25-0342  2  Social Welfare and Development Committee
--   CE25-0784  2  Computer Society of India
--   CE25-0692  1  Computer Society of India
--   EE25-0191  1  Entrepreneurship Development Club
--   ELE25-0575 1  Social Welfare and Development Committee
--   ELE25-0666 1  Entrepreneurship Development Club
-- Say: 'A club head can now invite these students personally.'
-- ===========================================================
CALL sp_recruitment_leads(1);


-- ===========================================================
-- STEP 2C : ONLY THE MOST ENGAGED (p_min_events = 2)
-- EXPECTED: 3 rows: CE25-0314, CE25-0342, CE25-0784. Same procedure,
-- different input.
-- ===========================================================
CALL sp_recruitment_leads(2);


-- ===========================================================
-- STEP 2D : A LEAD JOINS THE CLUB (permanent change in Memberships)
-- Student CE25-0314 joins CSI. Row DEMO-LEAD-001 is added.
-- THEN GO TO THE BASE TAB and run: SELECT * FROM Memberships ORDER BY membership_id;
-- EXPECTED in base tab: a new row DEMO-LEAD-001 (CE25-0314, CSI).
-- ===========================================================
SET autocommit = 1;
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('DEMO-LEAD-001', 'CE25-0314', 'CSI', 'Member', '2026-10-18', 'Active');


-- ===========================================================
-- STEP 2E : RUN THE LEADS CURSOR AGAIN
-- EXPECTED: only 6 rows - CE25-0314 is gone from the list because she
-- is now a member. The cursor reads the CURRENT table data.
-- ===========================================================
CALL sp_recruitment_leads(1);


-- ===========================================================
-- STEP 2F : UNDO - REMOVE THE DEMO ROW, THEN RUN THE CURSOR
-- EXPECTED here: lead list is back to 7 rows, CE25-0314 included.
-- THEN GO TO THE BASE TAB and run: SELECT * FROM Memberships ORDER BY membership_id;
-- EXPECTED in base tab: the DEMO-LEAD-001 row is gone (original table).
-- ===========================================================
DELETE FROM Memberships WHERE membership_id = 'DEMO-LEAD-001';
CALL sp_recruitment_leads(1);


-- ===========================================================
-- OPTIONAL CLEAN-UP (only if you want to remove the procedures)
-- ===========================================================
-- DROP PROCEDURE IF EXISTS sp_audit_club_counts;
-- DROP PROCEDURE IF EXISTS sp_recruitment_leads;