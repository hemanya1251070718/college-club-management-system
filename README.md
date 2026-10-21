# College Club Management System (GCP Cloud Deployment)

> **Cloud Deployment Task:** Demonstrating a production-ready Web Application deployed on Google Cloud Platform featuring live Cloud SQL (MySQL 8.0) database integration, Secret Manager encryption, least-privilege IAM service account, automated database triggers, SQL views, and stored procedures.

---

## Architecture Overview
- **Compute:** Google Cloud Run (Serverless Container Runtime, region: `asia-south1` Mumbai)
- **Database:** Google Cloud SQL for MySQL 8.0 (Enterprise, 1 vCPU, 3.75 GB RAM, single zone)
- **Security:** Google Secret Manager (stores database credentials; zero secrets in code or git history)
- **Identity & Access:** Dedicated GCP Service Account with least-privilege roles (`roles/cloudsql.client`, `roles/secretmanager.secretAccessor`)
- **Backend:** Python 3.13, Flask 3.1, PyMySQL
- **Frontend:** Bootstrap 5, Vanilla JavaScript, Responsive Design

---

## Database Features Demonstrated
1. **CRUD Operations:** Full Create, Read, Update, and Delete across `Clubs`, `Students`, `Memberships`, and `Events`.
2. **Database View (`ClubSummary`):** Aggregates club information with faculty advisors and live member counts.
3. **Automated Database Triggers (`trg_increase_member_count`, `trg_decrease_member_count`):** Automatically increments/decrements `Clubs.member_count` whenever memberships are created or deleted.
4. **Stored Procedures:**
   - `GetStudentClubs(p_student_id)`: Fetches club enrollments for a given student via a relational join.
   - `sp_audit_club_counts(p_fix)`: Loops through clubs via a MySQL cursor to detect and auto-repair member count discrepancies.
5. **System Health Endpoint (`/health`):** Verifies database reachability and returns connection mode (TCP vs Unix socket).

---

## Local Development Setup

### 1. Prerequisites
- Python 3.13+
- MySQL 8.0 Server running locally

### 2. Setup Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Database Credentials
Create a `.env` file (copied from `.env.example`):
```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_local_mysql_password
DB_NAME=trial_club
SECRET_KEY=dev-secret-key-vit-cloud-2026
```

### 4. Initialize Database
Import schema and triggers into MySQL:
```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p trial_club < Club_Management_System_BASE.sql
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p trial_club < triggers.sql
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p trial_club < cursor.sql
```

### 5. Run Application & Tests
```powershell
# Run Tests
pytest -v

# Run Dev Server
python run.py
```
Open [http://localhost:8080](http://localhost:8080) in your browser.
