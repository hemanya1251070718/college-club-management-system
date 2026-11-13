# hem-trigger: Live MySQL Editor Demonstration Guide for 2 Triggers

> **Project:** College Club Management System (ClubHub DBMS)  
> **Author:** Hemanya Gillurkar  
> **Course:** Database Management Systems Mini Project Evaluation (VIT Pune)  
> **Target Database:** `trial_club`  
> **Companion SQL Script:** [`docs/hem-trigger.sql`](file:///d:/VIT%20PUNE/GDG/cloud/docs/hem-trigger.sql)

---

## 🎯 The 2 Completely Different Triggers You Are Demonstrating

You are demonstrating **two completely different architectural styles of MySQL triggers**:

| Trigger | Name | Timing & Table | Type of Trigger | What It Does (In Layman Terms) |
| :--- | :--- | :--- | :--- | :--- |
| **Trigger 1** | `trg_after_membership_insert_sync_count` | `AFTER INSERT ON Memberships` | **Data Propagation (Positive Automation)** | Whenever a student joins a club, MySQL automatically adds `+1` to `Clubs.member_count` in the original base table. |
| **Trigger 2** | `trg_prevent_multiple_presidents` | `BEFORE INSERT ON Memberships` | **Integrity Enforcement (Negative Constraint)** | Enforces College Bylaws: If an unauthorized user tries to add a 2nd President to a club, MySQL instantly aborts the transaction with `SIGNAL SQLSTATE '45000'`. |

> **🌟 Why Faculty Love This Contrast:**  
> - Trigger 1 proves you know how to **propagate changes** across relational tables automatically without manual code.  
> - Trigger 2 proves you know how to **protect relational data** from corruption by throwing custom database exceptions before invalid rows land in the storage engine.

---

## 🖥️ Screen & Tab Setup in MySQL Workbench / Editor

To clearly show the changes in the original table to your examiner, set up **Two Query Tabs**:

```
┌─────────────────────────────────┐   ┌─────────────────────────────────┐
│ TAB 1: [ORIGINAL TABLES]        │   │ TAB 2: [docs/hem-trigger.sql]   │
│                                 │   │                                 │
│ SELECT * FROM Clubs...          │◄──┼──► Execute INSERT / DELETE      │
│ SELECT * FROM Memberships...    │   │    Triggers fire in background! │
└─────────────────────────────────┘   └─────────────────────────────────┘
                ▲                                     ▲
                └────────── Press [Ctrl + Tab] ───────┘
```

### 1. Set Up Tab 1 (Original Tables Verification Tab)
In MySQL Workbench, press **`Ctrl + T`** to open a new tab. Paste these two lines:
```sql
USE trial_club;
-- Query 1A: Inspect Original Clubs Table
SELECT club_id, club_name, member_count FROM Clubs WHERE club_id = 'CSI';

-- Query 2A: Inspect Original Memberships Table for President
SELECT membership_id, student_id, club_id, role, status FROM Memberships WHERE club_id = 'CSI' AND role = 'President';
```

### 2. Set Up Tab 2 (Your Demo Actions Tab)
Open the file [`docs/hem-trigger.sql`](file:///d:/VIT%20PUNE/GDG/cloud/docs/hem-trigger.sql).

### 3. How to Hop Between Files During the Demo:
* **Switch Tab:** Press **`Ctrl + Tab`** (or simply click the tab name at the top).
* **Execute Single Line:** Put your blinking cursor on the specific line and press **`Ctrl + Enter`** (executes ONLY that query).

---

## 🕹️ Step-by-Step Demonstration Walkthrough (Line by Line)

---

### 📍 PRE-FLIGHT (Before the Examiner looks)
1. Open MySQL Workbench.
2. In `docs/hem-trigger.sql`, highlight the `CREATE TRIGGER` blocks (lines 25–65) and run them once to ensure both triggers exist.
3. In the left **Schemas Navigator**, expand `trial_club` $\rightarrow$ `Tables` $\rightarrow$ `Memberships` $\rightarrow$ `Triggers`.  
   👉 Point out to the teacher: Both triggers are live inside the MySQL engine!

---

### 📍 PART 1: DEMONSTRATING TRIGGER 1 (AUTOMATED BASE TABLE DATA SYNC)

#### STEP 1.1: [HOP TO TAB 1] $\rightarrow$ Show Baseline Count in Original `Clubs` Table
* **Action:** Hop to **Tab 1** (or Line 96 in `hem-trigger.sql`).
* **Line to run:**
  ```sql
  SELECT club_id, club_name, member_count FROM Clubs WHERE club_id = 'CSI';
  ```
* **Keyboard Shortcut:** Put cursor on this line and press **`Ctrl + Enter`**.
* **What appears on screen:** The Result Grid shows CSI with `member_count` (e.g. **`22`**).
* **🗣️ Spoken Dialogue:**
  > *"Sir, please observe our original base table `Clubs`. For the club 'CSI', the current stored `member_count` is **22**. Now, without running any update query on this table, watch what happens when a student enrolls."*

---

#### STEP 1.2: [HOP TO TAB 2] $\rightarrow$ Fire Trigger 1 by Enrolling a Student
* **Action:** Press **`Ctrl + Tab`** to switch to **Tab 2** (`docs/hem-trigger.sql`).
* **Line to run (Line 106):**
  ```sql
  INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
  VALUES ('HEM-DEMO-01', 'ME25-0898', 'CSI', 'Member', CURRENT_DATE, 'Active');
  ```
* **Keyboard Shortcut:** Put cursor on Line 106 and press **`Ctrl + Enter`**.
* **What appears on screen:** In the bottom **Action Output** pane, a **Green Checkmark** appears: `1 row(s) affected`.
* **🗣️ Spoken Dialogue:**
  > *"Sir, I have inserted one new active membership for student ME25-0898 into the `Memberships` table. Notice that I only inserted into `Memberships`; I did not touch the `Clubs` table at all."*

---

#### STEP 1.3: [HOP TO TAB 1] $\rightarrow$ Show Automatic +1 Change in Original `Clubs` Table!
* **Action:** Press **`Ctrl + Tab`** to hop back to **Tab 1**.
* **Line to run (or Line 117 in `hem-trigger.sql`):**
  ```sql
  SELECT club_id, club_name, member_count FROM Clubs WHERE club_id = 'CSI';
  ```
* **Keyboard Shortcut:** Press **`Ctrl + Enter`** (or click the Refresh icon above the grid).
* **What appears on screen:** The `member_count` has automatically incremented from 22 to **`23`**!
* **🗣️ Spoken Dialogue:**
  > *"Look at the original `Clubs` table now, sir! `member_count` automatically incremented to **23**! Our AFTER INSERT trigger executed in the background and updated the base table in $O(1)$ time with zero manual recount code."*

---

#### STEP 1.4: [HOP TO TAB 2] $\rightarrow$ Clean up the Trigger 1 Demo Row
* **Action:** Press **`Ctrl + Tab`** to switch to **Tab 2**, put cursor on Line 124, and press **`Ctrl + Enter`**:
  ```sql
  DELETE FROM Memberships WHERE membership_id = 'HEM-DEMO-01';
  ```

---

### 📍 PART 2: DEMONSTRATING TRIGGER 2 (BUSINESS BYLAW & INTEGRITY ENFORCEMENT)

#### STEP 2.1: [HOP TO TAB 1] $\rightarrow$ Show Existing Active President in Original Table
* **Action:** Press **`Ctrl + Tab`** to switch to **Tab 1**.
* **Line to run:**
  ```sql
  SELECT membership_id, student_id, club_id, role, status 
  FROM Memberships 
  WHERE club_id = 'CSI' AND role = 'President';
  ```
* **Keyboard Shortcut:** Put cursor on this line and press **`Ctrl + Enter`**.
* **What appears on screen:** Result Grid shows that **Hitaishi Bodele** (`CE25-0369`) is already the active President of CSI.
* **🗣️ Spoken Dialogue:**
  > *"Now for Trigger 2, please observe our original `Memberships` table. CSI already has an active President. According to college bylaws, a club cannot have two presidents simultaneously."*

---

#### STEP 2.2: [HOP TO TAB 2] $\rightarrow$ Attempt to Insert a 2nd President (FAILS WITH ERROR!)
* **Action:** Press **`Ctrl + Tab`** to switch to **Tab 2** (`docs/hem-trigger.sql`).
* **Line to run (Line 150):**
  ```sql
  INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
  VALUES ('HEM-ILLEGAL-PRES', 'ME25-0898', 'CSI', 'President', CURRENT_DATE, 'Active');
  ```
* **Keyboard Shortcut:** Put cursor on Line 150 and press **`Ctrl + Enter`**.
* **What appears on screen:** A **Red 'X' Error** pops up in the bottom Action Output pane:
  ```
  Error Code: 1644. Integrity Violation: A club cannot have more than ONE active President simultaneously.
  ```
* **🗣️ Spoken Dialogue:**
  > *"Now an unauthorized user attempts to insert a second President for CSI. Notice that MySQL immediately intercepts the query and raises SQLSTATE 45000, rejecting the transaction before any data is written!"*

---

#### STEP 2.3: [HOP TO TAB 1] $\rightarrow$ Show Original Table Was NOT Corrupted!
* **Action:** Press **`Ctrl + Tab`** to switch to **Tab 1**.
* **Line to run:**
  ```sql
  SELECT membership_id, student_id, club_id, role, status 
  FROM Memberships 
  WHERE club_id = 'CSI' AND role = 'President';
  ```
* **Keyboard Shortcut:** Press **`Ctrl + Enter`**.
* **What appears on screen:** Result Grid still shows **only one row**! The illegal second president was rejected completely.
* **🗣️ Spoken Dialogue:**
  > *"When we re-query the original `Memberships` table, you can see that the illegal record was never admitted. Trigger 2 preserved database integrity directly at the storage engine level."*

---

#### STEP 2.4: [HOP TO TAB 2] $\rightarrow$ Prove Valid Membership Enrollment Works
* **Action:** Switch to **Tab 2**, put cursor on Line 171, and press **`Ctrl + Enter`**:
  ```sql
  INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
  VALUES ('HEM-VALID-02', 'ME25-0898', 'CSI', 'Member', CURRENT_DATE, 'Active');
  ```
* **What appears on screen:** Green checkmark!
* **🗣️ Spoken Dialogue:**
  > *"To prove the trigger only blocks illegal presidential appointments, when we enroll this exact same student as an ordinary 'Member', the transaction succeeds immediately!"*
* **Cleanup:** Run Line 175 (`DELETE FROM Memberships WHERE membership_id = 'HEM-VALID-02';`).

---

## 🏆 Final Summary Statement to Deliver to Examiner
> *"Sir, Trigger 1 demonstrates **affirmative data propagation** (automatically incrementing member counts across tables), while Trigger 2 demonstrates **defensive constraint enforcement** (aborting duplicate leadership appointments via custom SQLSTATE 45000). Together, they prove that our database maintains complete relational integrity autonomously without relying on application code."*
