-- ===========================================================
-- TRIGGERS FOR MEMBER COUNT SYNCHRONIZATION
-- Database: trial_club
-- These triggers keep Clubs.member_count accurate whenever
-- Memberships rows are added, removed, or transferred.
-- ===========================================================

USE trial_club;

DROP TRIGGER IF EXISTS trg_increase_member_count;
DROP TRIGGER IF EXISTS trg_decrease_member_count;
DROP TRIGGER IF EXISTS trg_update_member_count;

DELIMITER $$

-- 1. Increase member count after new membership is inserted
CREATE TRIGGER trg_increase_member_count
AFTER INSERT ON Memberships
FOR EACH ROW
BEGIN
    UPDATE Clubs
    SET member_count = member_count + 1
    WHERE club_id = NEW.club_id;
END$$

-- 2. Decrease member count after a membership is deleted
CREATE TRIGGER trg_decrease_member_count
AFTER DELETE ON Memberships
FOR EACH ROW
BEGIN
    UPDATE Clubs
    SET member_count = GREATEST(0, member_count - 1)
    WHERE club_id = OLD.club_id;
END$$

-- 3. Update member counts if a membership row moves across clubs
CREATE TRIGGER trg_update_member_count
AFTER UPDATE ON Memberships
FOR EACH ROW
BEGIN
    IF OLD.club_id <> NEW.club_id THEN
        UPDATE Clubs SET member_count = GREATEST(0, member_count - 1) WHERE club_id = OLD.club_id;
        UPDATE Clubs SET member_count = member_count + 1 WHERE club_id = NEW.club_id;
    END IF;
END$$

DELIMITER ;
