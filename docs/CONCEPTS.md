# Google Cloud & Systems Concepts Guide

This guide breaks down every cloud computing, database, and security concept used in this project into plain English with real-world analogies, mapped directly to where they exist in our code and cloud infrastructure.

---

## 1. Cloud Service Models: IaaS vs. PaaS vs. Serverless
* **Analogy:**
  * **IaaS (Infrastructure as a Service):** Buying an empty plot of land. You build the house, plumbing, and wiring yourself (e.g., Google Compute Engine virtual machines).
  * **PaaS (Platform as a Service):** Renting a furnished apartment. You bring your clothes and furniture; the landlord handles building maintenance (e.g., Google App Engine).
  * **Serverless (Container-as-a-Service):** Calling a cab on Uber. A car appears only when you need a ride, you pay only for the minutes you ride, and the car leaves when you get out (e.g., Google Cloud Run).
* **In This Project:** We chose **Cloud Run (Serverless)** because as a student project, you pay $0.00 when nobody is using the website. The server automatically spins down to zero instances.

---

## 2. Regions & Zones
* **What it is:**
  * **Region:** A distinct geographic location where Google has multiple data centers (e.g., `asia-south1` is Mumbai, India; `asia-south2` is Delhi).
  * **Zone:** An isolated data center within that region (e.g., `asia-south1-a`, `asia-south1-b`). Zones have independent power, cooling, and network hardware.
* **In This Project:**
  * We target **`asia-south1` (Mumbai)** to minimize network latency for users in India.
  * We host Cloud SQL in a single zone (`asia-south1-a`) to avoid the 2x cost multiplier of multi-zone high-availability.

---

## 3. Serverless Compute: Google Cloud Run
* **What it is:** A fully managed serverless compute platform that runs stateless Docker containers behind an automated HTTPS load balancer.
* **Revisions:** Every time you deploy new code, Cloud Run creates an immutable snapshot called a **Revision**. If a new release has a bug, you can instantly rollback traffic to the previous revision with one click.
* **Autoscaling:** Cloud Run automatically scales containers from 0 up to your configured maximum based on incoming concurrent HTTP requests.
* **Cold Starts:** When traffic drops to 0, Cloud Run deallocates all containers to save money. When a new user visits, Cloud Run must pull the container image and initialize Python/Flask. This first request takes 1–3 seconds (a "cold start"). Subsequent requests respond in milliseconds ("warm").
* **In This Project:** Configured in [`Dockerfile`](file:///d:/VIT%20PUNE/GDG/cloud/Dockerfile) with `--max-instances=2` and `--memory=512MiB`.

---

## 4. Managed Relational Database: Google Cloud SQL
* **Cloud SQL vs. Firestore (NoSQL):**
  * **Cloud SQL:** Fully managed relational MySQL/PostgreSQL with ACID transactions, foreign keys, triggers, and complex JOIN queries. Perfect for relational schemas like College Clubs with strict relational constraints.
  * **Firestore:** Document/NoSQL database optimized for massive horizontal scale and real-time document listeners, but lacks native relational JOINs, foreign key cascades, and complex SQL views.
* **In This Project:** We run **Cloud SQL for MySQL 8.0** to natively support the existing relational schema, foreign keys, `ClubSummary` view, and `AFTER INSERT` triggers.

---

## 5. Cloud Database Networking: Unix Socket vs. Public IP
* **The Dangerous Way (Public IP):** Adding `0.0.0.0/0` to authorized networks opens port 3306 to the entire internet. Attackers use automated botnets to brute-force MySQL passwords.
* **The Google Cloud Way (Unix Domain Socket):** Cloud Run has built-in integration with Cloud SQL. When deployed, Google mounts a private Unix domain socket directly inside the container filesystem at `/cloudsql/PROJECT:REGION:INSTANCE`.
* **In This Project:** In [`app/config.py`](file:///d:/VIT%20PUNE/GDG/cloud/app/config.py) and [`app/db.py`](file:///d:/VIT%20PUNE/GDG/cloud/app/db.py), PyMySQL connects directly to this internal Unix socket when `INSTANCE_CONNECTION_NAME` is present, requiring zero internet port exposure.

---

## 6. IAM (Identity and Access Management) & Least Privilege
* **Principle of Least Privilege:** An identity (human or service) should be granted *only* the minimum permissions necessary to accomplish its specific job, and nothing more.
* **User Accounts vs. Service Accounts:**
  * **User Account:** Represents a human with email and password/MFA (e.g., `hemanyagillurkar28@gmail.com`). Used to log into GCP console.
  * **Service Account:** A non-human identity used by applications to authenticate when talking to other Google Cloud services.
* **In This Project:**
  * We created a dedicated service account: `club-app-sa@...`.
  * We assigned only 2 fine-grained roles:
    1. `roles/cloudsql.client` (Connects to Cloud SQL via proxy).
    2. `roles/secretmanager.secretAccessor` (Reads decrypted secret payloads).
  * We avoided the generic `Editor` or `Owner` roles.

---

## 7. Secrets Management: Google Secret Manager
* **Why not environment variables directly in console?** Plain environment variables can leak in console screenshots, build logs, or process dumps.
* **How Secret Manager works:** Secrets are encrypted with Google-managed or customer-managed encryption keys (AES-256) at rest. Versioning allows rotating passwords without editing code.
* **In This Project:** Cloud Run references the secret resource name (`db-password`) and injects it securely into the container runtime as the `DB_PASSWORD` environment variable.

---

## 8. Application Health & Observability
* **Health Endpoint (`/health`):**
  * Implemented in [`app/routes.py:L11`](file:///d:/VIT%20PUNE/GDG/cloud/app/routes.py#L11).
  * Executes `SELECT 1, VERSION(), DATABASE()` against MySQL. Returns HTTP 200 if connected, or HTTP 503 if the database is unreachable.
* **Cloud Logging:**
  * Any output written to Python's `stdout` or `stderr` is automatically captured by Google Cloud Logging with structured severity levels (`INFO`, `WARNING`, `ERROR`).
