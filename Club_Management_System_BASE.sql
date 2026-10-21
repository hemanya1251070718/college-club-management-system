-- ===========================================================
-- Club Management System  -  BASE SCRIPT (no triggers, no demos)
-- DBMS Mini Project  |  Database: MySQL 8.x  |  Schema: trial_club
--
-- Run the WHOLE file (Ctrl+Shift+Enter). It rebuilds everything and shows
-- ONLY the 8 original tables, in this order:
--   Students, FacultyCoordinators, Clubs, ClubProfile, Memberships,
--   Events, EventRegistrations, Feedback
-- Safe to run again and again (it drops and rebuilds everything).
-- The trigger demo is in the separate file: Trigger_Demo_Steps.sql
-- ===========================================================


-- ===========================================================
-- SETUP
-- ===========================================================

-- Harmless reset: throws away any half-finished demo transaction.
ROLLBACK;
SET autocommit = 1;

-- ===========================================================
-- DATABASE
-- ===========================================================

CREATE DATABASE IF NOT EXISTS trial_club;
USE trial_club;


-- ===========================================================
-- DROP EXISTING TABLES / OBJECTS
-- ===========================================================

DROP TABLE IF EXISTS Feedback;
DROP TABLE IF EXISTS EventRegistrations;
DROP TABLE IF EXISTS Events;
DROP TABLE IF EXISTS Memberships;
DROP TABLE IF EXISTS ClubProfile;
DROP TABLE IF EXISTS Clubs;
DROP TABLE IF EXISTS FacultyCoordinators;
DROP TABLE IF EXISTS Students;

DROP VIEW IF EXISTS ClubSummary;
DROP PROCEDURE IF EXISTS GetStudentClubs;
DROP TRIGGER IF EXISTS trg_increase_member_count;
DROP TRIGGER IF EXISTS trg_decrease_member_count;
DROP TRIGGER IF EXISTS trg_update_member_count;
DROP TRIGGER IF EXISTS increase_member_count;


-- ===========================================================
-- 1. STUDENTS TABLE
-- ===========================================================

CREATE TABLE Students (
    student_id    VARCHAR(20) PRIMARY KEY,
    prn_number    VARCHAR(20) NOT NULL UNIQUE,
    name          VARCHAR(100) NOT NULL,
    email         VARCHAR(100) NOT NULL UNIQUE,
    phone         VARCHAR(15),
    dept_id       VARCHAR(10) NOT NULL,
    dept_name     VARCHAR(100) NOT NULL,
    year_of_study TINYINT NOT NULL
) ENGINE=InnoDB;


-- ===========================================================
-- 2. FACULTY COORDINATORS TABLE
-- ===========================================================

CREATE TABLE FacultyCoordinators (
    faculty_id    VARCHAR(20) PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    email         VARCHAR(100) NOT NULL UNIQUE,
    phone         VARCHAR(15),
    dept_id       VARCHAR(10) NOT NULL,
    dept_name     VARCHAR(100) NOT NULL
) ENGINE=InnoDB;


-- ===========================================================
-- 3. CLUBS TABLE
-- ===========================================================

CREATE TABLE Clubs (
    club_id       VARCHAR(20) PRIMARY KEY,
    club_name     VARCHAR(100) NOT NULL UNIQUE,
    category      VARCHAR(50) NOT NULL,
    faculty_id    VARCHAR(20) NOT NULL,
    description   TEXT,
    member_count  INT DEFAULT 0,

    FOREIGN KEY (faculty_id)
        REFERENCES FacultyCoordinators(faculty_id)
) ENGINE=InnoDB;


-- ===========================================================
-- 4. CLUB PROFILE TABLE
-- ===========================================================

CREATE TABLE ClubProfile (
    club_id           VARCHAR(20) PRIMARY KEY,
    official_email    VARCHAR(100),
    instagram_handle  VARCHAR(50),

    FOREIGN KEY (club_id)
        REFERENCES Clubs(club_id)
) ENGINE=InnoDB;


-- ===========================================================
-- 5. MEMBERSHIPS TABLE
-- Every row here = a real club member. The role column only
-- classifies WHICH KIND of member they are (President, Secretary,
-- Treasurer, Event Coordinator, Core Member, Volunteer, or plain
-- Member) — it never means "not a member." A student with NO row
-- in this table at all is the only true non-member.
-- ===========================================================

CREATE TABLE Memberships (
    membership_id VARCHAR(30) PRIMARY KEY,
    student_id    VARCHAR(20) NOT NULL,
    club_id       VARCHAR(20) NOT NULL,
    role          VARCHAR(30) NOT NULL DEFAULT 'Member',
    join_date     DATE,
    status        VARCHAR(20) DEFAULT 'Active',

    UNIQUE (student_id, club_id),

    FOREIGN KEY (student_id)
        REFERENCES Students(student_id),

    FOREIGN KEY (club_id)
        REFERENCES Clubs(club_id),

    CHECK (role IN ('President','Secretary','Treasurer','Event Coordinator','Core Member','Volunteer','Member'))
) ENGINE=InnoDB;


-- ===========================================================
-- 6. EVENTS TABLE
-- ===========================================================

CREATE TABLE Events (
    event_id          VARCHAR(30) PRIMARY KEY,
    club_id           VARCHAR(20) NOT NULL,
    event_name        VARCHAR(150) NOT NULL,
    event_date        DATE,
    venue             VARCHAR(100),
    budget_allocated  DECIMAL(10,2) DEFAULT 0,
    event_type        VARCHAR(30),
    status            VARCHAR(20) DEFAULT 'Planned',
    is_award_winning  BOOLEAN DEFAULT FALSE,
    award_title       VARCHAR(150),
    award_level       VARCHAR(30),

    FOREIGN KEY (club_id)
        REFERENCES Clubs(club_id)
) ENGINE=InnoDB;


-- ===========================================================
-- 7. EVENT REGISTRATIONS TABLE
-- Note: a student can appear here WITHOUT ever appearing in
-- Memberships — that's exactly how a non-member attending an
-- event is represented (see the BONUS CHECK query at the bottom).
-- ===========================================================

CREATE TABLE EventRegistrations (
    registration_id   VARCHAR(30) PRIMARY KEY,
    event_id          VARCHAR(30) NOT NULL,
    student_id        VARCHAR(20) NOT NULL,
    registration_date DATE,
    attendance_status VARCHAR(20) DEFAULT 'Registered',

    UNIQUE (event_id, student_id),

    FOREIGN KEY (event_id)
        REFERENCES Events(event_id),

    FOREIGN KEY (student_id)
        REFERENCES Students(student_id)
) ENGINE=InnoDB;


-- ===========================================================
-- 8. FEEDBACK TABLE
-- Supports BOTH Club Feedback and Event Feedback
-- ===========================================================

CREATE TABLE Feedback (
    feedback_id   VARCHAR(30) PRIMARY KEY,
    student_id    VARCHAR(20) NOT NULL,
    club_id       VARCHAR(20),
    event_id      VARCHAR(30),
    feedback_type VARCHAR(10) NOT NULL,
    rating        INT NOT NULL,
    comments      TEXT,
    feedback_date DATE,

    FOREIGN KEY (student_id)
        REFERENCES Students(student_id),

    FOREIGN KEY (club_id)
        REFERENCES Clubs(club_id),

    FOREIGN KEY (event_id)
        REFERENCES Events(event_id),

    CHECK (feedback_type IN ('Club', 'Event')),

    CHECK (rating BETWEEN 1 AND 5),

    CHECK (
        (feedback_type = 'Club'
         AND club_id IS NOT NULL
         AND event_id IS NULL)
        OR
        (feedback_type = 'Event'
         AND event_id IS NOT NULL
         AND club_id IS NULL)
    )
) ENGINE=InnoDB;




-- ===========================================================
-- STORED PROCEDURE
-- ===========================================================

DELIMITER $$

CREATE PROCEDURE GetStudentClubs(IN p_student_id VARCHAR(20))
BEGIN
    SELECT
        c.club_name,
        c.category,
        m.role,
        m.join_date
    FROM Memberships m
    JOIN Clubs c ON m.club_id = c.club_id
    WHERE m.student_id = p_student_id;
END$$

DELIMITER ;


-- ===========================================================
-- VIEW
-- ===========================================================

CREATE VIEW ClubSummary AS
SELECT
    c.club_id,
    c.club_name,
    c.category,
    c.member_count,
    f.name AS faculty_coordinator
FROM Clubs c
JOIN FacultyCoordinators f ON c.faculty_id = f.faculty_id;


-- ===========================================================
-- SAMPLE DATA
-- ===========================================================


-- ===========================================================
-- STUDENTS (all 69 — includes both club members AND non-members)
-- ===========================================================

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('ME25-0898', '1251070898', 'Kachave Aditya', 'aditya.1251070898@vit.edu', '7066443949', 'ME', 'Mechanical Engineering', 3);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0870', '1251070870', 'Jiya Bhandari', 'jiya.1251070870@vit.edu', '9833833682', 'CE', 'Computer Engineering', 1);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-1008', '1251071008', 'Shivani Hiremath', 'shivani.1251071008@vit.edu', '8668636030', 'CE', 'Computer Engineering', 1);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0230', '1251070230', 'Mayur Hiralal Kaithwas', 'mayur.1251070230@vit.edu', '9175203369', 'CE', 'Computer Engineering', 3);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0125', '1251070125', 'Achala Vaibhav Hon', 'achala.1251070125@vit.edu', '9270310970', 'CE', 'Computer Engineering', 2);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0193', '1251070193', 'Rani Popat Jagtap', 'rani.1251070193@vit.edu', '8830233304', 'CE', 'Computer Engineering', 1);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0314', '1251070314', 'Kanchan Navnath Jogdand', 'kanchan.1251070314@vit.edu', '7796500350', 'CE', 'Computer Engineering', 1);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('EE25-0191', '1251070191', 'Hrushikesh Sanjay Patil', 'hrushikesh.1251070191@vit.edu', '9373709234', 'EE', 'Electronics Engineering', 1);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-1062', '1251071062', 'Ujjwal sanjay jain', 'ujjwal.1251071062@vit.edu', '9325533633', 'CE', 'Computer Engineering', 3);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0573', '1251070573', 'Rohit Jadhav', 'rohit.1251070573@vit.edu', '8788074740', 'CE', 'Computer Engineering', 1);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('EE25-0348', '1251070348', 'Jyotiraditya Mahendra Pawar', 'jyotiraditya.1251070348@vit.edu', '9404502074', 'EE', 'Electronics Engineering', 3);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('ME25-1059', '1251071059', 'Soham Jadhav', 'soham.1251071059@vit.edu', '8010281574', 'ME', 'Mechanical Engineering', 3);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0203', '1251070203', 'Kadam Pragati Balaji', 'pragati.1251070203@vit.edu', '8669913782', 'CE', 'Computer Engineering', 3);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('ELE25-0575', '1251070575', 'Kale Aditya Nitin', 'aditya.1251070575@vit.edu', '8421018893', 'ELE', 'Electrical Engineering', 1);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0277', '1251070277', 'Ishan Shailendra Sahu', 'ishan.1251070277@vit.edu', '7498446313', 'CE', 'Computer Engineering', 3);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0165', '1251070165', 'Shreehari Sudarshan Joshi', 'shreehari.1251070165@vit.edu', '7774087227', 'CE', 'Computer Engineering', 2);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0784', '1251070784', 'Jaimin Vipul Chudasama', 'jaimin.1251070784@vit.edu', '8591850146', 'CE', 'Computer Engineering', 1);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('ME25-0867', '1251070867', 'Ayush Jha', 'ayush.1251070867@vit.edu', '9370269310', 'ME', 'Mechanical Engineering', 1);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('ELE25-0416', '1251070416', 'Kale Suraj Ganesh', 'suraj.1251070416@vit.edu', '9595443411', 'ELE', 'Electrical Engineering', 1);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0826', '1251070826', 'Soham Jadhav', 'soham.1251070826@vit.edu', '8767256732', 'CE', 'Computer Engineering', 1);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('ELE25-0666', '1251070666', 'Isha Anil Kulkarni', 'isha.1251070666@vit.edu', '7558689744', 'ELE', 'Electrical Engineering', 1);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0323', '1251070323', 'Iliyas Ismail Bhesti', 'iliyas.1251070323@vit.edu', NULL, 'CE', 'Computer Engineering', 3);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-1032', '1251071032', 'Shivam Mahesh Jagtap', 'shivam.1251071032@vit.edu', '8432586261', 'CE', 'Computer Engineering', 3);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0692', '1251070692', 'Swara Hase', 'swara.1251070692@vit.edu', '9822290259', 'CE', 'Computer Engineering', 1);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0815', '1251070815', 'Shravani Ganesh Kakad', 'shravani.1251070815@vit.edu', '7972682889', 'CE', 'Computer Engineering', 3);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('ME25-0885', '1251070885', 'Ishita Srivastava', 'ishita.1251070885@vit.edu', '9156111131', 'ME', 'Mechanical Engineering', 1);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0855', '1251070855', 'Harsh', 'harsh.1251070855@vit.edu', '8360969037', 'CE', 'Computer Engineering', 3);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('ME25-0893', '1251070893', 'Harsh Agarwal', 'agarwal.1251070893@vit.edu', '9767429262', 'ME', 'Mechanical Engineering', 3);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0424', '1251070424', 'Sarthak Rajendra Jamdade', 'sarthak.1251070424@vit.edu', '8308621277', 'CE', 'Computer Engineering', 3);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0226', '1251070226', 'kadam Samruddhi Balwant', 'samruddhi.1251070226@vit.edu', '9699818684', 'CE', 'Computer Engineering', 3);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('EE25-0992', '1251070992', 'Shivjeet Jagdale', 'shivjeet.1251070992@vit.edu', '8010960231', 'EE', 'Electronics Engineering', 2);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0342', '1251070342', 'Shravani Sakharam Kale', 'shravani.1251070342@vit.edu', '7722081200', 'CE', 'Computer Engineering', 1);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0369', '1251070369', 'Hitaishi Bodele', 'hitaishi.1251070369@vit.edu', '9325724660', 'CE', 'Computer Engineering', 2);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('ELE25-0678', '1251070678', 'Vedant Vinod Jaiswal', 'vedant.1251070678@vit.edu', '9209906859', 'ELE', 'Electrical Engineering', 3);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0856', '1251070856', 'Ishwari Umesh Honrao', 'ishwari.1251070856@vit.edu', '8010234914', 'CE', 'Computer Engineering', 2);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-1055', '1251071055', 'Izyan Karim Lalani', 'izyan.1251071055@vit.edu', '9096634608', 'CE', 'Computer Engineering', 1);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0431', '1251070431', 'Jadhav Vivek Govind', 'vivek.1251070431@vit.edu', '9420113130', 'CE', 'Computer Engineering', 1);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('EE25-1039', '1251071039', 'Shubham kale', 'shubham.1251071039@vit.edu', '9284623523', 'EE', 'Electronics Engineering', 3);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0185', '1251070185', 'Kadam Sharad Shankar', 'sharad.1251070185@vit.edu', '7559262124', 'CE', 'Computer Engineering', 2);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('ME25-0187', '1251070187', 'Jyuthika Babaso Herwade', 'jyuthika.1251070187@vit.edu', '8308429248', 'ME', 'Mechanical Engineering', 2);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-1029', '1251071029', 'Janhavi Pradip Kadukar', 'janhavi.1251071029@vit.edu', '9172977298', 'CE', 'Computer Engineering', 2);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0804', '1251070804', 'Hasti Shashikant Patil', 'hasti.1251070804@vit.edu', '9421191633', 'CE', 'Computer Engineering', 1);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-1041', '1251071041', 'Harshad mahadik', 'harshad.1251071041@vit.edu', '9699497810', 'CE', 'Computer Engineering', 1);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('EE25-0246', '1251070246', 'Himanshu Satupte', 'himanshu.1251070246@vit.edu', '7249511721', 'EE', 'Electronics Engineering', 2);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('EE25-0757', '1251070757', 'Aditi Sandip Kadilag', 'aditi.1251070757@vit.edu', '7745045546', 'EE', 'Electronics Engineering', 1);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0311', '1251070311', 'Apeksha Ramesh Kale', 'apeksha.1251070311@vit.edu', '9422648134', 'CE', 'Computer Engineering', 1);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0453', '1251070453', 'Ishita Jitendra Deshmukh', 'ishita.1251070453@vit.edu', '8767221563', 'CE', 'Computer Engineering', 2);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0240', '1251070240', 'Rudra', 'rudra.1251070240@vit.edu', NULL, 'CE', 'Computer Engineering', 1);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('ME25-1053', '1251071053', 'Harshal Tapade', 'harshal.1251071053@vit.edu', '9422714676', 'ME', 'Mechanical Engineering', 2);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0648', '1252070648', 'Jayesh Amit Vishwakarma', 'jayesh.1252070648@vit.edu', '9987481554', 'CE', 'Computer Engineering', 2);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0541', '1251070541', 'Ayush Umesh Jambagi', 'ayush.1251070541@vit.edu', '8855838356', 'CE', 'Computer Engineering', 3);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0315', '1251070315', 'PRUTHVIRAJ KAKARWAL', 'pruthviraj.1251070315@vit.edu', '7769980415', 'CE', 'Computer Engineering', 2);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0307', '1251070307', 'Rishabh kanhaiya joshi', 'rishabh.1251070307@vit.edu', '9881120445', 'CE', 'Computer Engineering', 1);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0718', '1251070718', 'Hemanya Gillurkar', 'hemanya.1251070718@vit.edu', '9834352901', 'CE', 'Computer Engineering', 3);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0887', '1251070887', 'Jakate Arnav Gopal', 'arnav.1251070887@vit.edu', '9096460453', 'CE', 'Computer Engineering', 2);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0122', '1251070122', 'Harshada Hanumant Jadhav', 'harshada.1251070122@vit.edu', '9403834381', 'CE', 'Computer Engineering', 3);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0407', '1251070407', 'Jadhav Shrikant Vilas', 'shrikant.1251070407@vit.edu', '7507437194', 'CE', 'Computer Engineering', 1);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0998', '1251070998', 'Darsh Jaiswal', 'darsh.1251070998@vit.edu', '9834111084', 'CE', 'Computer Engineering', 2);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0100', '1251070100', 'Pranali Pramod Ingle', 'pranali.1251070100@vit.edu', '8767297036', 'CE', 'Computer Engineering', 1);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('EE25-0497', '1251070497', 'Jadhav Atharv Santaji', 'atharv.1251070497@vit.edu', '9503708289', 'EE', 'Electronics Engineering', 3);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0112', '1251070112', 'Zoya Sameer Inamdar', 'zoya.1251070112@vit.edu', '9890819899', 'CE', 'Computer Engineering', 2);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0747', '1251070747', 'Isha Shashikant Madrewar', 'isha.1251070747@vit.edu', '7276063016', 'CE', 'Computer Engineering', 3);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0150', '1251070150', 'Harshwardhan Mukund Pawar', 'harshwardhan.1251070150@vit.edu', '9022217098', 'CE', 'Computer Engineering', 3);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0662', '1251070662', 'Hatwar Nayan Ramprakash', 'nayan.1251070662@vit.edu', '9356203686', 'CE', 'Computer Engineering', 2);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0493', '1251070493', 'Swapnil jajgekar', 'swapnil.1251070493@vit.edu', NULL, 'CE', 'Computer Engineering', 3);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('ELE25-0047', '1251070047', 'Shivam Premsing Jamadar', 'shivam.1251070047@vit.edu', '9404911936', 'ELE', 'Electrical Engineering', 1);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0494', '1251070494', 'Shravani Dnyanoba Kale', 'shravani.1251070494@vit.edu', '9309241182', 'CE', 'Computer Engineering', 3);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0282', '1251070282', 'Ayush Shailesh Jadhav', 'ayush.1251070282@vit.edu', '9699578196', 'CE', 'Computer Engineering', 1);

INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
VALUES ('CE25-0152', '1251070152', 'Tanmay Dattatray Kachare', 'tanmay.1251070152@vit.edu', '8767526391', 'CE', 'Computer Engineering', 1);


-- ===========================================================
-- FACULTY COORDINATORS
-- ===========================================================

INSERT INTO FacultyCoordinators (faculty_id, name, email, phone, dept_id, dept_name)
VALUES ('CE-AS', 'Dr. Anjali Sharma', 'anjali.sharma@vit.edu', '9822011001', 'CE', 'Computer Engineering');

INSERT INTO FacultyCoordinators (faculty_id, name, email, phone, dept_id, dept_name)
VALUES ('CE-RK', 'Dr. Ramesh Kulkarni', 'ramesh.kulkarni@vit.edu', '9822011002', 'CE', 'Computer Engineering');

INSERT INTO FacultyCoordinators (faculty_id, name, email, phone, dept_id, dept_name)
VALUES ('EE-SD', 'Prof. Sneha Deshmukh', 'sneha.deshmukh@vit.edu', '9822011003', 'EE', 'Electronics Engineering');

INSERT INTO FacultyCoordinators (faculty_id, name, email, phone, dept_id, dept_name)
VALUES ('ME-VP', 'Dr. Vikram Patil', 'vikram.patil@vit.edu', '9822011004', 'ME', 'Mechanical Engineering');

INSERT INTO FacultyCoordinators (faculty_id, name, email, phone, dept_id, dept_name)
VALUES ('ME-SK', 'Prof. Suresh Kadam', 'suresh.kadam@vit.edu', '9822011005', 'ME', 'Mechanical Engineering');

INSERT INTO FacultyCoordinators (faculty_id, name, email, phone, dept_id, dept_name)
VALUES ('EE-RN', 'Dr. Rajesh Nair', 'rajesh.nair@vit.edu', '9822011006', 'EE', 'Electronics Engineering');

INSERT INTO FacultyCoordinators (faculty_id, name, email, phone, dept_id, dept_name)
VALUES ('ELE-AK', 'Prof. Ashwini Kale', 'ashwini.kale@vit.edu', '9822011007', 'ELE', 'Electrical Engineering');

INSERT INTO FacultyCoordinators (faculty_id, name, email, phone, dept_id, dept_name)
VALUES ('ELE-VT', 'Dr. Vinayak Thorat', 'vinayak.thorat@vit.edu', '9822011008', 'ELE', 'Electrical Engineering');

INSERT INTO FacultyCoordinators (faculty_id, name, email, phone, dept_id, dept_name)
VALUES ('CE-NG', 'Prof. Nandini Ghorpade', 'nandini.ghorpade@vit.edu', '9822011009', 'CE', 'Computer Engineering');

INSERT INTO FacultyCoordinators (faculty_id, name, email, phone, dept_id, dept_name)
VALUES ('ME-AJ', 'Dr. Ajinkya Jadhav', 'ajinkya.jadhav@vit.edu', '9822011010', 'ME', 'Mechanical Engineering');


-- ===========================================================
-- CLUBS
-- ===========================================================

INSERT INTO Clubs (club_id, club_name, category, faculty_id, description)
VALUES ('CSI', 'Computer Society of India', 'Technical', 'CE-AS',
'One of the most active technical societies on campus, empowering students with computing and technology skills through workshops and collaboration');

INSERT INTO Clubs (club_id, club_name, category, faculty_id, description)
VALUES ('SWD', 'Social Welfare and Development Committee', 'Social Service', 'EE-SD',
'Conducts annual social outreach camps and community service drives in villages around Pune');

INSERT INTO Clubs (club_id, club_name, category, faculty_id, description)
VALUES ('EDC', 'Entrepreneurship Development Club', 'Entrepreneurship', 'CE-RK',
'Fosters an entrepreneurial mindset among students through startup mentorship, pitching sessions, and industry networking events');

INSERT INTO Clubs (club_id, club_name, category, faculty_id, description)
VALUES ('ZEPHYR', 'Zephyr', 'Dance', 'ME-VP',
'VIT Pune''s official dance club, bringing together dancers across genres to choreograph, perform, and compete at inter-college fests');

INSERT INTO Clubs (club_id, club_name, category, faculty_id, description)
VALUES ('CSA', 'Computer Society Association', 'Technical', 'ME-VP',
'VIT Pune''s official tech  club, bringing together dancers across genres to choreograph, perform, and compete at inter-college fests');


-- ===========================================================
-- CLUB PROFILES
-- ===========================================================

INSERT INTO ClubProfile (club_id, official_email, instagram_handle)
VALUES ('CSI', 'csi@vit.edu', '@csi_vitpune');

INSERT INTO ClubProfile (club_id, official_email, instagram_handle)
VALUES ('SWD', 'swdcommittee@vit.edu', '@vit_swd');

INSERT INTO ClubProfile (club_id, official_email, instagram_handle)
VALUES ('EDC', 'edc@vit.edu', '@edc_vitpune');

INSERT INTO ClubProfile (club_id, official_email, instagram_handle)
VALUES ('ZEPHYR', 'zephyr@vit.edu', '@zephyr_vitpune');


-- ===========================================================
-- MEMBERSHIPS (initial load; after the modifications below the table
-- holds 86 rows. Clean leadership structure: each club has exactly one President,
-- Secretary, Treasurer, and Event Coordinator)
--
-- 10 students deliberately have NO row here at all (12 more are
-- added as non-members by the modifications block, so 22 in total): CE25-0692, EE25-0191, ELE25-0666, ELE25-0575,
-- CE25-0856, CE25-0240, CE25-0100, CE25-1032, CE25-0165, EE25-0497.
-- These are true non-members. The first four still appear in
-- EventRegistrations below — proving a student can attend an
-- event without ever joining a club.
-- ===========================================================

-- ----- CSI members -----
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('CSI-0369', 'CE25-0369', 'CSI', 'President', '2025-08-05', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('CSI-0718', 'CE25-0718', 'CSI', 'Secretary', '2025-08-01', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('CSI-1041', 'CE25-1041', 'CSI', 'Treasurer', '2025-08-01', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('CSI-0348', 'EE25-0348', 'CSI', 'Event Coordinator', '2025-08-20', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('CSI-1053', 'ME25-1053', 'CSI', 'Member', '2025-09-10', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('CSI-0323', 'CE25-0323', 'CSI', 'Volunteer', '2025-08-05', 'Inactive');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('CSI-0277', 'CE25-0277', 'CSI', 'Member', '2025-09-15', 'Inactive');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('CSI-0314', 'CE25-0314', 'CSI', 'Member', '2025-09-15', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('CSI-0152', 'CE25-0152', 'CSI', 'Member', '2025-08-01', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('CSI-0804', 'CE25-0804', 'CSI', 'Member', '2025-08-05', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('CSI-0662', 'CE25-0662', 'CSI', 'Member', '2025-08-12', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('CSI-0541', 'CE25-0541', 'CSI', 'Core Member', '2025-09-15', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('CSI-0424', 'CE25-0424', 'CSI', 'Volunteer', '2025-08-12', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('CSI-0573', 'CE25-0573', 'CSI', 'Member', '2025-09-10', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('CSI-0826', 'CE25-0826', 'CSI', 'Volunteer', '2025-09-01', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('CSI-0998', 'CE25-0998', 'CSI', 'Core Member', '2025-09-10', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('CSI-0870', 'CE25-0870', 'CSI', 'Member', '2025-08-12', 'Active');

-- ----- SWD members -----
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('SWD-0893', 'ME25-0893', 'SWD', 'President', '2025-08-10', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('SWD-0431', 'CE25-0431', 'SWD', 'Secretary', '2025-08-20', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('SWD-0648', 'CE25-0648', 'SWD', 'Treasurer', '2025-08-12', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('SWD-0125', 'CE25-0125', 'SWD', 'Event Coordinator', '2025-08-01', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('SWD-0453', 'CE25-0453', 'SWD', 'Volunteer', '2025-08-20', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('SWD-1059', 'ME25-1059', 'SWD', 'Member', '2025-08-12', 'Inactive');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('SWD-0855', 'CE25-0855', 'SWD', 'Member', '2025-08-12', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('SWD-0407', 'CE25-0407', 'SWD', 'Core Member', '2025-09-10', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('SWD-0047', 'ELE25-0047', 'SWD', 'Member', '2025-08-12', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('SWD-0898', 'ME25-0898', 'SWD', 'Core Member', '2025-09-10', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('SWD-0757', 'EE25-0757', 'SWD', 'Member', '2025-09-10', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('SWD-0150', 'CE25-0150', 'SWD', 'Volunteer', '2025-08-05', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('SWD-0493', 'CE25-0493', 'SWD', 'Member', '2025-08-01', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('SWD-0867', 'ME25-0867', 'SWD', 'Volunteer', '2025-09-15', 'Active');

-- ----- EDC members -----
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('EDC-0246', 'EE25-0246', 'EDC', 'President', '2024-08-01', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('EDC-0122', 'CE25-0122', 'EDC', 'Secretary', '2025-08-05', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('EDC-0230', 'CE25-0230', 'EDC', 'Treasurer', '2025-09-10', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('EDC-1055', 'CE25-1055', 'EDC', 'Event Coordinator', '2025-09-10', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('EDC-0315', 'CE25-0315', 'EDC', 'Core Member', '2025-08-05', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('EDC-1008', 'CE25-1008', 'EDC', 'Member', '2025-08-12', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('EDC-0747', 'CE25-0747', 'EDC', 'Member', '2025-09-10', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('EDC-0226', 'CE25-0226', 'EDC', 'Member', '2025-09-10', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('EDC-0815', 'CE25-0815', 'EDC', 'Core Member', '2025-09-01', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('EDC-0342', 'CE25-0342', 'EDC', 'Member', '2025-08-05', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('EDC-0992', 'EE25-0992', 'EDC', 'Member', '2025-09-10', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('EDC-0784', 'CE25-0784', 'EDC', 'Volunteer', '2025-08-12', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('EDC-0678', 'ELE25-0678', 'EDC', 'Member', '2025-09-15', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('EDC-0887', 'CE25-0887', 'EDC', 'Core Member', '2025-09-10', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('EDC-0494', 'CE25-0494', 'EDC', 'Volunteer', '2025-09-15', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('EDC-1039', 'EE25-1039', 'EDC', 'Member', '2025-08-01', 'Active');

-- ----- ZEPHYR members -----
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('ZEPHYR-0187', 'ME25-0187', 'ZEPHYR', 'President', '2025-09-15', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('ZEPHYR-0193', 'CE25-0193', 'ZEPHYR', 'Secretary', '2025-09-10', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('ZEPHYR-0311', 'CE25-0311', 'ZEPHYR', 'Treasurer', '2025-08-20', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('ZEPHYR-0203', 'CE25-0203', 'ZEPHYR', 'Event Coordinator', '2025-09-10', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('ZEPHYR-1029', 'CE25-1029', 'ZEPHYR', 'Member', '2025-08-01', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('ZEPHYR-0185', 'CE25-0185', 'ZEPHYR', 'Member', '2025-08-12', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('ZEPHYR-0416', 'ELE25-0416', 'ZEPHYR', 'Member', '2025-09-15', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('ZEPHYR-0112', 'CE25-0112', 'ZEPHYR', 'Core Member', '2025-08-01', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('ZEPHYR-0885', 'ME25-0885', 'ZEPHYR', 'Volunteer', '2025-09-01', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('ZEPHYR-0282', 'CE25-0282', 'ZEPHYR', 'Member', '2025-08-12', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('ZEPHYR-1062', 'CE25-1062', 'ZEPHYR', 'Volunteer', '2025-08-20', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('ZEPHYR-0307', 'CE25-0307', 'ZEPHYR', 'Member', '2025-08-01', 'Active');

-- ----- ADDITIONAL memberships: students enrolled in a 2nd or 3rd club -----
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('ZEPHYR-0718', 'CE25-0718', 'ZEPHYR', 'Member', '2025-11-20', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('EDC-0453', 'CE25-0453', 'EDC', 'Member', '2025-11-01', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('CSI-0047', 'ELE25-0047', 'CSI', 'Member', '2025-10-15', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('ZEPHYR-0424', 'CE25-0424', 'ZEPHYR', 'Member', '2025-10-15', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('SWD-0804', 'CE25-0804', 'SWD', 'Member', '2026-01-10', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('EDC-0493', 'CE25-0493', 'EDC', 'Member', '2026-01-10', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('SWD-0307', 'CE25-0307', 'SWD', 'Member', '2025-11-01', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('EDC-0203', 'CE25-0203', 'EDC', 'Member', '2025-11-20', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('EDC-0855', 'CE25-0855', 'EDC', 'Member', '2026-01-10', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('CSI-0226', 'CE25-0226', 'CSI', 'Member', '2025-10-01', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('ZEPHYR-0407', 'CE25-0407', 'ZEPHYR', 'Member', '2025-11-20', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('CSI-0246', 'EE25-0246', 'CSI', 'Member', '2025-11-01', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('CSI-0125', 'CE25-0125', 'CSI', 'Member', '2025-11-20', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('SWD-1039', 'EE25-1039', 'SWD', 'Member', '2025-10-01', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('ZEPHYR-0747', 'CE25-0747', 'ZEPHYR', 'Member', '2025-10-01', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('EDC-0885', 'ME25-0885', 'EDC', 'Member', '2026-01-10', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('SWD-0494', 'CE25-0494', 'SWD', 'Member', '2025-11-01', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('ZEPHYR-1041', 'CE25-1041', 'ZEPHYR', 'Member', '2026-01-10', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('EDC-1041', 'CE25-1041', 'EDC', 'Member', '2025-11-20', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('ZEPHYR-0887', 'CE25-0887', 'ZEPHYR', 'Member', '2025-10-01', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('SWD-0887', 'CE25-0887', 'SWD', 'Member', '2025-10-01', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('EDC-0541', 'CE25-0541', 'EDC', 'Member', '2026-02-05', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('ZEPHYR-0541', 'CE25-0541', 'ZEPHYR', 'Member', '2026-02-05', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('CSI-0815', 'CE25-0815', 'CSI', 'Member', '2026-02-05', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('ZEPHYR-0815', 'CE25-0815', 'ZEPHYR', 'Member', '2026-02-05', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('SWD-1029', 'CE25-1029', 'SWD', 'Member', '2025-11-01', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('EDC-1029', 'CE25-1029', 'EDC', 'Member', '2026-02-05', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('SWD-0230', 'CE25-0230', 'SWD', 'Member', '2025-10-01', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('ZEPHYR-0230', 'CE25-0230', 'ZEPHYR', 'Member', '2025-11-20', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('EDC-0648', 'CE25-0648', 'EDC', 'Member', '2026-01-10', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('CSI-0648', 'CE25-0648', 'CSI', 'Member', '2025-10-01', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('EDC-0870', 'CE25-0870', 'EDC', 'Member', '2025-10-15', 'Active');
INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
VALUES ('SWD-0870', 'CE25-0870', 'SWD', 'Member', '2025-11-01', 'Active');

-- ===========================================================
-- EVENTS
-- ===========================================================

INSERT INTO Events (event_id, club_id, event_name, event_date, venue, budget_allocated, event_type, status)
VALUES ('CSI26-TF', 'CSI', 'CSI TechFest 26', '2026-09-25', 'Conference Room', 30000.00, 'Workshop', 'Planned');

INSERT INTO Events (event_id, club_id, event_name, event_date, venue, budget_allocated, event_type, status)
VALUES ('EDC26-ES', 'EDC', 'E-Summit 26', '2026-10-10', 'Sharad Arena', 50000.00, 'Entrepreneurship', 'Completed');

INSERT INTO Events (event_id, club_id, event_name, event_date, venue, budget_allocated, event_type, status)
VALUES ('SWD26-NGO', 'SWD', 'NGO Outreach Drive', '2026-12-15', 'Velhe Village, Pune District', 25000.00, 'Social', 'Completed');

INSERT INTO Events (event_id, club_id, event_name, event_date, venue, budget_allocated, event_type, status,
                     is_award_winning, award_title, award_level)
VALUES ('ZEPH26-GF', 'ZEPHYR', 'Groovefest 26', '2025-11-20', 'Sharad Arena', 12000.00, 'Cultural', 'Completed',
        TRUE, 'Best Dance Performance - Inter-College Fest', 'Inter-College');

INSERT INTO Events (event_id, club_id, event_name, event_date, venue, budget_allocated, event_type, status)
VALUES ('CSI26-HACK', 'CSI', 'CodeStorm Hackathon 26', '2026-09-05', 'IT Lab 3', 40000.00, 'Hackathon', 'Planned');

INSERT INTO Events (event_id, club_id, event_name, event_date, venue, budget_allocated, event_type, status)
VALUES ('CSI26-WEB', 'CSI', 'Web Dev Bootcamp', '2026-10-18', 'Seminar Hall 2', 15000.00, 'Workshop', 'Planned');

INSERT INTO Events (event_id, club_id, event_name, event_date, venue, budget_allocated, event_type, status)
VALUES ('EDC26-PITCH', 'EDC', 'Startup Pitch Day', '2026-11-05', 'Auditorium', 35000.00, 'Entrepreneurship', 'Completed');

INSERT INTO Events (event_id, club_id, event_name, event_date, venue, budget_allocated, event_type, status)
VALUES ('EDC26-ALUM', 'EDC', 'Alumni Founders Talk Series', '2026-12-02', 'Seminar Hall 1', 10000.00, 'Talk', 'Planned');

INSERT INTO Events (event_id, club_id, event_name, event_date, venue, budget_allocated, event_type, status)
VALUES ('SWD26-BLOOD', 'SWD', 'Blood Donation Camp', '2026-09-20', 'College Ground', 8000.00, 'Social', 'Planned');

INSERT INTO Events (event_id, club_id, event_name, event_date, venue, budget_allocated, event_type, status)
VALUES ('ZEPH26-FRESH', 'ZEPHYR', 'Freshers Dance Meet', '2026-09-12', 'Open Air Theatre', 18000.00, 'Cultural', 'Planned');


-- ===========================================================
-- EVENT REGISTRATIONS
-- Note: ME25-0893, CE25-0369 remain real members attending their
-- own club's event (normal case). CE25-0692, EE25-0191,
-- ELE25-0666, ELE25-0575 are now NON-members attending events —
-- the exact case sir asked about, now cleanly demonstrable.
-- ===========================================================

INSERT INTO EventRegistrations (registration_id, event_id, student_id, registration_date, attendance_status)
VALUES ('TF26-0893', 'CSI26-TF', 'ME25-0893', '2026-09-01', 'Registered');

INSERT INTO EventRegistrations (registration_id, event_id, student_id, registration_date, attendance_status)
VALUES ('ES26-0718', 'EDC26-ES', 'CE25-0718', '2026-09-15', 'Registered');

INSERT INTO EventRegistrations (registration_id, event_id, student_id, registration_date, attendance_status)
VALUES ('NGO26-0369', 'SWD26-NGO', 'CE25-0369', '2026-11-01', 'Attended');

INSERT INTO EventRegistrations (registration_id, event_id, student_id, registration_date, attendance_status)
VALUES ('GF25-0246', 'ZEPH26-GF', 'EE25-0246', '2025-11-01', 'Attended');

INSERT INTO EventRegistrations (registration_id, event_id, student_id, registration_date, attendance_status)
VALUES ('HACK26-0692', 'CSI26-HACK', 'CE25-0692', '2026-08-25', 'Registered');

INSERT INTO EventRegistrations (registration_id, event_id, student_id, registration_date, attendance_status)
VALUES ('WEB26-0125', 'CSI26-WEB', 'CE25-0125', '2026-09-30', 'Attended');

INSERT INTO EventRegistrations (registration_id, event_id, student_id, registration_date, attendance_status)
VALUES ('PITCH26-0191', 'EDC26-PITCH', 'EE25-0191', '2026-10-20', 'Registered');

INSERT INTO EventRegistrations (registration_id, event_id, student_id, registration_date, attendance_status)
VALUES ('ALUM26-0666', 'EDC26-ALUM', 'ELE25-0666', '2026-11-15', 'Attended');

INSERT INTO EventRegistrations (registration_id, event_id, student_id, registration_date, attendance_status)
VALUES ('BLOOD26-0575', 'SWD26-BLOOD', 'ELE25-0575', '2026-09-10', 'Registered');

INSERT INTO EventRegistrations (registration_id, event_id, student_id, registration_date, attendance_status)
VALUES ('FRESH26-0885', 'ZEPH26-FRESH', 'ME25-0885', '2026-09-01', 'Registered');


-- ===========================================================
-- FEEDBACK
-- ===========================================================

INSERT INTO Feedback (feedback_id, student_id, club_id, event_id, feedback_type, rating, comments, feedback_date)
VALUES ('CF26-01', 'CE25-0369', 'CSI', NULL, 'Club', 5, 'Very active club with good technical activities.', '2026-08-10');

INSERT INTO Feedback (feedback_id, student_id, club_id, event_id, feedback_type, rating, comments, feedback_date)
VALUES ('CF26-02', 'EE25-0246', 'EDC', NULL, 'Club', 4, 'Great exposure to startups and networking opportunities.', '2026-08-10');

INSERT INTO Feedback (feedback_id, student_id, club_id, event_id, feedback_type, rating, comments, feedback_date)
VALUES ('EF25-01', 'EE25-0246', NULL, 'ZEPH26-GF', 'Event', 5, 'Groovefest was very well organised and high energy.', '2025-11-21');




-- ===========================================================
-- REQUESTED DATA MODIFICATIONS
-- ===========================================================
-- IMPORTANT:
-- Everything above this section is the original Club Management
-- System SQL/data exactly as supplied.
-- The original 69 Students rows and the original Memberships
-- rows are NOT replaced or shortened.
-- This section only performs the requested modifications AFTER
-- the original tables and original checks have been created.
-- ===========================================================

START TRANSACTION;


-- ===========================================================
-- 1. CREATE 12 TRUE NON-MEMBERS
-- ===========================================================
-- These students already exist in Students and each originally had
-- exactly ONE Memberships row. We remove ALL of their Memberships
-- rows, but we do NOT delete the students themselves.
-- Final effect: each of these 12 students has ZERO club memberships.
-- ===========================================================

-- Selected student_ids (12 total):
-- CE25-0152, CE25-0185, CE25-0277, CE25-0282,
-- CE25-0314, CE25-0323, CE25-0342, CE25-0573,
-- CE25-0662, CE25-0784, CE25-0826, CE25-1008

DELETE FROM Memberships
WHERE student_id IN (
    'CE25-0152',
    'CE25-0185',
    'CE25-0277',
    'CE25-0282',
    'CE25-0314',
    'CE25-0323',
    'CE25-0342',
    'CE25-0573',
    'CE25-0662',
    'CE25-0784',
    'CE25-0826',
    'CE25-1008'
);


-- ===========================================================
-- 2. CREATE 6 MULTI-CLUB MEMBERS
-- ===========================================================
-- Each selected student originally had exactly ONE membership.
-- A new membership is added in a DIFFERENT club.
-- Existing roles are untouched; all new rows use role='Member'.
-- All new join dates are later than the original join dates.
-- The UNIQUE(student_id, club_id) constraint is respected.
-- ===========================================================

INSERT INTO Memberships
    (membership_id, student_id, club_id, role, join_date, status)
VALUES
    ('CSI-0112',     'CE25-0112', 'CSI',    'Member', '2026-03-01', 'Active'),
    ('SWD-0122',     'CE25-0122', 'SWD',    'Member', '2026-03-02', 'Active'),
    ('EDC-0150',     'CE25-0150', 'EDC',    'Member', '2026-03-03', 'Active'),
    ('EDC-0193',     'CE25-0193', 'EDC',    'Member', '2026-03-04', 'Active'),
    ('ZEPHYR-0348',  'EE25-0348', 'ZEPHYR', 'Member', '2026-03-05', 'Active'),
    ('SWD-1053',     'ME25-1053', 'SWD',    'Member', '2026-03-06', 'Active');


-- ===========================================================
-- 3. CREATE MULTI-EVENT PARTICIPANTS
-- ===========================================================
-- Add 10 new EventRegistrations across different events.
-- Three of the students below are among the NEW non-members:
-- CE25-0314, CE25-0342, CE25-0784.
-- This demonstrates that a student may participate in multiple
-- events without belonging to any club.
-- ===========================================================

INSERT INTO EventRegistrations
    (registration_id, event_id, student_id, registration_date, attendance_status)
VALUES
    ('TF26-0314',    'CSI26-TF',    'CE25-0314', '2026-09-02', 'Registered'),
    ('ES26-0314',    'EDC26-ES',    'CE25-0314', '2026-09-05', 'Registered'),
    ('NGO26-0342',   'SWD26-NGO',   'CE25-0342', '2026-11-05', 'Registered'),
    ('FRESH26-0342', 'ZEPH26-FRESH','CE25-0342', '2026-09-03', 'Attended'),
    ('HACK26-0784',  'CSI26-HACK',  'CE25-0784', '2026-08-28', 'Registered'),
    ('PITCH26-0784', 'EDC26-PITCH', 'CE25-0784', '2026-10-25', 'Registered'),
    ('WEB26-0893',   'CSI26-WEB',   'ME25-0893', '2026-09-10', 'Attended'),
    ('ALUM26-0718',  'EDC26-ALUM',  'CE25-0718', '2026-09-20', 'Registered'),
    ('HACK26-0369',  'CSI26-HACK',  'CE25-0369', '2026-08-28', 'Attended'),
    ('BLOOD26-0246', 'SWD26-BLOOD', 'EE25-0246', '2026-09-05', 'Attended');

COMMIT;


-- ===========================================================
-- MEMBER COUNT SYNC
-- Clubs.member_count is set once = the real number of rows in Memberships
-- for that club. Non-members have no Memberships row, so they are never
-- counted. Result: CSI 17, SWD 24, EDC 25, ZEPHYR 20, CSA 0.
-- ===========================================================

UPDATE Clubs
SET member_count = (SELECT COUNT(*) FROM Memberships m WHERE m.club_id = Clubs.club_id)
WHERE club_id IN ('CSI','SWD','EDC','ZEPHYR','CSA');

COMMIT;

-- ===========================================================
-- OUTPUT: the 8 original tables (fixed order, each by primary key)
-- ===========================================================
SELECT * FROM Students           ORDER BY student_id;
SELECT * FROM FacultyCoordinators ORDER BY faculty_id;
SELECT * FROM Clubs              ORDER BY club_id;
SELECT * FROM ClubProfile        ORDER BY club_id;
SELECT * FROM Memberships        ORDER BY membership_id;
SELECT * FROM Events             ORDER BY event_id;
SELECT * FROM EventRegistrations ORDER BY registration_id;
SELECT * FROM Feedback           ORDER BY feedback_id;