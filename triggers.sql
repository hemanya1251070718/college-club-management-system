-- ======================================================================================
-- 8 PRODUCTION DATABASE TRIGGERS
-- Database: trial_club (College Club Management System)
-- ======================================================================================

USE trial_club;

-- Cleanup any legacy triggers
DROP TRIGGER IF EXISTS trg_increase_member_count;
DROP TRIGGER IF EXISTS trg_decrease_member_count;
DROP TRIGGER IF EXISTS trg_update_member_count;
DROP TRIGGER IF EXISTS increase_member_count;

-- --------------------------------------------------------------------------------------
-- TRIGGER 1: trg_after_membership_insert_sync_count
-- Syncs Clubs.member_count on active member registration
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
-- TRIGGER 2: trg_after_membership_delete_sync_count
-- Syncs Clubs.member_count on active member departure
-- --------------------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_after_membership_delete_sync_count;

DELIMITER $$
CREATE TRIGGER trg_after_membership_delete_sync_count
AFTER DELETE ON Memberships
FOR EACH ROW
BEGIN
    IF OLD.status = 'Active' THEN
        UPDATE Clubs
        SET member_count = GREATEST(0, member_count - 1)
        WHERE club_id = OLD.club_id;
    END IF;
END$$
DELIMITER ;


-- --------------------------------------------------------------------------------------
-- TRIGGER 3: trg_prevent_multiple_presidents
-- Enforces VIT Club Bylaws: exactly ONE active President per club
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


-- --------------------------------------------------------------------------------------
-- TRIGGER 4: trg_adjust_member_count_on_status_change
-- Dynamically adjusts Clubs.member_count on Active <-> Inactive transitions
-- --------------------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_adjust_member_count_on_status_change;

DELIMITER $$
CREATE TRIGGER trg_adjust_member_count_on_status_change
AFTER UPDATE ON Memberships
FOR EACH ROW
BEGIN
    -- Active -> Inactive : decrement count
    IF OLD.status = 'Active' AND NEW.status = 'Inactive' THEN
        UPDATE Clubs
        SET member_count = GREATEST(0, member_count - 1)
        WHERE club_id = NEW.club_id;
    -- Inactive -> Active : increment count
    ELSEIF OLD.status = 'Inactive' AND NEW.status = 'Active' THEN
        UPDATE Clubs
        SET member_count = member_count + 1
        WHERE club_id = NEW.club_id;
    END IF;
END$$
DELIMITER ;


-- --------------------------------------------------------------------------------------
-- TRIGGER 5: trg_prevent_registration_for_completed_event
-- Prevents retrospective registrations on completed or cancelled events
-- --------------------------------------------------------------------------------------
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


-- --------------------------------------------------------------------------------------
-- TRIGGER 6: trg_verify_feedback_registration
-- Authenticity assurance: verifies event registration before accepting event feedback
-- --------------------------------------------------------------------------------------
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


-- --------------------------------------------------------------------------------------
-- TRIGGER 7: trg_auto_progress_event_on_attendance
-- Automatically progresses event status from 'Planned' to 'Ongoing' upon first attendance
-- --------------------------------------------------------------------------------------
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


-- --------------------------------------------------------------------------------------
-- TRIGGER 8: trg_auto_create_club_profile
-- Zero-config provisioning: automatically generates profile with institutional email & handle
-- --------------------------------------------------------------------------------------
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
