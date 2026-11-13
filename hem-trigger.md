# hem-trigger: Live MySQL Editor Demonstration Guide for 2 Triggers

> **Project:** College Club Management System (ClubHub DBMS)  
> **Author:** Hemanya Gillurkar  
> **Course:** Database Management Systems Mini Project Evaluation (VIT Pune)  
> **Target Database:** `trial_club`  
> **Companion SQL Script:** [`docs/hem-trigger.sql`](file:///d:/VIT%20PUNE/GDG/cloud/docs/hem-trigger.sql)

---

## 🎯 The 2 Triggers You Are Demonstrating

You are demonstrating **Trigger 1** and **Trigger 2**, which form a **closed, self-balancing cycle** on the original `Clubs` base table:

| Trigger | Name | Timing & Table | What It Does (In Layman Terms) |
| :--- | :--- | :--- | :--- |
| **Trigger 1** | `trg_after_membership_insert_sync_count` | `AFTER INSERT ON Memberships` | Whenever a student joins a club, MySQL automatically adds `+1` to `Clubs.member_count`. |
| **Trigger 2** | `trg_after_membership_delete_sync_count` | `AFTER DELETE ON Memberships` | Whenever that student is removed or leaves, MySQL automatically subtracts `-1` from `Clubs.member_count`. |

> **🌟 Why Faculty Love This Demo:**  
> You don't write any `UPDATE Clubs ...` command yourself! The database engine updates its own original table automatically in $O(1)$ time, guaranteeing zero data corruption.

---

## 🖥️ Screen & Tab Setup in MySQL Workbench / Editor

To clearly show the changes in the original table to your examiner, you can use **either of two setups**:

### 🌟 Method A: The Two-Tab Method (Most Impressive for Professors)

Open **two Query Tabs** side-by-side or tab-by-tab in MySQL Workbench / VS Code:

* **TAB 1 (Named "Original Table: Clubs"):**
  ```sql
  USE trial_club;
  SELECT club_id, club_name, member_count FROM Clubs WHERE club_id = 'CSI';
  ```
* **TAB 2 (Named "Trigger Actions: hem-trigger.sql"):**
  * Open the file `hem-trigger.sql`.

> **How to hop between tabs:**  
> Click the tab headers at the top, or press **`Ctrl + Tab`** / **`Ctrl + PageUp/PageDown`**.

---

### 🌟 Method B: Single Tab Method (Simple & Direct)

Open `hem-trigger.sql` in a single query tab. You will simply move your blinking text cursor from line to line and press **`Ctrl + Enter`**.

---

## 🕹️ Step-by-Step Demonstration Walkthrough (Line by Line)

Here is the exact step-by-step procedure of where to put your cursor, what keys to press, when to hop tabs, and what to say:

```
[Tab 1: Clubs] ──► See count = 22
      │
[Tab 2: Triggers] ─► Run INSERT ('HEM-DEMO-01') ──► Trigger 1 fires!
      │
[Tab 1: Clubs] ──► Re-run SELECT ──► See count = 23 (+1 automatically!)
      │
[Tab 2: Triggers] ─► Run DELETE ('HEM-DEMO-01') ──► Trigger 2 fires!
      │
[Tab 1: Clubs] ──► Re-run SELECT ──► See count = 22 (-1 back to original!)
```

---

### 📍 PRE-FLIGHT (Before the Examiner looks)
1. Open MySQL Workbench / Editor.
2. In `hem-trigger.sql`, highlight lines **27 to 57** (the `CREATE TRIGGER` blocks) and run them once to ensure both triggers exist in the database.
3. In the left **Schemas Navigator**, expand `trial_club` $\rightarrow$ `Tables` $\rightarrow$ `Memberships` $\rightarrow$ `Triggers`.  
   👉 Point out to the teacher: *`trg_after_membership_insert_sync_count`* and *`trg_after_membership_delete_sync_count`* are live inside the MySQL engine.

---

### 📍 STEP 1: Show Original Table Baseline Count
* **Where to go:** Open **Tab 1** (or go to Line 64 in `hem-trigger.sql`).
* **Line to select:**
  ```sql
  SELECT club_id, club_name, member_count FROM Clubs WHERE club_id = 'CSI';
  ```
* **Action:** Place your blinking cursor anywhere inside this line and press **`Ctrl + Enter`**.
* **What appears on screen:** The bottom **Result Grid** shows `CSI`, `Computer Society of India`, and `member_count` (e.g., **`22`**).
* **🗣️ What to say to the Examiner:**
  > *"Sir, please look at our original base table `Clubs`. For the club 'CSI', the current stored `member_count` is **22**. Now, without running any update query on this table, watch what happens when a student enrolls."*

---

### 📍 STEP 2: Hop to Trigger Tab & Fire Trigger 1 (INSERT)
* **Where to go:** Hop to **Tab 2** (`hem-trigger.sql`).
* **Line to select:** Place your cursor on **Line 74**:
  ```sql
  INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
  VALUES ('HEM-DEMO-01', 'ME25-0898', 'CSI', 'Member', CURRENT_DATE, 'Active');
  ```
* **Action:** Press **`Ctrl + Enter`**.
* **What appears on screen:** In the bottom **Action Output** pane, a **Green Checkmark** appears:
  `1 row(s) affected`.
* **🗣️ What to say to the Examiner:**
  > *"Sir, I have inserted one new active membership for student ME25-0898 into the `Memberships` table. Notice that I only inserted into `Memberships`; I did not touch the `Clubs` table at all."*

---

### 📍 STEP 3: Hop Back to Original Table & Show the Automatic Change!
* **Where to go:** Hop back to **Tab 1** (or go to Line 84 in `hem-trigger.sql`).
* **Line to select:**
  ```sql
  SELECT club_id, club_name, member_count FROM Clubs WHERE club_id = 'CSI';
  ```
* **Action:** Press **`Ctrl + Enter`** (or click the small **Refresh / Execute** button above the grid).
* **What appears on screen:** The bottom **Result Grid** now shows `member_count` has become **`23`**!
* **🗣️ What to say to the Examiner:**
  > *"Look here, sir! In the original `Clubs` table, `member_count` automatically changed from 22 to **23**! Our AFTER INSERT trigger executed in the background and synchronized the base table in $O(1)$ time."*

---

### 📍 STEP 4: Hop Back to Trigger Tab & Fire Trigger 2 (DELETE)
* **Where to go:** Hop back to **Tab 2** (`hem-trigger.sql`).
* **Line to select:** Place your cursor on **Line 94**:
  ```sql
  DELETE FROM Memberships WHERE membership_id = 'HEM-DEMO-01';
  ```
* **Action:** Press **`Ctrl + Enter`**.
* **What appears on screen:** In the bottom **Action Output** pane, a **Green Checkmark** appears:
  `1 row(s) affected`.
* **🗣️ What to say to the Examiner:**
  > *"Now, suppose this student cancels their membership or leaves the club. I will delete this record from the `Memberships` table using line 94."*

---

### 📍 STEP 5: Hop Back to Original Table & Show Automatic Reversal!
* **Where to go:** Hop back to **Tab 1** (or go to Line 104 in `hem-trigger.sql`).
* **Line to select:**
  ```sql
  SELECT club_id, club_name, member_count FROM Clubs WHERE club_id = 'CSI';
  ```
* **Action:** Press **`Ctrl + Enter`**.
* **What appears on screen:** The bottom **Result Grid** now shows `member_count` is back to **`22`**!
* **🗣️ What to say to the Examiner:**
  > *"Sir, as you can see, `member_count` in the original `Clubs` table automatically decremented back from 23 to **22**! Trigger 2 handled the cleanup seamlessly. Both triggers ensure our database never has count discrepancies or stale data."*

---

## ⌨️ Essential Keyboard Shortcuts in MySQL Workbench

| Shortcut | What It Does | When to Use It |
| :--- | :--- | :--- |
| **`Ctrl + Enter`** | **Execute Current Statement** | **ALWAYS USE THIS!** Executes only the single SQL query where your cursor is currently blinking. |
| **`Ctrl + Shift + Enter`** | Execute All / Whole Script | Use only once at the beginning to create the triggers. |
| **`Ctrl + Tab`** | Hop to Next Editor Tab | Use to switch between the `Clubs` table tab and the `hem-trigger` tab smoothly. |
| **`Ctrl + W`** | Close current tab | If you open an unnecessary tab. |

---

## 🛠️ Failsafe & Emergency Reset (Just in Case)

If you made a typo or ran the INSERT twice by accident:
1. Run this quick cleanup line:
   ```sql
   DELETE FROM Memberships WHERE membership_id = 'HEM-DEMO-01';
   ```
2. Resync the count with one line:
   ```sql
   UPDATE Clubs SET member_count = (SELECT COUNT(*) FROM Memberships WHERE club_id = 'CSI' AND status = 'Active') WHERE club_id = 'CSI';
   ```
3. Check `Clubs` again:
   ```sql
   SELECT club_id, member_count FROM Clubs WHERE club_id = 'CSI';
   ```
   Everything is restored back to normal!

---

## 🏆 Quick Summary Card to Keep Open on Your Phone

1. **Tab 1:** Run `SELECT ... FROM Clubs WHERE club_id = 'CSI'` $\rightarrow$ **Count = 22**
2. **Tab 2:** Put cursor on `INSERT INTO Memberships ... VALUES ('HEM-DEMO-01'...)` $\rightarrow$ Press `Ctrl + Enter`
3. **Tab 1:** Press `Ctrl + Enter` on `SELECT` $\rightarrow$ **Count = 23 (+1!)**
4. **Tab 2:** Put cursor on `DELETE FROM Memberships WHERE membership_id = 'HEM-DEMO-01'` $\rightarrow$ Press `Ctrl + Enter`
5. **Tab 1:** Press `Ctrl + Enter` on `SELECT` $\rightarrow$ **Count = 22 (-1 back to original!)**

