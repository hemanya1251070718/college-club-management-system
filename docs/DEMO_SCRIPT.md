# ClubHub Enterprise DBMS — Viva & Faculty Demonstration Script

> **A Step-by-Step Practical Demonstration Protocol for Academic Evaluation**  
> *Designed for presenting before professors, evaluators, and project panels at VIT Pune.*

---

## 🎬 Quick Navigation & Pre-Flight Checklist

- **Live URL**: [https://cloud-chi-six.vercel.app](https://cloud-chi-six.vercel.app)
- **Fallback Cloud Run URL**: [https://club-management-app-326279554484.asia-south1.run.app](https://club-management-app-326279554484.asia-south1.run.app)
- **Top Right Instant Safe-Fail Button**: Click **`Guest`** (or `Guest Evaluator`) anytime to demonstrate full functionality with 100% permissions.
- **Audit Report**: Open the **8 Golden Rules** modal from the navbar, or view [`/8_golden_rules.pdf`](/8_golden_rules.pdf).

---

## 🧭 Phase 1: Authentication & Role-Based Access Control (RBAC)

### 1.1 First Impression & Gatekeeper Screen (Switchd-Inspired Aesthetic)
1. Open [https://cloud-chi-six.vercel.app](https://cloud-chi-six.vercel.app).
2. Point out the gatekeeper authentication page with real-time DBMS telemetry, dark Tesla-inspired palette, and instant role detection.
3. **Key Highlight to State to Panel**:
   > *"Sir, we have implemented strict institutional email-based Role-Based Access Control. Our system automatically parses the email pattern to enforce the principle of least privilege before granting access to student charters or database triggers."*

### 1.2 Demonstrating Real-Time Role Detection
1. Click the **Email** input field.
2. Type `aarav.123456@vit.edu`:
   - Notice the badge instantly appears: **`Student Member (Read-Only Access)`**.
3. Type `patil.121001.cordinator@vit.edu`:
   - Notice the badge immediately flips to: **`Faculty Coordinator (Charters & Events)`**.
4. Type `sharma.principal@vit.edu`:
   - Notice the badge elevates to: **`Principal / Super Admin (Full Governance)`**.
5. Demonstrate the **Google Pay Rainbow Celebration Animation**:
   - Click one of the pre-configured demo chips (or enter `password123` with any account).
   - Click **`Sign In`**.
   - Show the rotating rainbow completion circle with the animated checkmark as authentication succeeds and enters the cockpit.

---

## ⚡ Phase 2: Production Database Triggers Demonstration

### 2.1 Navigate to Triggers Architecture
- Click **`Triggers`** in the top navigation bar or side drawer.
- Point out the **Featured Trigger 1 Spotlight Card** at the top of the page.

### 2.2 Live Testing: Trigger 1 (`trg_after_membership_insert_sync_count`) — Member 1
1. **Show the Problem Solved**:
   > *"Sir, in traditional applications, whenever a student joins a club, the backend developer has to write an extra query `UPDATE Clubs SET member_count = member_count + 1`. If the app crashes or if an admin inserts a row directly into the database, data corruption occurs. Our Trigger 1 enforces declarative synchronization directly inside MySQL."*
2. **Step-by-Step Live Proof**:
   - Check the member count for **Computer Society of India (CSI)** on the dashboard or Clubs tab (e.g., currently 19).
   - In the **Trigger 1 Spotlight Card**, click **`Enroll Member to Fire Trigger 1`** (or go to `Memberships` > `Enroll New Member`).
   - Fill in:
     - Student: Pick any enrolled student (e.g., `ME25-0898`).
     - Club: Select `CSI` (Computer Society of India).
     - Role: `Member`.
     - Status: `Active`.
   - Click **`Confirm Enrolment`**.
   - Navigate back to `Clubs` or `Cockpit`: **Notice CSI member count automatically incremented to 20!**
   - Point out: *Zero manual recount query was executed by Python; MySQL executed `trg_after_membership_insert_sync_count` in $O(1)$ time.*

### 2.3 Live Testing: Trigger 2 (`trg_after_membership_delete_sync_count`) — Member 1
1. Go to `Memberships`.
2. Find the membership created above and click **`Delete`**.
3. Confirm in the pre-destruction modal.
4. Check CSI member count again: **Automatically decremented back by 1!**

### 2.4 Live Testing: Trigger 3 (`trg_prevent_multiple_presidents`) — Member 2
1. Go to `Memberships` > `Enroll New Member`.
2. Select a club that already has a President (e.g., `CSI`).
3. Select Role: `President` with Status: `Active`.
4. Click `Confirm Enrolment`.
5. **Show the Result**:
   - Transaction aborts with `SIGNAL SQLSTATE '45000'`: *"Bylaw Violation: Club already possesses an active President."*

---

## 🔄 Phase 3: Stored Procedures & Cursors Demonstration

### 3.1 Navigate to Procedures Hub
- Click **`Procedures`** in the top navigation bar.
- Point out that there are **8 distinct stored procedures powered by SQL cursors**, covering club count audits, recruitment leads, budget reconciliation, and auto-deactivation.

### 3.2 Live Testing: `sp_audit_club_counts(p_fix)`
1. Locate the **Audit Club Member Counts** card.
2. Select Mode: **`Dry-Run (Detect Drift Only)`** and click **`Execute Procedure`**.
3. Show the panel output:
   - The cursor loops through every row in `Clubs`.
   - Computes `COUNT(*)` from `Memberships WHERE status = 'Active'`.
   - Flags any discrepancy between `member_count` cache and raw memberships.
4. Select Mode: **`Apply Repairs (Auto-Correct Base Tables)`** and run again:
   - Show how the procedure updates mismatched counts in a single atomic transaction.

---

## 🛡️ Phase 4: Shneiderman's 8 Golden Rules & Accessibility Audit

1. In the navigation bar, click the **`8 Golden Rules`** badge button.
2. Show the evaluator the modal summarizing compliance across all 8 rules:
   - **Consistency**: Unified tokens, button classes, 56px table rows.
   - **Universal Usability**: Keyboard shortcuts (`/` for search, `?` for cheat sheet, `Esc` to close).
   - **Informative Feedback**: Real-time state badges, Google Pay checkmark, toast notifications.
   - **Dialog Closure**: Phased wizard forms with step progress indicators.
   - **Error Prevention**: Live regex pattern validation and input boundary enforcement.
   - **Reversal of Actions**: Two-step deletion modal confirmation, reversible membership status toggles.
   - **User in Control**: Top-right 1-Click Guest demo override for faculty.
   - **Reduced Memory Load**: Universal breadcrumb navigation and inline SQL definitions.
3. Click **`View Full 13-Page Audit PDF (8_golden_rules.pdf)`** to display the complete generated compliance document.

---

## 🎯 Emergency Fallback: "The Guest Button"
If your professor or evaluator wants to explore all tabs without signing into different roles:
- Simply click the glowing **`Guest`** pill on the top right.
- The site instantly lifts all editing and execution restrictions, giving full unrestricted access to all 8 triggers, 8 cursors, and CRUD interfaces.
