# Learning Notes

## Phase B0: Discovery & Environment Setup
- **What happened:** We inspected your local machine and scanned your workspace for database assets and tools.
- **Why it matters:** Before creating any code or cloud resources, a senior engineer always verifies existing foundations: local runtimes, database schemas, and CLI tooling. 
- **Findings:**
  - Found your schema in `Club_Management_System_BASE.sql` (8 tables, view `ClubSummary`, stored procedure `GetStudentClubs`, and 69 student records) and two advanced audit/recruitment procedures in `cursor.sql`.
  - Python 3.13.5 and Git 2.55 are installed and ready.
  - Local MySQL Server 8.0.46 is already installed and actively running as a Windows service (`MySQL80`).
  - Google Cloud CLI (`gcloud`) installer was executed and authenticated.

## Phase B1: Local Application Construction & Automated Testing
- **What happened:** We structured and built a modular Flask application (`app/routes.py`, `app/db.py`, `app/config.py`) connected to MySQL using PyMySQL, complete with a Bootstrap 5 UI, interactive stored procedure execution, and an 8-test pytest suite.
- **Why it matters:** In production cloud engineering, you never deploy directly to the cloud without validating functionality locally first. Developing locally allows fast debugging, verifies parameterized SQL queries prevent SQL injection, and ensures database triggers automatically maintain business data integrity before spending cloud resources.
- **Key Files & Highlights:**
  - `app/db.py`: Dual-mode connection manager that dynamically uses TCP locally (`DB_HOST:DB_PORT`) and Unix Sockets (`/cloudsql/...`) when deployed to Cloud Run.
  - `triggers.sql`: Defines `trg_increase_member_count` and `trg_decrease_member_count` so inserting or deleting a student membership in the web UI automatically updates `Clubs.member_count` in MySQL.
  - `app/routes.py`: Every database query uses parameter substitution (`%s` tuples), completely eliminating SQL injection risks.
  - `tests/test_app.py`: 8 automated unit tests verifying health checks, environment toggling, and route security.

## Phase B2: Cloud Account Activation, IAM Hardening & Pipeline Verification
- **What happened:** Your ₹1,000 prepayment settled, activating Billing Account `015C4C-8DD910-6F8D3B`. We linked project `project-a4079d46-9d8b-469f-993`, enabled the 5 required Google Cloud APIs (`run`, `sqladmin`, `secretmanager`, `artifactregistry`, `cloudbuild`), created a dedicated service account (`club-app-sa`) with least-privilege roles, and deployed a live "Hello World" service to Cloud Run in Mumbai (`asia-south1`).
- **Why it matters:** Senior cloud engineers prove deployment pipelines with a trivial service first before introducing database complexity. Creating a dedicated runtime identity (`club-app-sa`) ensures the application cannot modify or delete cloud infrastructure if breached.
- **Key Resources & Roles:**
  - `club-app-sa@project-a4079d46-9d8b-469f-993.iam.gserviceaccount.com`: The application's runtime identity.
  - `roles/cloudsql.client`: Allows connecting to Cloud SQL via internal socket proxy without granting administrative DB rights.
  - `roles/secretmanager.secretAccessor`: Allows reading the database password from Secret Manager without granting permission to create or delete secrets.
  - Live Endpoint: `https://hello-pipeline-test-326279554484.asia-south1.run.app` (Returning HTTP 200).

## Phase B3: Managed Cloud Database & Secret Encryption
- **What happened:** We provisioned a Google Cloud SQL instance (`club-mysql-instance`) running MySQL 8.0 in Mumbai (`asia-south1-a`), created the database `trial_club` and user `club_app_user`, and stored the password securely in Secret Manager as `club-db-password` (v2).
- **Why it matters:** Hardcoding database credentials in code or `.env` files committed to Git is the #1 security vulnerability in web development. By delegating credential storage to Secret Manager, the password is encrypted at rest and injected directly into Cloud Run at startup.
- **Key Architecture Insight:** The Cloud SQL instance has zero authorized public networks (`0.0.0.0/0` is blocked). Connections are only permitted via the Cloud SQL Proxy Unix Socket inside the Google Cloud private backbone.

## Phase B4: Cloud Run Deployment & Database Population
- **What happened:** We containerized the Flask application with Docker, configured Gunicorn WSGI workers, attached the Cloud SQL instance connection name, and deployed to Cloud Run (`club-management-app`). We then ran `load_schema.py` inside the container via `/init-db` to populate all 8 tables, 69 students, triggers, views, and stored procedures.
- **Why it matters:** Cloud Run automatically handles TLS/HTTPS certificates, load balancing, and autoscaling. By configuring `min-instances=0` (scale-to-zero) and `max-instances=2`, your app incurs ₹0 compute costs when nobody is visiting, while preventing billing runaway during high traffic.
- **Live Service URL:** `https://club-management-app-326279554484.asia-south1.run.app`

## Phase B5: Live Functional Verification & Procedure Validation
- **What happened:** We verified every endpoint on the live Cloud Run deployment:
  - `/health`: Confirmed database status `healthy`, engine `8.0.46-google`, and connection mode `Cloud SQL Unix Socket`.
  - `/`: Loaded `ClubSummary` view data and college club counts.
  - `/memberships`: Verified trigger `trg_increase_member_count` on inserting student memberships.
  - `/procedures/audit`: Executed cursor procedure `sp_audit_club_counts(0)` validating synchronization across all 5 clubs.
  - `/procedures/student-clubs`: Executed `GetStudentClubs` returning multi-club memberships for student `CE25-1029`.
- **Recorded Artifact:** Recorded interactive tour `live_cloud_app_tour_1792702022052.webp`.

## Phase B6: Documentation & Interview Readiness
- **What happened:** We committed the final architecture diagrams, demo scripts, resource tracking tables, and 50+ interview questions with honest technical answers into the repository.
- **Deliverables Ready:**
  - `README.md`: Complete project overview, architecture diagram, and teardown commands.
  - `docs/DEMO_SCRIPT.md`: Step-by-step 5-minute live interview demonstration.
  - `docs/INTERVIEW_PREP.md`: 50+ categorized interview questions and answers.
  - `docs/CONCEPTS.md`: Plain-English analogies for every cloud and database concept.
  - `docs/SECURITY.md`: Honest evaluation of our security posture and real-world enterprise improvements.
