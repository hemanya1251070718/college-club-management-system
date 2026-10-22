# Engineering Study Map: From Local Code to Cloud Defense

This document defines your structured learning path. Every concept is directly linked to the actual code, configuration file, or cloud resource in this repository.

---

## Stage 1: The Application & Database Foundations
*Goal: Understand what the code does before explaining how the cloud hosts it.*

| Topic | Concept to Master | Where It Appears in This Project |
|---|---|---|
| **1. Relational Schema & Integrity** | Primary keys, foreign key constraints, cascading effects, polymorphic checks. | [`Club_Management_System_BASE.sql`](file:///d:/VIT%20PUNE/GDG/cloud/Club_Management_System_BASE.sql) |
| **2. Database Triggers** | Event-driven execution inside the database engine (`AFTER INSERT`, `AFTER DELETE`). | [`triggers.sql`](file:///d:/VIT%20PUNE/GDG/cloud/triggers.sql) & [`app/templates/memberships/list.html`](file:///d:/VIT%20PUNE/GDG/cloud/app/templates/memberships/list.html) |
| **3. Database Views** | Virtual tables defined by stored queries for simplified reporting and security. | [`ClubSummary` in `Club_Management_System_BASE.sql`](file:///d:/VIT%20PUNE/GDG/cloud/Club_Management_System_BASE.sql#L254) |
| **4. Stored Procedures & Cursors** | Server-side procedural logic; row-by-row cursor iteration for auditing and repairs. | [`cursor.sql`](file:///d:/VIT%20PUNE/GDG/cloud/cursor.sql) & [`app/templates/procedures/audit.html`](file:///d:/VIT%20PUNE/GDG/cloud/app/templates/procedures/audit.html) |
| **5. Application Architecture** | Flask application factory pattern, routing, template rendering, and error handling. | [`app/__init__.py`](file:///d:/VIT%20PUNE/GDG/cloud/app/__init__.py) & [`app/routes.py`](file:///d:/VIT%20PUNE/GDG/cloud/app/routes.py) |

---

## Stage 2: Packaging & Containerization
*Goal: Understand how the application becomes portable for any cloud environment.*

| Topic | Concept to Master | Where It Appears in This Project |
|---|---|---|
| **6. Containers vs. Virtual Machines** | Operating system-level virtualization, process isolation, lightweight base images. | [`Dockerfile`](file:///d:/VIT%20PUNE/GDG/cloud/Dockerfile) |
| **7. Production WSGI Servers** | Why Flask's built-in server is unsafe for production; Gunicorn multi-threading (`workers=1, threads=8`). | [`Dockerfile:L23`](file:///d:/VIT%20PUNE/GDG/cloud/Dockerfile#L23) |
| **8. Build Hygiene & Security** | Excluding sensitive environment files and caches from container images. | [`.dockerignore`](file:///d:/VIT%20PUNE/GDG/cloud/.dockerignore) & [`.gitignore`](file:///d:/VIT%20PUNE/GDG/cloud/.gitignore) |

---

## Stage 3: Google Cloud Architecture & Operations
*Goal: Understand the cloud services powering your project and why each was chosen.*

| Topic | Concept to Master | Where It Appears in This Project |
|---|---|---|
| **9. Serverless Compute (Cloud Run)** | Knative-based auto-scaling, scale-to-zero, cold starts, and container request lifecycle. | [`docs/CONCEPTS.md`](file:///d:/VIT%20PUNE/GDG/cloud/docs/CONCEPTS.md) |
| **10. Managed Database (Cloud SQL)** | Fully managed MySQL 8.0, automated backups, single-zone vs high-availability trade-offs. | [`app/db.py`](file:///d:/VIT%20PUNE/GDG/cloud/app/db.py) & Cloud SQL console |
| **11. Cloud Networking & Sockets** | Why open `0.0.0.0/0` is dangerous; connecting via Unix Domain Socket (`/cloudsql/...`). | [`app/config.py`](file:///d:/VIT%20PUNE/GDG/cloud/app/config.py) & [`app/db.py`](file:///d:/VIT%20PUNE/GDG/cloud/app/db.py) |
| **12. Health Probes & Monitoring** | Liveness checking, HTTP 200/503 statuses, Cloud Logging aggregation. | [`/health` in `app/routes.py`](file:///d:/VIT%20PUNE/GDG/cloud/app/routes.py#L11) |

---

## Stage 4: Cloud Security & Defense
*Goal: Defend your architecture against standard security audit questions.*

| Topic | Concept to Master | Where It Appears in This Project |
|---|---|---|
| **13. IAM & Least Privilege** | Avoiding default Editor roles; granting minimum permissions via dedicated service accounts. | [`docs/SECURITY.md`](file:///d:/VIT%20PUNE/GDG/cloud/docs/SECURITY.md) |
| **14. Secrets Management** | Envelope encryption, secret versioning, runtime injection vs compile-time baking. | Google Secret Manager (`db-password`) |
| **15. SQL Injection Prevention** | Parameter substitution (`%s`), prepared statement compilation. | [`app/routes.py`](file:///d:/VIT%20PUNE/GDG/cloud/app/routes.py) |
| **16. Cost Control & Guardrails** | Budget alerts, max instances limits, avoiding bill shock in serverless. | GCP Billing & Cloud Run scaling flags |

---

## Stage 5: Live Demonstration & Interview Defense
*Goal: Deliver a flawless 5-minute presentation and ace follow-up questions.*

| Topic | Concept to Master | Where It Appears in This Project |
|---|---|---|
| **17. Minute-by-Minute Script** | Structured walk-through: UI -> Cloud SQL verification -> Cloud Run settings -> IAM. | [`docs/DEMO_SCRIPT.md`](file:///d:/VIT%20PUNE/GDG/cloud/docs/DEMO_SCRIPT.md) |
| **18. 50+ Interview Questions** | Answering the "trap" questions: cold starts, connection pooling, high availability. | [`docs/INTERVIEW_PREP.md`](file:///d:/VIT%20PUNE/GDG/cloud/docs/INTERVIEW_PREP.md) |
