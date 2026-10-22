# Cloud Security Architecture & Assessment

This document outlines the security posture, defense-in-depth measures, and acknowledged limitations of the **College Club Management System** deployed on Google Cloud Platform.

---

## 1. What Is Protected (Security Measures Implemented)

### A. Zero Secrets in Code or Repositories
- **Implementation:** The database password is never hardcoded, written to disk, or committed to Git.
- **Mechanism:** In production, credentials are stored in **Google Secret Manager** (`db-password`). At container startup, Google Cloud Run fetches the secret dynamically and injects it into the environment as `DB_PASSWORD`.
- **Git Hygiene:** Local `.env` and secret files are strictly excluded via [`.gitignore`](file:///d:/VIT%20PUNE/GDG/cloud/.gitignore).

### B. Prevention of SQL Injection (SQLi)
- **Implementation:** 100% of database interactions in [`app/routes.py`](file:///d:/VIT%20PUNE/GDG/cloud/app/routes.py) use **parameterized queries** with tuple bindings (`%s`).
- **Mechanism:** User inputs from HTML forms are never concatenated or formatted via f-strings into SQL statements. MySQL treats user inputs strictly as literals, completely neutralizing SQL injection attacks.

### C. IAM Principle of Least Privilege
- **Implementation:** The application does **not** run using the default Compute Engine service account (which has broad `Editor` permissions).
- **Mechanism:** A dedicated service account (`club-app-sa`) is provisioned with only the exact roles required:
  1. `roles/cloudsql.client` (Permits establishing proxy connections to Cloud SQL instances).
  2. `roles/secretmanager.secretAccessor` (Permits reading the database password from Secret Manager).
- **Impact:** Even if the web application were compromised, the attacker has zero permissions to alter infrastructure, delete databases, or modify IAM policies.

### D. Network Isolation (Zero Public DB Exposure)
- **Implementation:** The Cloud SQL instance does **not** authorize `0.0.0.0/0` (open internet).
- **Mechanism:** Cloud Run communicates with Cloud SQL through the built-in Cloud SQL connector over a local Unix domain socket mount (`/cloudsql/PROJECT:REGION:INSTANCE`).
- **Impact:** Port 3306 is not publicly reachable from the open internet, preventing automated port scans and brute-force MySQL attacks.

### E. Information Leakage Suppression
- **Implementation:** Custom HTTP 404 and 500 error pages in [`app/templates/errors/`](file:///d:/VIT%20PUNE/GDG/cloud/app/templates/errors/).
- **Mechanism:** Raw Python exceptions, database schema dumps, and traceback logs are suppressed from the client browser and redirected to Google Cloud Logging (`stdout`/`stderr`).

### F. Cost & Denial-of-Service (DoS) Capping
- **Implementation:** Cloud Run `--max-instances=2` and memory limit `--memory=512MiB`.
- **Impact:** Prevents bill explosion or runaway autoscaling during high traffic or automated stress testing.

---

## 2. What Is NOT Protected (Honest Architectural Limitations)

In an engineering interview, acknowledging real limitations shows maturity:

1. **Unauthenticated Public Endpoints:**
   - *Limitation:* The web routes currently do not enforce user authentication (no session login, OAuth, or RBAC). Anyone who possesses the public Cloud Run URL can view or edit club data.
   - *Production Remediation:* In a full campus rollout, integrate Google Identity-Aware Proxy (IAP) or Firebase Authentication with student college email verification.

2. **Absence of Web Application Firewall (WAF) / Rate Limiting:**
   - *Limitation:* The app relies on Cloud Run's built-in Google front-end DDoS defenses, but lacks application-layer rate limiting (e.g., limiting form submissions to 10 per minute per IP).
   - *Production Remediation:* Place Google Cloud Armor in front of the Cloud Run service via an External HTTPS Load Balancer with rate-limiting rules.

3. **Single Zone Database Deployment (No High Availability):**
   - *Limitation:* Cloud SQL is provisioned in a single zone (`asia-south1-a`) without a standby failover instance to remain strictly within student free-tier budget limits.
   - *Production Remediation:* Enable Cloud SQL High Availability (Regional HA) with automatic regional failover for critical enterprise uptime.
