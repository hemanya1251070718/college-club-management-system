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
