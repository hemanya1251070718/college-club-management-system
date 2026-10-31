-- ======================================================================================
-- 8 PRODUCTION STORED PROCEDURES & CURSORS
-- Database: trial_club (College Club Management System)
-- ======================================================================================

USE trial_club;

-- --------------------------------------------------------------------------------------
-- PROCEDURE 1: sp_audit_club_counts
-- Purpose: Audits and reconciles denormalized Clubs.member_count against Memberships
-- Parameters: p_fix (0 = Preview only, 1 = Update Clubs table directly)
-- --------------------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_audit_club_counts;

DELIMITER $$
CREATE PROCEDURE sp_audit_club_counts(IN p_fix TINYINT)
BEGIN
    DECLARE v_done   INT DEFAULT 0;
    DECLARE v_club   VARCHAR(20);
    DECLARE v_stored INT;
    DECLARE v_actual INT;
    DECLARE v_result VARCHAR(20);

    DECLARE cur_clubs CURSOR FOR
        SELECT club_id, member_count FROM Clubs ORDER BY club_id;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

    DROP TEMPORARY TABLE IF EXISTS tmp_audit;
    CREATE TEMPORARY TABLE tmp_audit (
        club_id VARCHAR(20),
        stored_count INT,
        actual_count INT,
        result VARCHAR(20)
    );

    OPEN cur_clubs;
    read_loop: LOOP
        FETCH cur_clubs INTO v_club, v_stored;
        IF v_done = 1 THEN
            LEAVE read_loop;
        END IF;

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


-- --------------------------------------------------------------------------------------
-- PROCEDURE 2: sp_recruitment_leads_and_auto_invite
-- Purpose: Identifies non-members actively participating in events and auto-enrolls them
-- Parameters: p_min_events (threshold), p_auto_invite (0 = Preview, 1 = Auto-enroll)
-- --------------------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_recruitment_leads_and_auto_invite;

DELIMITER $$
CREATE PROCEDURE sp_recruitment_leads_and_auto_invite(
    IN p_min_events INT,
    IN p_auto_invite TINYINT
)
BEGIN
    DECLARE v_done         INT DEFAULT 0;
    DECLARE v_sid          VARCHAR(20);
    DECLARE v_name         VARCHAR(100);
    DECLARE v_events       INT;
    DECLARE v_target_cid   VARCHAR(20);
    DECLARE v_target_cname VARCHAR(100);
    DECLARE v_action       VARCHAR(30);

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
        student_id VARCHAR(20),
        student_name VARCHAR(100),
        events_joined INT,
        suggested_club_id VARCHAR(20),
        suggested_club_name VARCHAR(100),
        action_taken VARCHAR(30)
    );

    OPEN cur_leads;
    lead_loop: LOOP
        FETCH cur_leads INTO v_sid, v_name, v_events;
        IF v_done = 1 THEN
            LEAVE lead_loop;
        END IF;

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
            INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
            VALUES (CONCAT('AUTO-', v_sid), v_sid, v_target_cid, 'Volunteer', CURRENT_DATE, 'Active')
            ON DUPLICATE KEY UPDATE status = 'Active';

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


-- --------------------------------------------------------------------------------------
-- PROCEDURE 3: sp_reconcile_event_budgets
-- Purpose: Evaluates feedback ratings on completed events and awards performance bonus budgets
-- Parameters: p_min_rating (threshold), p_bonus_pct (e.g. 10.0), p_apply (0=Preview, 1=Apply)
-- --------------------------------------------------------------------------------------
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

    DECLARE cur_events CURSOR FOR
        SELECT event_id, event_name, budget_allocated 
        FROM Events 
        WHERE status = 'Completed' 
        ORDER BY event_id;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

    DROP TEMPORARY TABLE IF EXISTS tmp_budget_recon;
    CREATE TEMPORARY TABLE tmp_budget_recon (
        event_id VARCHAR(30),
        event_name VARCHAR(150),
        avg_rating DECIMAL(3,2),
        old_budget DECIMAL(10,2),
        bonus_applied DECIMAL(10,2),
        new_budget DECIMAL(10,2),
        action_status VARCHAR(30)
    );

    OPEN cur_events;
    event_loop: LOOP
        FETCH cur_events INTO v_eid, v_ename, v_old_budget;
        IF v_done = 1 THEN
            LEAVE event_loop;
        END IF;

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


-- --------------------------------------------------------------------------------------
-- PROCEDURE 4: sp_close_past_events
-- Purpose: Automatically reconciles past scheduled events (event_date < cutoff) to Completed or Cancelled
-- Parameters: p_cutoff_date, p_apply (0=Preview, 1=Apply)
-- --------------------------------------------------------------------------------------
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

    DECLARE cur_past_events CURSOR FOR
        SELECT event_id, event_name, event_date
        FROM Events
        WHERE status = 'Planned' AND event_date < p_cutoff_date
        ORDER BY event_date;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

    DROP TEMPORARY TABLE IF EXISTS tmp_event_closure;
    CREATE TEMPORARY TABLE tmp_event_closure (
        event_id VARCHAR(30),
        event_name VARCHAR(150),
        event_date DATE,
        attendees_count INT,
        resolved_status VARCHAR(20),
        action_taken VARCHAR(30)
    );

    OPEN cur_past_events;
    close_loop: LOOP
        FETCH cur_past_events INTO v_eid, v_ename, v_edate;
        IF v_done = 1 THEN
            LEAVE close_loop;
        END IF;

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


-- --------------------------------------------------------------------------------------
-- PROCEDURE 5: sp_deactivate_inactive_members
-- Purpose: Identifies active members who missed >= p_max_missed_events and marks them Inactive
-- Parameters: p_max_missed_events, p_apply (0=Preview, 1=Apply)
-- --------------------------------------------------------------------------------------
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

    DECLARE cur_active_members CURSOR FOR
        SELECT m.membership_id, m.student_id, m.club_id, s.name
        FROM Memberships m
        JOIN Students s ON s.student_id = m.student_id
        WHERE m.status = 'Active' AND m.role IN ('Member', 'Volunteer')
        ORDER BY m.membership_id;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

    DROP TEMPORARY TABLE IF EXISTS tmp_absentee_audit;
    CREATE TEMPORARY TABLE tmp_absentee_audit (
        membership_id VARCHAR(30),
        student_id VARCHAR(20),
        student_name VARCHAR(100),
        club_id VARCHAR(20),
        missed_events INT,
        action_taken VARCHAR(30)
    );

    OPEN cur_active_members;
    member_loop: LOOP
        FETCH cur_active_members INTO v_mid, v_sid, v_cid, v_sname;
        IF v_done = 1 THEN
            LEAVE member_loop;
        END IF;

        SELECT COUNT(*) INTO v_missed_count
        FROM EventRegistrations er
        JOIN Events e ON e.event_id = er.event_id
        WHERE er.student_id = v_sid 
          AND e.club_id = v_cid
          AND er.attendance_status = 'Registered';

        IF v_missed_count >= p_max_missed_events THEN
            IF p_apply = 1 THEN
                UPDATE Memberships 
                SET status = 'Inactive' 
                WHERE membership_id = v_mid;

                UPDATE Clubs 
                SET member_count = GREATEST(0, member_count - 1) 
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


-- --------------------------------------------------------------------------------------
-- PROCEDURE 6: sp_award_active_contributors
-- Purpose: Evaluates member event attendance and promotes qualifying members to 'Core Member'
-- Parameters: p_student_id ('ALL' or specific student_id), p_min_attended, p_apply (0/1)
-- --------------------------------------------------------------------------------------
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


-- --------------------------------------------------------------------------------------
-- PROCEDURE 7: sp_senior_graduation_rollout
-- Purpose: Transitions graduating seniors (year_of_study = 4) to Inactive Alumni status
-- Parameters: p_grad_year (e.g. 4), p_apply (0=Preview, 1=Apply)
-- --------------------------------------------------------------------------------------
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

    DECLARE cur_seniors CURSOR FOR
        SELECT m.membership_id, m.student_id, s.name, m.club_id, m.role
        FROM Memberships m
        JOIN Students s ON s.student_id = m.student_id
        WHERE s.year_of_study = p_grad_year AND m.status = 'Active'
        ORDER BY m.membership_id;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

    DROP TEMPORARY TABLE IF EXISTS tmp_grad_rollout;
    CREATE TEMPORARY TABLE tmp_grad_rollout (
        membership_id VARCHAR(30),
        student_id VARCHAR(20),
        student_name VARCHAR(100),
        club_id VARCHAR(20),
        role VARCHAR(30),
        transition_status VARCHAR(30)
    );

    OPEN cur_seniors;
    grad_loop: LOOP
        FETCH cur_seniors INTO v_mid, v_sid, v_sname, v_cid, v_role;
        IF v_done = 1 THEN
            LEAVE grad_loop;
        END IF;

        IF p_apply = 1 THEN
            UPDATE Memberships 
            SET status = 'Inactive' 
            WHERE membership_id = v_mid;

            UPDATE Clubs 
            SET member_count = GREATEST(0, member_count - 1) 
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


-- --------------------------------------------------------------------------------------
-- PROCEDURE 8: sp_anonymize_sensitive_feedback
-- Purpose: Anonymizes and tags critical reviews (rating <= threshold) to protect student privacy
-- Parameters: p_low_rating_threshold (e.g. 2), p_apply (0=Preview, 1=Apply)
-- --------------------------------------------------------------------------------------
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

    DECLARE cur_feedback CURSOR FOR
        SELECT feedback_id, student_id, feedback_type, rating, comments
        FROM Feedback
        WHERE rating <= p_low_rating_threshold 
          AND (comments NOT LIKE '[PROTECTED ANONYMOUS REVIEW]%' OR comments IS NULL)
        ORDER BY feedback_id;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

    DROP TEMPORARY TABLE IF EXISTS tmp_feedback_privacy;
    CREATE TEMPORARY TABLE tmp_feedback_privacy (
        feedback_id VARCHAR(30),
        student_id VARCHAR(20),
        feedback_type VARCHAR(10),
        rating INT,
        original_comment TEXT,
        protected_comment TEXT,
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
