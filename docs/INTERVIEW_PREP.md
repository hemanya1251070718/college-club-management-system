# ClubHub Enterprise DBMS — Viva & Interview Preparation Guide

> **Comprehensive Technical Master Guide for DBMS Project Viva & Architecture Interviews**  
> *Curated for VIT Pune Academic Evaluation, Project Defense, and Technical Interviews.*

---

## 📌 Section 1: Database Triggers Architecture

### Q1: What is a Database Trigger and why did we implement them in MySQL?
**Answer**:
A database trigger is a procedural code block stored in the database dictionary that executes automatically in response to specified Data Manipulation Language (DML) events (`INSERT`, `UPDATE`, `DELETE`) on a particular table.
In ClubHub, we implemented **8 declarative triggers** to enforce business rules and data consistency at the lowest architectural layer:
- **Zero Application Drift**: If an administrator or script modifies records directly in Cloud SQL, business rules cannot be bypassed.
- **$O(1)$ Performance**: Avoids expensive `COUNT(*)` table scans across large membership tables.
- **Data Integrity**: Guarantees that related tables (e.g., `Clubs.member_count`) are atomically updated within the same transaction.

### Q2: Explain Trigger 1 (`trg_after_membership_insert_sync_count`) in detail.
**Answer**:
- **Timing & Event**: `AFTER INSERT ON Memberships FOR EACH ROW`
- **Assigned Track**: Member 1
- **Business Rule**: Whenever a student joins a club with status `'Active'`, the corresponding club's `member_count` in the `Clubs` table must be incremented by 1 immediately.
- **SQL Implementation**:
```sql
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
END $$
DELIMITER ;
```
- **Key Concepts**:
  - `NEW`: Pseudo-record representing the incoming row being inserted.
  - `OLD`: Not available during an `INSERT` trigger (only in `UPDATE` and `DELETE`).
  - Atomicity: If the `UPDATE Clubs` fails, the `INSERT INTO Memberships` transaction is rolled back automatically.

### Q3: How does Trigger 3 (`trg_prevent_multiple_presidents`) abort transactions?
**Answer**:
Trigger 3 uses MySQL's standard `SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '...'` construct:
- `SQLSTATE '45000'` is the ANSI SQL standard generic state code for user-defined unhandled exceptions.
- It immediately aborts the current transaction, preventing multiple students from holding an `'Active'` President role in the same club.

---

## 🔁 Section 2: Stored Procedures & Cursors

### Q1: What is a Cursor in MySQL and what is its complete lifecycle?
**Answer**:
A cursor is a database pointer mechanism that enables row-by-row iteration over a multi-row result set returned by a `SELECT` query.
Its lifecycle consists of 5 explicit steps:
1. **`DECLARE cursor_name CURSOR FOR select_statement;`**: Declares the query associated with the cursor (must appear after variable declarations).
2. **`DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;`**: Catches the end of the result set to break the loop gracefully.
3. **`OPEN cursor_name;`**: Executes the query and allocates server-side memory for the result set.
4. **`FETCH cursor_name INTO var1, var2;`**: Retrieves the current row values into local variables and advances the cursor pointer.
5. **`CLOSE cursor_name;`**: Releases the server resources and memory associated with the cursor.

### Q2: Why did we build `sp_audit_club_counts(p_fix)`?
**Answer**:
`sp_audit_club_counts` is an administrative reconciliation procedure that uses a cursor to iterate through all registered clubs in the `Clubs` table, calculates the true active headcount from `Memberships`, compares it with `Clubs.member_count`, and in fix mode (`p_fix = TRUE`), atomically repairs any discrepancy.

---

## 🔒 Section 3: Cloud Architecture, Security & RBAC

### Q1: How does Cloud SQL integration work securely without public IP exposure?
**Answer**:
- **Private Socket Connection**: Our Cloud Run container connects to Cloud SQL over an encrypted Unix domain socket (`/cloudsql/project-id:region:instance-name`).
- **No External IP / No `0.0.0.0/0`**: The Cloud SQL instance strictly disallows public internet ingress.
- **Google Secret Manager**: Passwords and connection secrets are loaded dynamically via Cloud Run environment bindings connected to Secret Manager (`roles/secretmanager.secretAccessor`).
- **Least-Privilege IAM**: The dedicated Service Account (`club-app-sa`) only possesses permissions to access the secret and communicate over the Cloud SQL client socket.

### Q2: How does the Role-Based Access Control (RBAC) work?
**Answer**:
ClubHub implements strict institutional email detection:
1. **Principal / Super Admin (`admin`)**: Matches `*.principal@vit.edu`. Full administrative authority, raw cursor execution, schema management.
2. **Faculty Coordinator (`manager`)**: Matches `*.*.cordinator@vit.edu`. Charter management, event scheduling, attendance records.
3. **Student Member (`member`)**: Matches `*.*@vit.edu`. Exploratory read-only directory access; all write endpoints are protected via Flask `@write_required` decorators.
4. **Guest Evaluator (`guest`)**: 1-Click presentation mode bypassing restrictions so evaluators can inspect every feature effortlessly.

---

## 🎨 Section 4: Ben Shneiderman's 8 Golden Rules

| # | Rule | Concrete Implementation in ClubHub |
|---|---|---|
| **1** | **Strive for Consistency** | Centralized design tokens in `tokens.css`, uniform 56px table rows, 4-state buttons, standard modal structures. |
| **2** | **Seek Universal Usability** | Full keyboard control (`/` search, `?` cheat sheet, `Esc` dismiss), high-contrast text (WCAG AA), screen-reader tags. |
| **3** | **Offer Informative Feedback** | Google Pay rainbow confirmation animation, real-time Cloud SQL socket telemetry ping, toast notifications. |
| **4** | **Design Dialogs to Yield Closure** | Phased wizard steps for enrolment, pre-submission review summaries, explicit completion banners. |
| **5** | **Prevent Errors** | Real-time regex email pattern detection, date bounds, capacity validation, clear human-readable error messages. |
| **6** | **Permit Easy Reversal of Actions** | Pre-destruction confirmation dialogs for deletes, reversible status toggles (Active &harr; Inactive). |
| **7** | **Keep Users in Control** | Top-right 1-Click Guest demo override for faculty, non-modal side navigation drawer, persona switcher. |
| **8** | **Reduce Short-Term Memory Load** | Breadcrumb navigation trails on all pages, inline SQL trigger DDL boxes, form draft persistence. |
