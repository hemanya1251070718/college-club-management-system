# ClubHub Enterprise DBMS — Engineering Learning Notes

> **Deep-Dive Architectural & Database Engineering Notes**  
> *Documentation of database design principles, cloud infrastructure trade-offs, and design system tokens.*

---

## 🏗️ 1. Relational Schema Normalization

ClubHub features **8 canonical domain tables** architected according to Boyce-Codd Normal Form (BCNF):

```
Students ────< Memberships >──── Clubs
                   │
                   v
          EventRegistrations >──── Events ────< Feedback
                   │
                   v
             AttendanceLogs
```

### Normal Form Breakdown:
1. **First Normal Form (1NF)**:
   - All column values are atomic (e.g., student names are split, no multi-valued contact lists).
   - Each table has a designated primary key (`student_id`, `club_id`, `membership_id`, `event_id`).
2. **Second Normal Form (2NF)**:
   - In 1NF and contains zero partial key dependencies.
   - All composite associative entities (such as `Memberships` and `EventRegistrations`) use surrogate keys while non-key attributes depend entirely on the primary key.
3. **Third Normal Form (3NF)**:
   - In 2NF and contains zero transitive dependencies ($X \to Y \to Z$).
   - Club leader metadata is normalized; `Clubs` references student leaders via foreign keys rather than duplicating personal details.
4. **Boyce-Codd Normal Form (BCNF)**:
   - Every functional dependency determinant is a superkey, preventing update and deletion anomalies.

---

## ⚡ 2. Declarative Triggers vs Application-Layer Recounts

### Architectural Trade-off:
- **Application-Layer Recount**:
  ```python
  # Fragile: requires two separate round-trips; susceptible to race conditions and dirty reads
  cursor.execute("INSERT INTO Memberships ...")
  cursor.execute("UPDATE Clubs SET member_count = (SELECT COUNT(*) FROM Memberships WHERE club_id = %s)", (club_id,))
  ```
- **Declarative Database Trigger (Trigger 1)**:
  ```sql
  -- Atomic: executed inside the database transaction engine at C-level speed
  CREATE TRIGGER trg_after_membership_insert_sync_count
  AFTER INSERT ON Memberships
  FOR EACH ROW
  BEGIN
      IF NEW.status = 'Active' THEN
          UPDATE Clubs SET member_count = member_count + 1 WHERE club_id = NEW.club_id;
      END IF;
  END;
  ```
- **Benefit**: Even if an administrator executes a bulk import directly via MySQL Workbench, data integrity is 100% preserved.

---

## 🌐 3. Serverless State & Ephemeral Containers

### The Challenge on Modern Serverless Platforms (Vercel / AWS Lambda):
1. **Stateless Nature**: Each incoming HTTP request may be routed to an independent execution sandbox.
2. **Read-Only Code Directory**: The code root is immutable; only `/tmp` is writable.
3. **Cold Starts**: When a new sandbox spins up, process memory (`MEMORY_USERS`) resets to baseline seed data.

### The ClubHub Dual-Layer Resilience Strategy:
1. **Targeted `/tmp/users.db` Path**: SQLite automatically resolves to `/tmp/users.db` when running on serverless runtimes.
2. **Auto-Rehydration for Official Institutional Accounts**:
   ```python
   # In authenticate_user():
   role, role_title, err = detect_role_from_email(email_clean)
   if not err and len(password.strip()) >= 4:
       # Auto-provision on the freshly spawned sandbox immediately
   ```
3. **Client-Side Sync via `localStorage`**: The browser transparently rehydrates registered accounts if a cold container returns an unauthenticated status.

---

## 🎨 4. Design System Tokens (`tokens.css`)

ClubHub adopts a luxury automotive (Tesla/Apple) dark visual identity using standardized CSS custom properties:

```css
:root {
  --bg-0: #05060B;           /* Primary page background */
  --surface-1: #0D1020;      /* Card & panel backgrounds */
  --surface-2: #141834;      /* Modals & raised surfaces */
  --blue-400: #4F7CFF;       /* Active accents & focus rings */
  --blue-500: #2F5BEA;       /* Primary CTA button background */
  --text-1: #F4F6FF;         /* Primary text (Contrast >= 15:1) */
  --text-2: #B6BBD8;         /* Secondary text (Contrast >= 8:1) */
  --radius-card: 14px;       /* Consistent corner curve */
}
```

This token architecture ensures strict compliance with **Ben Shneiderman's Rule 1 (Strive for Consistency)** and **Rule 2 (Universal Usability / WCAG AA Contrast)**.
