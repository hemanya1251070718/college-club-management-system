-- ======================================================================================
-- CURSOR ASSIGNMENT - 8 NON-IDENTICAL CURSORS (STEP-BY-STEP DEMO)
-- Database: trial_club (College Club Management System)
-- Course: Database Management Systems (DBMS Mini Project Evaluation)
--
-- DISTRIBUTION FOR GROUP OF 4 MEMBERS (2 Unique Cursors per Member):
--   Member 1: Cursor 1 (Audit & Repair Club Counts) & Cursor 2 (Recruitment Leads & Auto-Enroll)
--   Member 2: Cursor 3 (Reconcile Event Performance Budgets) & Cursor 4 (Automated Past Event Closure)
--   Member 3: Cursor 5 (Deactivate Chronic Absentee Members) & Cursor 6 (Merit Promotion to Core Member)
--   Member 4: Cursor 7 (Graduating Senior Alumni Transition) & Cursor 8 (Anonymize Sensitive Feedback)
--
-- INSTRUCTIONS:
-- 1. Run Club_Management_System_BASE.sql first to ensure clean base data.
-- 2. Open THIS file in a separate tab in MySQL Workbench / Editor.
-- 3. Run each step ONE BY ONE (select step banner to banner and press Ctrl+Shift+Enter).
-- 4. In every cursor, p_apply = 0 provides a preview/audit report, while p_apply = 1 makes
--    permanent, real modifications directly in the original 8 base tables!
-- 5. No permanent 9th table is ever created; all temporary reporting tables are dropped before return.
-- ======================================================================================

USE trial_club;
SET autocommit = 1;


-- ######################################################################################
-- # MEMBER 1 - CURSORS 1 & 2
-- # Data Integrity Auditing & Prospective Member Auto-Recruitment
-- ######################################################################################

-- ======================================================================================
-- CURSOR 1: sp_audit_club_counts
-- WHO USES IT: Database Administrator / Lead Faculty Coordinator.
-- WHY: Clubs.member_count is a denormalized performance cache. If manual inserts or deletions
--      cause it to drift from actual active Memberships rows, this cursor iterates club by
--      club, calculates the true count, and repairs the Clubs base table.
-- PARAMETERS: p_fix (0 = Preview only, 1 = Update Clubs table directly)
-- LOGIC: Cursor over Clubs -> COUNT on Memberships per club -> UPDATE Clubs if p_fix=1.
-- COMPLEXITY: O(C) where C is the number of clubs, with indexed count on Memberships.
-- ======================================================================================

DROP PROCEDURE IF EXISTS sp_audit_club_counts;

DELIMITER $$
CREATE PROCEDURE sp_audit_club_counts(IN p_fix TINYINT)
BEGIN
    DECLARE v_done   INT DEFAULT 0;
    DECLARE v_club   VARCHAR(20);
    DECLARE v_stored INT;
    DECLARE v_actual INT;
    DECLARE v_result VARCHAR(20);

    -- Cursor iterating through all clubs
    DECLARE cur_clubs CURSOR FOR
        SELECT club_id, member_count FROM Clubs ORDER BY club_id;
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

        -- Count actual active members in Memberships table
        SELECT COUNT(*) INTO v_actual 
        FROM Memberships 
        WHERE club_id = v_club AND status = 'Active';

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
    DROP TEMPORARY TABLE IF EXISTS tmp_audit;
END$$
DELIMITER ;


-- ----- STEP 1A: RUN AUDIT ON ORIGINAL CLEAN DATA -----
-- Expected Result: All clubs show 'OK'
CALL sp_audit_club_counts(0);

-- ----- STEP 1B: SIMULATE DRIFT IN BASE CLUBS TABLE -----
-- Manually tamper CSI member_count to 99 in the real Clubs table
UPDATE Clubs SET member_count = 99 WHERE club_id = 'CSI';
SELECT club_id, club_name, member_count FROM Clubs WHERE club_id = 'CSI';

-- ----- STEP 1C: DETECT THE MISMATCH (PREVIEW MODE) -----
-- Expected: CSI row shows stored=99, actual=17, result='MISMATCH'
CALL sp_audit_club_counts(0);

-- ----- STEP 1D: AUTOMATICALLY REPAIR BASE TABLE -----
-- Expected: CSI row shows result='FIXED'
CALL sp_audit_club_counts(1);

-- Verify in base table: member_count is permanently restored to 17!
SELECT club_id, club_name, member_count FROM Clubs WHERE club_id = 'CSI';



-- ======================================================================================
-- CURSOR 2: sp_recruitment_leads_and_auto_invite
-- WHO USES IT: Club Presidents & Head of Student Recruitment.
-- WHY: Students who participate in multiple events but have never formally joined a club
--      are high-value prospective recruits. This cursor iterates over non-members, finds
--      the club whose events they registered for the most, and if p_auto_invite=1,
--      automatically provisions them as active 'Volunteer' members in Memberships and
--      increments Clubs.member_count.
-- PARAMETERS: p_min_events (filter), p_auto_invite (0 = Report only, 1 = Insert into Memberships)
-- COMPLEXITY: O(N) where N is non-members registered for events, with inner group aggregate.
-- ======================================================================================

DROP PROCEDURE IF EXISTS sp_recruitment_leads_and_auto_invite;

DELIMITER $$
CREATE PROCEDURE sp_recruitment_leads_and_auto_invite(
    IN p_min_events INT,
    IN p_auto_invite TINYINT
)
BEGIN
    DECLARE v_done       INT DEFAULT 0;
    DECLARE v_sid        VARCHAR(20);
    DECLARE v_name       VARCHAR(100);
    DECLARE v_events     INT;
    DECLARE v_target_cid VARCHAR(20);
    DECLARE v_target_cname VARCHAR(100);
    DECLARE v_action     VARCHAR(30);

    -- Cursor over students with NO club membership but >= p_min_events registrations
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
        student_id VARCHAR(20), student_name VARCHAR(100),
        events_joined INT, suggested_club_id VARCHAR(20),
        suggested_club_name VARCHAR(100), action_taken VARCHAR(30)
    );

    OPEN cur_leads;
    lead_loop: LOOP
        FETCH cur_leads INTO v_sid, v_name, v_events;
        IF v_done = 1 THEN
            LEAVE lead_loop;
        END IF;

        -- Find the club whose events this non-member attended/registered for most
        SELECT c.club_id, c.club_name 
        INTO v_target_cid, v_target_cname
        FROM EventRegistrations er
        JOIN Events e ON e.event_id = er.event_id
        JOIN Clubs  c ON c.club_id  = e.club_id
        WHERE er.student_id = v_sid
        GROUP BY c.club_id, c.club_name
        ORDER BY COUNT(*) DESC, c.club_id
        LIMIT 1;

        IF p_auto_invite = 1 THEN
            -- Directly insert a new membership in the original Memberships table!
            INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
            VALUES (CONCAT('AUTO-', v_sid), v_sid, v_target_cid, 'Volunteer', CURRENT_DATE, 'Active');

            -- Update member count in the original Clubs table!
            UPDATE Clubs 
            SET member_count = member_count + 1 
            WHERE club_id = v_target_cid;

            SET v_action = 'ENROLLED AS VOLUNTEER';
        ELSE
            SET v_action = 'RECOMMENDED';
        END IF;

        INSERT INTO tmp_leads VALUES (v_sid, v_name, v_events, v_target_cid, v_target_cname, v_action);
    END LOOP;
    CLOSE cur_leads;

    SELECT * FROM tmp_leads;
    DROP TEMPORARY TABLE IF EXISTS tmp_leads;
END$$
DELIMITER ;


-- ----- STEP 2A: RUN RECRUITMENT ANALYSIS (REPORT MODE) -----
-- Identifies non-members with >= 2 event participations (e.g. CE25-0314, CE25-0342, CE25-0784)
CALL sp_recruitment_leads_and_auto_invite(2, 0);

-- ----- STEP 2B: AUTO-ENROLL LEADS INTO ORIGINAL BASE TABLES -----
-- Provisions active memberships directly into Memberships table:
CALL sp_recruitment_leads_and_auto_invite(2, 1);

-- ----- STEP 2C: VERIFY DIRECT INSERTIONS IN BASE MEMBERSHIPS TABLE -----
SELECT * FROM Memberships WHERE membership_id LIKE 'AUTO-%';

-- ----- STEP 2D: CLEANUP (RESTORE BASE TABLE STATE) -----
DELETE FROM Memberships WHERE membership_id LIKE 'AUTO-%';
UPDATE Clubs SET member_count = (SELECT COUNT(*) FROM Memberships m WHERE m.club_id = Clubs.club_id AND m.status = 'Active');



-- ######################################################################################
-- # MEMBER 2 - CURSORS 3 & 4
-- # Financial Budget Allocation & Automated Event Lifecycle Closure
-- ######################################################################################

-- ======================================================================================
-- CURSOR 3: sp_reconcile_event_budgets
-- WHO USES IT: Dean of Student Activities & Student Council Treasurer.
-- WHY: High-performing club events that received stellar ratings from attendees (average
--      feedback >= p_min_rating) qualify for performance bonus budget reconciliation.
--      This cursor loops through all Completed events, aggregates attendee ratings from
--      Feedback, calculates the bonus, and updates Events.budget_allocated directly.
-- PARAMETERS: p_min_rating (e.g. 4.5), p_bonus_pct (e.g. 10.0%), p_apply (0=preview, 1=apply)
-- COMPLEXITY: O(E_comp) where E_comp is Completed events, with grouped aggregate on Feedback.
-- ======================================================================================

DROP PROCEDURE IF EXISTS sp_reconcile_event_budgets;

DELIMITER $$
CREATE PROCEDURE sp_reconcile_event_budgets(
    IN p_min_rating DECIMAL(3,2),
    IN p_bonus_pct  DECIMAL(5,2),
    IN p_apply      TINYINT
)
BEGIN
    DECLARE v_done       INT DEFAULT 0;
    DECLARE v_eid        VARCHAR(30);
    DECLARE v_ename      VARCHAR(150);
    DECLARE v_old_budget DECIMAL(10,2);
    DECLARE v_avg_rating DECIMAL(3,2);
    DECLARE v_bonus      DECIMAL(10,2);
    DECLARE v_new_budget DECIMAL(10,2);
    DECLARE v_status     VARCHAR(30);

    -- Cursor over all Completed events
    DECLARE cur_events CURSOR FOR
        SELECT event_id, event_name, budget_allocated 
        FROM Events 
        WHERE status = 'Completed' 
        ORDER BY event_id;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

    DROP TEMPORARY TABLE IF EXISTS tmp_budget_recon;
    CREATE TEMPORARY TABLE tmp_budget_recon (
        event_id VARCHAR(30), event_name VARCHAR(150),
        avg_rating DECIMAL(3,2), old_budget DECIMAL(10,2),
        bonus_applied DECIMAL(10,2), new_budget DECIMAL(10,2),
        action_status VARCHAR(30)
    );

    OPEN cur_events;
    event_loop: LOOP
        FETCH cur_events INTO v_eid, v_ename, v_old_budget;
        IF v_done = 1 THEN
            LEAVE event_loop;
        END IF;

        -- Calculate average rating from genuine attendee Feedback
        SELECT COALESCE(AVG(rating), 0) INTO v_avg_rating
        FROM Feedback
        WHERE event_id = v_eid;

        IF v_avg_rating >= p_min_rating THEN
            SET v_bonus = ROUND(v_old_budget * (p_bonus_pct / 100), 2);
            SET v_new_budget = v_old_budget + v_bonus;

            IF p_apply = 1 THEN
                UPDATE Events 
                SET budget_allocated = v_new_budget 
                WHERE event_id = v_eid;
                SET v_status = 'BUDGET UPDATED';
            ELSE
                SET v_status = 'QUALIFIED FOR BONUS';
            END IF;
        ELSE
            SET v_bonus = 0.00;
            SET v_new_budget = v_old_budget;
            SET v_status = 'NO BONUS (BELOW THRESHOLD)';
        END IF;

        INSERT INTO tmp_budget_recon 
        VALUES (v_eid, v_ename, v_avg_rating, v_old_budget, v_bonus, v_new_budget, v_status);
    END LOOP;
    CLOSE cur_events;

    SELECT * FROM tmp_budget_recon;
    DROP TEMPORARY TABLE IF EXISTS tmp_budget_recon;
END$$
DELIMITER ;


-- ----- STEP 3A: CHECK BASE EVENTS TABLE BEFORE BUDGET RECONCILIATION -----
SELECT event_id, event_name, budget_allocated, status FROM Events WHERE status = 'Completed';

-- ----- STEP 3B: RUN BUDGET RECONCILIATION (PREVIEW MODE) -----
-- High rating threshold 4.5, 10% bonus preview
CALL sp_reconcile_event_budgets(4.50, 10.00, 0);

-- ----- STEP 3C: APPLY BUDGET PERFORMANCE BONUSES TO BASE TABLE -----
CALL sp_reconcile_event_budgets(4.50, 10.00, 1);

-- ----- STEP 3D: VERIFY DIRECT BUDGET INCREMENT IN EVENTS BASE TABLE -----
-- E-Summit 26 (EDC26-ES) has increased from 50000.00 to 55000.00!
SELECT event_id, event_name, budget_allocated, status FROM Events WHERE status = 'Completed';

-- ----- STEP 3E: CLEANUP (RESTORE ORIGINAL BUDGETS) -----
UPDATE Events SET budget_allocated = 50000.00 WHERE event_id = 'EDC26-ES';
UPDATE Events SET budget_allocated = 25000.00 WHERE event_id = 'SWD26-NGO';
UPDATE Events SET budget_allocated = 12000.00 WHERE event_id = 'ZEPH26-GF';



-- ======================================================================================
-- CURSOR 4: sp_close_past_events
-- WHO USES IT: Event Operations Head & Academic Scheduler.
-- WHY: Events whose scheduled date has passed (event_date < p_cutoff_date) but remain lingering
--      in 'Planned' status must be programmatically reconciled. The cursor scans each past
--      planned event: if attendance was recorded, it sets status to 'Completed'; if zero
--      students attended, it marks the event 'Cancelled'.
-- PARAMETERS: p_cutoff_date (e.g. '2026-01-01'), p_apply (0=preview, 1=update Events table)
-- COMPLEXITY: O(E_past) with index-assisted attendance count on EventRegistrations.
-- ======================================================================================

DROP PROCEDURE IF EXISTS sp_close_past_events;

DELIMITER $$
CREATE PROCEDURE sp_close_past_events(
    IN p_cutoff_date DATE,
    IN p_apply       TINYINT
)
BEGIN
    DECLARE v_done       INT DEFAULT 0;
    DECLARE v_eid        VARCHAR(30);
    DECLARE v_ename      VARCHAR(150);
    DECLARE v_edate      DATE;
    DECLARE v_attended   INT;
    DECLARE v_new_status VARCHAR(20);
    DECLARE v_action     VARCHAR(30);

    -- Cursor over Planned events whose scheduled date is in the past
    DECLARE cur_past_events CURSOR FOR
        SELECT event_id, event_name, event_date
        FROM Events
        WHERE status = 'Planned' AND event_date < p_cutoff_date
        ORDER BY event_date;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

    DROP TEMPORARY TABLE IF EXISTS tmp_event_closure;
    CREATE TEMPORARY TABLE tmp_event_closure (
        event_id VARCHAR(30), event_name VARCHAR(150),
        event_date DATE, attendees_count INT,
        resolved_status VARCHAR(20), action_taken VARCHAR(30)
    );

    OPEN cur_past_events;
    close_loop: LOOP
        FETCH cur_past_events INTO v_eid, v_ename, v_edate;
        IF v_done = 1 THEN
            LEAVE close_loop;
        END IF;

        -- Count actual attendees who showed up
        SELECT COUNT(*) INTO v_attended
        FROM EventRegistrations
        WHERE event_id = v_eid AND attendance_status = 'Attended';

        IF v_attended > 0 THEN
            SET v_new_status = 'Completed';
        ELSE
            SET v_new_status = 'Cancelled';
        END IF;

        IF p_apply = 1 THEN
            UPDATE Events 
            SET status = v_new_status 
            WHERE event_id = v_eid;
            SET v_action = CONCAT('STATUS -> ', v_new_status);
        ELSE
            SET v_action = CONCAT('PROPOSED -> ', v_new_status);
        END IF;

        INSERT INTO tmp_event_closure 
        VALUES (v_eid, v_ename, v_edate, v_attended, v_new_status, v_action);
    END LOOP;
    CLOSE cur_past_events;

    SELECT * FROM tmp_event_closure;
    DROP TEMPORARY TABLE IF EXISTS tmp_event_closure;
END$$
DELIMITER ;


-- ----- STEP 4A: CHECK BASE TABLE FOR PAST PLANNED EVENTS -----
-- CSI25-PYW (attended) and EDC25-IDEA (0 attendees) are both currently 'Planned'
SELECT event_id, event_name, event_date, status FROM Events WHERE event_id IN ('CSI25-PYW', 'EDC25-IDEA');

-- ----- STEP 4B: RUN EVENT CLOSURE (PREVIEW MODE) -----
-- Cutoff '2026-01-01': CSI25-PYW qualifies for 'Completed', EDC25-IDEA qualifies for 'Cancelled'
CALL sp_close_past_events('2026-01-01', 0);

-- ----- STEP 4C: APPLY EVENT CLOSURES TO BASE EVENTS TABLE -----
CALL sp_close_past_events('2026-01-01', 1);

-- ----- STEP 4D: VERIFY DIRECT UPDATES IN BASE EVENTS TABLE -----
SELECT event_id, event_name, event_date, status FROM Events WHERE event_id IN ('CSI25-PYW', 'EDC25-IDEA');

-- ----- STEP 4E: RESET (RESTORE BASE TABLE STATE) -----
UPDATE Events SET status = 'Planned' WHERE event_id IN ('CSI25-PYW', 'EDC25-IDEA');



-- ######################################################################################
-- # MEMBER 3 - CURSORS 5 & 6
-- # Disciplinary Attendance Governance & Merit-Based Leadership Promotion
-- ######################################################################################

-- ======================================================================================
-- CURSOR 5: sp_deactivate_inactive_members
-- WHO USES IT: Club Secretaries & Disciplinary Board.
-- WHY: Club constitution dictates active attendance. Members who register for events of
--      their club but chronically skip (attendance_status = 'Registered' without ever
--      attending) >= p_max_missed_events times are deactivated to free up capacity.
--      The cursor loops through active members, counts their unexcused absences, and
--      updates Memberships.status to 'Inactive' and decrements Clubs.member_count.
-- PARAMETERS: p_max_missed_events (e.g. 2), p_apply (0=preview, 1=update Memberships & Clubs)
-- COMPLEXITY: O(M_active) where M_active is active members, with join to EventRegistrations.
-- ======================================================================================

DROP PROCEDURE IF EXISTS sp_deactivate_inactive_members;

DELIMITER $$
CREATE PROCEDURE sp_deactivate_inactive_members(
    IN p_max_missed_events INT,
    IN p_apply             TINYINT
)
BEGIN
    DECLARE v_done         INT DEFAULT 0;
    DECLARE v_mid          VARCHAR(30);
    DECLARE v_sid          VARCHAR(20);
    DECLARE v_cid          VARCHAR(20);
    DECLARE v_sname        VARCHAR(100);
    DECLARE v_missed_count INT;
    DECLARE v_action       VARCHAR(30);

    -- Cursor over active non-executive members
    DECLARE cur_active_members CURSOR FOR
        SELECT m.membership_id, m.student_id, m.club_id, s.name
        FROM Memberships m
        JOIN Students s ON s.student_id = m.student_id
        WHERE m.status = 'Active' AND m.role IN ('Member', 'Volunteer')
        ORDER BY m.membership_id;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

    DROP TEMPORARY TABLE IF EXISTS tmp_absentee_audit;
    CREATE TEMPORARY TABLE tmp_absentee_audit (
        membership_id VARCHAR(30), student_id VARCHAR(20),
        student_name VARCHAR(100), club_id VARCHAR(20),
        missed_events INT, action_taken VARCHAR(30)
    );

    OPEN cur_active_members;
    member_loop: LOOP
        FETCH cur_active_members INTO v_mid, v_sid, v_cid, v_sname;
        IF v_done = 1 THEN
            LEAVE member_loop;
        END IF;

        -- Count missed registrations for events hosted by their club
        SELECT COUNT(*) INTO v_missed_count
        FROM EventRegistrations er
        JOIN Events e ON e.event_id = er.event_id
        WHERE er.student_id = v_sid 
          AND e.club_id = v_cid
          AND er.attendance_status = 'Registered';

        IF v_missed_count >= p_max_missed_events THEN
            IF p_apply = 1 THEN
                -- Set status to Inactive in base Memberships table
                UPDATE Memberships 
                SET status = 'Inactive' 
                WHERE membership_id = v_mid;

                -- Adjust club size in base Clubs table
                UPDATE Clubs 
                SET member_count = member_count - 1 
                WHERE club_id = v_cid;

                SET v_action = 'DEACTIVATED';
            ELSE
                SET v_action = 'FLAGGED FOR DEACTIVATION';
            END IF;

            INSERT INTO tmp_absentee_audit 
            VALUES (v_mid, v_sid, v_sname, v_cid, v_missed_count, v_action);
        END IF;
    END LOOP;
    CLOSE cur_active_members;

    SELECT * FROM tmp_absentee_audit;
    DROP TEMPORARY TABLE IF EXISTS tmp_absentee_audit;
END$$
DELIMITER ;


-- ----- STEP 5A: CHECK BASE TABLE FOR TARGET MEMBER -----
-- Member ZEPHYR-0063 (Varun Kadam) registered for 2 Zephyr events but attended 0
SELECT membership_id, student_id, club_id, role, status FROM Memberships WHERE membership_id = 'ZEPHYR-0063';
SELECT club_id, member_count FROM Clubs WHERE club_id = 'ZEPHYR';

-- ----- STEP 5B: RUN ABSENTEE AUDIT (PREVIEW MODE) -----
-- Flags members with >= 2 unexcused absences
CALL sp_deactivate_inactive_members(2, 0);

-- ----- STEP 5C: DEACTIVATE CHRONIC ABSENTEES IN BASE TABLE -----
CALL sp_deactivate_inactive_members(2, 1);

-- ----- STEP 5D: VERIFY CHANGES IN BASE MEMBERSHIPS AND CLUBS TABLES -----
-- ZEPHYR-0063 status is now 'Inactive', and ZEPHYR member_count decremented!
SELECT membership_id, student_id, club_id, role, status FROM Memberships WHERE membership_id = 'ZEPHYR-0063';
SELECT club_id, member_count FROM Clubs WHERE club_id = 'ZEPHYR';

-- ----- STEP 5E: RESTORE BASE TABLE STATE -----
UPDATE Memberships SET status = 'Active' WHERE membership_id = 'ZEPHYR-0063';
UPDATE Clubs SET member_count = member_count + 1 WHERE club_id = 'ZEPHYR';



-- ======================================================================================
-- CURSOR 6: sp_award_active_contributors
-- WHO USES IT: Executive Committee & Club Presidents.
-- WHY: Merit-Based Promotion: Evaluates campus event attendance. If a regular 'Member'
--      attends >= p_min_attended events, they earn promotion to 'Core Member'.
--      Also intelligently flags non-members and members with insufficient attendance.
-- PARAMETERS: p_student_id (specific student or 'ALL'), p_min_attended (e.g. 3), p_apply (0/1)
-- COMPLEXITY: O(S_att) where S_att is students who attended events.
-- ======================================================================================

DROP PROCEDURE IF EXISTS sp_award_active_contributors;

DELIMITER $$
CREATE PROCEDURE sp_award_active_contributors(
    IN p_student_id   VARCHAR(20),
    IN p_min_attended INT,
    IN p_apply        TINYINT
)
BEGIN
    DECLARE v_done         INT DEFAULT 0;
    DECLARE v_sid          VARCHAR(20);
    DECLARE v_sname        VARCHAR(100);
    DECLARE v_attended     INT;
    DECLARE v_is_member    INT;
    DECLARE v_mid          VARCHAR(30);
    DECLARE v_cid          VARCHAR(20);
    DECLARE v_current_role VARCHAR(30);
    DECLARE v_new_role     VARCHAR(30);
    DECLARE v_action       VARCHAR(50);

    DECLARE cur_students CURSOR FOR
        SELECT s.student_id, s.name
        FROM Students s
        WHERE (p_student_id <> 'ALL' AND p_student_id IS NOT NULL AND s.student_id = p_student_id)
           OR ((p_student_id = 'ALL' OR p_student_id IS NULL) AND EXISTS (
               SELECT 1 FROM EventRegistrations er 
               WHERE er.student_id = s.student_id AND er.attendance_status = 'Attended'
           ))
        ORDER BY s.student_id;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

    DROP TEMPORARY TABLE IF EXISTS tmp_promotion_results;
    CREATE TEMPORARY TABLE tmp_promotion_results (
        student_id        VARCHAR(20),
        student_name      VARCHAR(100),
        club_id           VARCHAR(20),
        events_attended   INT,
        current_role      VARCHAR(30),
        new_role          VARCHAR(30),
        evaluation_result VARCHAR(50)
    );

    OPEN cur_students;
    eval_loop: LOOP
        FETCH cur_students INTO v_sid, v_sname;
        IF v_done = 1 THEN
            LEAVE eval_loop;
        END IF;

        SELECT COUNT(*) INTO v_attended
        FROM EventRegistrations
        WHERE student_id = v_sid AND attendance_status = 'Attended';

        SELECT COUNT(*) INTO v_is_member
        FROM Memberships
        WHERE student_id = v_sid;

        IF v_is_member = 0 THEN
            SET v_cid = 'None';
            SET v_current_role = 'Non-Member';
            SET v_new_role = 'Non-Member';
            SET v_action = 'NON-MEMBER (CANNOT PROMOTE)';
        ELSE
            SELECT membership_id, club_id, role 
            INTO v_mid, v_cid, v_current_role
            FROM Memberships
            WHERE student_id = v_sid
            ORDER BY (status = 'Active') DESC, membership_id ASC
            LIMIT 1;

            IF v_current_role = 'Member' AND v_attended >= p_min_attended THEN
                SET v_new_role = 'Core Member';
                IF p_apply = 1 THEN
                    UPDATE Memberships 
                    SET role = 'Core Member' 
                    WHERE membership_id = v_mid;
                    SET v_action = 'PROMOTED TO CORE MEMBER';
                ELSE
                    SET v_action = 'ELIGIBLE FOR PROMOTION';
                END IF;
            ELSEIF v_current_role = 'Member' AND v_attended < p_min_attended THEN
                SET v_new_role = 'Member (Unchanged)';
                SET v_action = CONCAT('NOT ELIGIBLE (Needs >= ', p_min_attended, ')');
            ELSE
                SET v_new_role = v_current_role;
                SET v_action = 'ALREADY LEADER / CORE MEMBER';
            END IF;
        END IF;

        INSERT INTO tmp_promotion_results 
        VALUES (v_sid, v_sname, v_cid, v_attended, v_current_role, v_new_role, v_action);
    END LOOP;
    CLOSE cur_students;

    SELECT * FROM tmp_promotion_results;
    DROP TEMPORARY TABLE IF EXISTS tmp_promotion_results;
END$$
DELIMITER ;


-- ----- STEP 6A: CHECK BASE TABLE FOR CANDIDATES -----
SELECT s.student_id, s.name, 
       COALESCE(m.club_id, 'None') AS club, 
       COALESCE(m.role, 'Non-Member') AS current_role,
       (SELECT COUNT(*) FROM EventRegistrations er WHERE er.student_id = s.student_id AND er.attendance_status = 'Attended') AS attended_events
FROM Students s
LEFT JOIN Memberships m ON m.student_id = s.student_id
WHERE s.student_id IN ('CE25-0042', 'ELE25-0058', 'CE25-0314')
ORDER BY s.student_id;

-- ----- STEP 6B: RUN PROMOTION EVALUATION FOR ALL (PREVIEW MODE) -----
CALL sp_award_active_contributors('ALL', 3, 0);

-- ----- STEP 6C: EXECUTE MERIT PROMOTIONS IN BASE TABLE -----
CALL sp_award_active_contributors('ALL', 3, 1);

-- ----- STEP 6D: VERIFY DIRECT ROLE PROMOTION IN BASE MEMBERSHIPS TABLE -----
SELECT s.student_id, s.name, m.membership_id, m.club_id, m.role, m.status
FROM Students s
LEFT JOIN Memberships m ON m.student_id = s.student_id
WHERE s.student_id IN ('CE25-0042', 'ELE25-0058', 'CE25-0314');

-- ----- STEP 6E: RESTORE BASE TABLE STATE -----
UPDATE Memberships SET role = 'Member' WHERE membership_id = 'CSI-0042';


-- ----- STEP 6E: RESTORE BASE TABLE STATE -----
UPDATE Memberships SET role = 'Member' WHERE membership_id = 'CSI-0042';



-- ######################################################################################
-- # MEMBER 4 - CURSORS 7 & 8
-- # Academic Graduation Lifecycles & Student Feedback Privacy Protection
-- ######################################################################################

-- ======================================================================================
-- CURSOR 7: sp_senior_graduation_rollout
-- WHO USES IT: Academic Registrar & Student Affairs Dean.
-- WHY: End of Academic Session: Final-year students (year_of_study = 4) complete their degrees
--      and graduate. Graduating seniors cannot remain active student club members. The cursor
--      identifies all active memberships held by Year 4 students, sets status to 'Inactive'
--      (alumni transition), and decrements Clubs.member_count.
-- PARAMETERS: p_grad_year (e.g. 4), p_apply (0=preview, 1=update Memberships & Clubs)
-- COMPLEXITY: O(M_grad) where M_grad is graduating senior memberships.
-- ======================================================================================

DROP PROCEDURE IF EXISTS sp_senior_graduation_rollout;

DELIMITER $$
CREATE PROCEDURE sp_senior_graduation_rollout(
    IN p_grad_year TINYINT,
    IN p_apply     TINYINT
)
BEGIN
    DECLARE v_done    INT DEFAULT 0;
    DECLARE v_mid     VARCHAR(30);
    DECLARE v_sid     VARCHAR(20);
    DECLARE v_sname   VARCHAR(100);
    DECLARE v_cid     VARCHAR(20);
    DECLARE v_role    VARCHAR(30);
    DECLARE v_action  VARCHAR(30);

    -- Cursor over active memberships belonging to students of target year_of_study
    DECLARE cur_seniors CURSOR FOR
        SELECT m.membership_id, m.student_id, s.name, m.club_id, m.role
        FROM Memberships m
        JOIN Students s ON s.student_id = m.student_id
        WHERE s.year_of_study = p_grad_year AND m.status = 'Active'
        ORDER BY m.membership_id;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

    DROP TEMPORARY TABLE IF EXISTS tmp_grad_rollout;
    CREATE TEMPORARY TABLE tmp_grad_rollout (
        membership_id VARCHAR(30), student_id VARCHAR(20),
        student_name VARCHAR(100), club_id VARCHAR(20),
        role VARCHAR(30), transition_status VARCHAR(30)
    );

    OPEN cur_seniors;
    grad_loop: LOOP
        FETCH cur_seniors INTO v_mid, v_sid, v_sname, v_cid, v_role;
        IF v_done = 1 THEN
            LEAVE grad_loop;
        END IF;

        IF p_apply = 1 THEN
            -- Transition membership status to Inactive (Alumni) in base table
            UPDATE Memberships 
            SET status = 'Inactive' 
            WHERE membership_id = v_mid;

            -- Decrement member count in base Clubs table
            UPDATE Clubs 
            SET member_count = member_count - 1 
            WHERE club_id = v_cid;

            SET v_action = 'TRANSITIONED TO ALUMNI';
        ELSE
            SET v_action = 'ELIGIBLE FOR ALUMNI EXIT';
        END IF;

        INSERT INTO tmp_grad_rollout 
        VALUES (v_mid, v_sid, v_sname, v_cid, v_role, v_action);
    END LOOP;
    CLOSE cur_seniors;

    SELECT * FROM tmp_grad_rollout;
    DROP TEMPORARY TABLE IF EXISTS tmp_grad_rollout;
END$$
DELIMITER ;


-- ----- STEP 7A: CHECK BASE TABLES FOR YEAR 4 SENIORS -----
SELECT s.student_id, s.name, s.year_of_study, m.membership_id, m.club_id, m.status
FROM Students s
JOIN Memberships m ON m.student_id = s.student_id
WHERE s.year_of_study = 4;

-- ----- STEP 7B: RUN SENIOR GRADUATION AUDIT (PREVIEW MODE) -----
CALL sp_senior_graduation_rollout(4, 0);

-- ----- STEP 7C: EXECUTE GRADUATION ROLLOUT IN BASE TABLES -----
CALL sp_senior_graduation_rollout(4, 1);

-- ----- STEP 7D: VERIFY DIRECT UPDATES IN BASE MEMBERSHIPS TABLE -----
-- All Year 4 senior memberships are now marked 'Inactive':
SELECT s.student_id, s.name, s.year_of_study, m.membership_id, m.club_id, m.status
FROM Students s
JOIN Memberships m ON m.student_id = s.student_id
WHERE s.year_of_study = 4;

-- ----- STEP 7E: RESTORE BASE TABLE STATE -----
UPDATE Memberships SET status = 'Active' WHERE membership_id IN ('CSI-0021', 'EDC-0035', 'SWD-0014');
UPDATE Clubs SET member_count = (SELECT COUNT(*) FROM Memberships m WHERE m.club_id = Clubs.club_id AND m.status = 'Active');



-- ======================================================================================
-- CURSOR 8: sp_anonymize_sensitive_feedback
-- WHO USES IT: Grievance Redressal Committee & Student Ombudsman.
-- WHY: Student Protection Policy: Candid critical feedback (rating <= p_low_rating_threshold)
--      exposes junior students to potential backlash or pressure. This cursor identifies
--      all critical reviews, anonymizes and standardizes them with the institutional
--      tag '[PROTECTED ANONYMOUS REVIEW]: ...' directly in the base Feedback table.
-- PARAMETERS: p_low_rating_threshold (e.g. 2), p_apply (0=preview, 1=update Feedback table)
-- COMPLEXITY: O(F_crit) where F_crit is critical feedback records, with string formatting.
-- ======================================================================================

DROP PROCEDURE IF EXISTS sp_anonymize_sensitive_feedback;

DELIMITER $$
CREATE PROCEDURE sp_anonymize_sensitive_feedback(
    IN p_low_rating_threshold INT,
    IN p_apply                TINYINT
)
BEGIN
    DECLARE v_done      INT DEFAULT 0;
    DECLARE v_fid       VARCHAR(30);
    DECLARE v_sid       VARCHAR(20);
    DECLARE v_ftype     VARCHAR(10);
    DECLARE v_rating    INT;
    DECLARE v_comments  TEXT;
    DECLARE v_protected TEXT;
    DECLARE v_action    VARCHAR(30);

    -- Cursor over critical feedback not yet anonymized
    DECLARE cur_feedback CURSOR FOR
        SELECT feedback_id, student_id, feedback_type, rating, comments
        FROM Feedback
        WHERE rating <= p_low_rating_threshold 
          AND (comments NOT LIKE '[PROTECTED ANONYMOUS REVIEW]%' OR comments IS NULL)
        ORDER BY feedback_id;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

    DROP TEMPORARY TABLE IF EXISTS tmp_feedback_privacy;
    CREATE TEMPORARY TABLE tmp_feedback_privacy (
        feedback_id VARCHAR(30), student_id VARCHAR(20),
        feedback_type VARCHAR(10), rating INT,
        original_comment TEXT, protected_comment TEXT,
        action_taken VARCHAR(30)
    );

    OPEN cur_feedback;
    feedback_loop: LOOP
        FETCH cur_feedback INTO v_fid, v_sid, v_ftype, v_rating, v_comments;
        IF v_done = 1 THEN
            LEAVE feedback_loop;
        END IF;

        SET v_protected = CONCAT('[PROTECTED ANONYMOUS REVIEW]: ', COALESCE(v_comments, 'No descriptive text provided.'));

        IF p_apply = 1 THEN
            UPDATE Feedback 
            SET comments = v_protected 
            WHERE feedback_id = v_fid;
            SET v_action = 'COMMENT ANONYMIZED';
        ELSE
            SET v_action = 'FLAGGED FOR PROTECTION';
        END IF;

        INSERT INTO tmp_feedback_privacy 
        VALUES (v_fid, v_sid, v_ftype, v_rating, v_comments, v_protected, v_action);
    END LOOP;
    CLOSE cur_feedback;

    SELECT * FROM tmp_feedback_privacy;
    DROP TEMPORARY TABLE IF EXISTS tmp_feedback_privacy;
END$$
DELIMITER ;


-- ----- STEP 8A: CHECK BASE FEEDBACK TABLE FOR LOW RATINGS -----
-- Rows with rating <= 2 (CF26-LOW1, CF26-LOW2, EF26-LOW1, EF26-LOW2)
SELECT feedback_id, student_id, feedback_type, rating, comments FROM Feedback WHERE rating <= 2;

-- ----- STEP 8B: RUN ANONYMIZATION AUDIT (PREVIEW MODE) -----
CALL sp_anonymize_sensitive_feedback(2, 0);

-- ----- STEP 8C: APPLY ANONYMIZATION TO BASE FEEDBACK TABLE -----
CALL sp_anonymize_sensitive_feedback(2, 1);

-- ----- STEP 8D: VERIFY DIRECT COMMENT PROTECTION IN BASE FEEDBACK TABLE -----
-- Comments in the original Feedback table now carry the [PROTECTED ANONYMOUS REVIEW] tag!
SELECT feedback_id, student_id, feedback_type, rating, comments FROM Feedback WHERE rating <= 2;

-- ----- STEP 8E: RESTORE ORIGINAL COMMENTS (CLEANUP) -----
UPDATE Feedback SET comments = 'Core committee meetings frequently get rescheduled at the last minute without prior notice.' WHERE feedback_id = 'CF26-LOW1';
UPDATE Feedback SET comments = 'Dance rehearsal hall timings clash severely with regular department laboratory schedules.' WHERE feedback_id = 'CF26-LOW2';
UPDATE Feedback SET comments = 'Long waiting queues at the medical station and drinking water ran out early.' WHERE feedback_id = 'EF26-LOW1';
UPDATE Feedback SET comments = 'Air conditioning in the conference room was malfunctioning during the tech seminar.' WHERE feedback_id = 'EF26-LOW2';


-- ======================================================================================
-- SUMMARY VERIFICATION: CONFIRM ONLY THE 8 CANONICAL TABLES EXIST
-- ======================================================================================
SHOW TABLES;
