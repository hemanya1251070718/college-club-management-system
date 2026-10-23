import os
import markdown
import subprocess

def build():
    docs_dir = os.path.join(os.path.dirname(__file__), "docs")
    
    # 1. Read all markdown files from docs/
    doc_files = [
        ("STUDY_MAP.md", "Section 2.1: Engineering Study Map & Progression"),
        ("CONCEPTS.md", "Section 2.2: Cloud & Systems Concepts Deep-Dive"),
        ("DECISIONS.md", "Section 2.3: Architectural & Technical Decisions Log"),
        ("SECURITY.md", "Section 2.4: Cloud Security Assessment & Honest Limitations"),
        ("RESOURCES.md", "Section 2.5: Cloud Resources Inventory & Post-Interview Teardown"),
        ("LEARNING_NOTES.md", "Section 2.6: Complete Phase Trajectory (Phases B0 to B6)"),
        ("DEMO_SCRIPT.md", "Section 2.7: 5-Minute Live Interview Demonstration Script"),
        ("INTERVIEW_PREP.md", "Section 2.8: 50+ Cloud Engineering Interview Questions & Traps")
    ]
    
    docs_html_sections = []
    for filename, section_title in doc_files:
        filepath = os.path.join(docs_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            # Convert markdown to html with tables and code blocks
            body_html = markdown.markdown(content, extensions=['tables', 'fenced_code'])
            docs_html_sections.append(f"""
            <div class="page-break"></div>
            <div class="doc-section">
                <div class="section-badge">INTEGRATED FROM docs/{filename}</div>
                <h2>{section_title}</h2>
                <div class="doc-content">
                    {body_html}
                </div>
            </div>
            """)
        else:
            print(f"Warning: {filepath} not found!")

    # 2. Master Template
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>College Club Management System - Master Knowledge & Architecture Guide</title>
  <style>
    @page {{
      size: A4;
      margin: 18mm 16mm 18mm 16mm;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      line-height: 1.55;
      color: #1f2937;
      background-color: #ffffff;
      font-size: 10pt;
    }}
    h1, h2, h3, h4 {{
      color: #111827;
      font-weight: 700;
    }}
    h1 {{
      font-size: 22pt;
      margin-top: 0;
      margin-bottom: 6px;
      color: #1e3a8a;
      border-bottom: 3px solid #3b82f6;
      padding-bottom: 8px;
    }}
    h2 {{
      font-size: 15pt;
      margin-top: 22px;
      margin-bottom: 10px;
      color: #1e40af;
      border-bottom: 1.5px solid #e5e7eb;
      padding-bottom: 5px;
      page-break-after: avoid;
    }}
    h3 {{
      font-size: 12pt;
      margin-top: 16px;
      margin-bottom: 6px;
      color: #1f2937;
      page-break-after: avoid;
    }}
    h4 {{
      font-size: 10.5pt;
      margin-top: 12px;
      margin-bottom: 4px;
      color: #374151;
      page-break-after: avoid;
    }}
    p {{
      margin-top: 0;
      margin-bottom: 8px;
    }}
    .badge {{
      display: inline-block;
      padding: 2px 7px;
      font-size: 8pt;
      font-weight: 600;
      border-radius: 4px;
      background-color: #e0e7ff;
      color: #3730a3;
      margin-right: 4px;
    }}
    .section-badge {{
      display: inline-block;
      padding: 3px 8px;
      font-size: 8pt;
      font-weight: 700;
      letter-spacing: 0.5px;
      text-transform: uppercase;
      border-radius: 4px;
      background-color: #fef3c7;
      color: #92400e;
      border: 1px solid #fde68a;
      margin-bottom: 6px;
    }}
    .callout {{
      background-color: #f8fafc;
      border-left: 4px solid #3b82f6;
      padding: 10px 14px;
      margin: 12px 0;
      border-radius: 0 6px 6px 0;
      page-break-inside: avoid;
    }}
    .callout-success {{
      background-color: #f0fdf4;
      border-left-color: #22c55e;
    }}
    .callout-warning {{
      background-color: #fffbeb;
      border-left-color: #f59e0b;
    }}
    .callout-title {{
      font-weight: 700;
      margin-bottom: 4px;
      color: #0f172a;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 12px 0;
      font-size: 8.5pt;
      page-break-inside: auto;
    }}
    tr {{
      page-break-inside: avoid;
      page-break-after: auto;
    }}
    th, td {{
      border: 1px solid #d1d5db;
      padding: 6px 8px;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      background-color: #f3f4f6;
      color: #111827;
      font-weight: 700;
    }}
    tr:nth-child(even) td {{
      background-color: #f9fafb;
    }}
    code {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      font-size: 8.5pt;
      background-color: #f1f5f9;
      padding: 1px 4px;
      border-radius: 4px;
      color: #0f172a;
      border: 1px solid #e2e8f0;
    }}
    pre {{
      background-color: #0f172a;
      color: #f8fafc;
      padding: 9px 12px;
      border-radius: 6px;
      font-size: 8pt;
      overflow-x: auto;
      margin: 8px 0;
      page-break-inside: avoid;
      line-height: 1.4;
    }}
    pre code {{
      background-color: transparent;
      color: inherit;
      border: none;
      padding: 0;
    }}
    .page-break {{
      page-break-before: always;
    }}
    .subtitle {{
      font-size: 11pt;
      color: #4b5563;
      margin-bottom: 14px;
    }}
    .meta-box {{
      background-color: #eff6ff;
      border: 1px solid #bfdbfe;
      border-radius: 6px;
      padding: 10px 14px;
      margin-bottom: 16px;
      font-size: 9pt;
    }}
    .meta-item {{
      margin-bottom: 3px;
    }}
    .meta-label {{
      font-weight: 700;
      color: #1e40af;
      display: inline-block;
      width: 140px;
    }}
    ul, ol {{
      margin-top: 0;
      margin-bottom: 8px;
      padding-left: 20px;
    }}
    li {{
      margin-bottom: 3px;
    }}
    .toc-box {{
      background-color: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      padding: 12px 18px;
      margin-bottom: 20px;
    }}
    .toc-title {{
      font-weight: 700;
      color: #1e3a8a;
      font-size: 11pt;
      margin-bottom: 8px;
    }}
    .toc-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px 20px;
      font-size: 8.5pt;
    }}
  </style>
</head>
<body>

  <!-- COVER / HEADER -->
  <h1>College Club Management System</h1>
  <div class="subtitle">Complete Master Guide: From Zero-Knowledge Basics to Enterprise Cloud Architecture</div>

  <div class="meta-box">
    <div class="meta-item"><span class="meta-label">Live Service URL:</span> <code>https://club-management-app-326279554484.asia-south1.run.app/</code></div>
    <div class="meta-item"><span class="meta-label">Google Cloud Region:</span> <code>asia-south1</code> (Mumbai, India) | Single-Zone: <code>asia-south1-a</code></div>
    <div class="meta-item"><span class="meta-label">Core Architecture:</span> Python 3.13, Flask 3.1, Cloud Run Serverless, Cloud SQL MySQL 8.0</div>
    <div class="meta-item"><span class="meta-label">Security Posture:</span> Google Secret Manager, Dedicated Service Account (Least Privilege), Private Unix Socket</div>
    <div class="meta-item"><span class="meta-label">Purpose:</span> 100% Comprehensive Master Reference Document integrating all Lessons &amp; Documentation</div>
  </div>

  <div class="toc-box">
    <div class="toc-title">Document Architecture &amp; Table of Contents</div>
    <div class="toc-grid">
      <div>
        <strong>SECTION I: Foundational Master Lessons</strong><br>
        • Part 1: Master Glossary Table (All 22 Terms)<br>
        • Part 2: 7 Google Cloud Components Explained<br>
        • Part 3: The Grand 1-Second Odyssey Timeline<br>
        • Part 4: Internet Fundamentals (Hosting, HTTP, Sockets)<br>
        • Part 5: Relational DB, Keys, Views, Triggers, Cursors<br>
        • Part 6: Docker Containerization (Images vs Containers)<br>
        • Part 7: Cloud Run &amp; Cloud SQL (Serverless &amp; Storage)<br>
        • Part 8: Cloud Security, Secret Manager &amp; Least Privilege
      </div>
      <div>
        <strong>SECTION II: 100% Integrated Documentation</strong><br>
        • 2.1: Engineering Study Map (<a href="#">STUDY_MAP.md</a>)<br>
        • 2.2: Cloud &amp; Systems Concepts (<a href="#">CONCEPTS.md</a>)<br>
        • 2.3: Architectural Decisions Log (<a href="#">DECISIONS.md</a>)<br>
        • 2.4: Cloud Security Assessment (<a href="#">SECURITY.md</a>)<br>
        • 2.5: Resources &amp; Teardown (<a href="#">RESOURCES.md</a>)<br>
        • 2.6: Learning Notes B0 to B6 (<a href="#">LEARNING_NOTES.md</a>)<br>
        • 2.7: 5-Minute Live Demo Script (<a href="#">DEMO_SCRIPT.md</a>)<br>
        • 2.8: 50+ Questions &amp; Traps (<a href="#">INTERVIEW_PREP.md</a>)
      </div>
    </div>
  </div>

  <!-- SECTION I: FOUNDATIONAL LESSONS -->
  <div style="border-top: 2px solid #1e40af; margin-top: 15px; padding-top: 10px;">
    <span class="badge" style="background:#1e40af; color:#fff; font-size:9pt; padding:4px 10px;">SECTION I</span>
    <h2 style="border:none; margin-top:5px; color:#1e3a8a;">The Foundational Lessons &amp; System Concepts</h2>
  </div>

  <!-- PART 1: MASTER GLOSSARY -->
  <h3>Part 1: The Master Glossary Table</h3>
  <p>Every single technical term broken down side-by-side into <em>Layman Meaning (Baby Level)</em>, <em>Technical Definition</em>, and <em>Exact Project Role</em>:</p>

  <table>
    <thead>
      <tr>
        <th style="width: 17%;">Technical Term</th>
        <th style="width: 38%;">🥪 Layman Explanation (Baby Level)</th>
        <th style="width: 45%;">⚙️ Technical Role in Our Project</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Hosting</strong></td>
        <td>Giving your files a 24/7 house so they don't sleep when your laptop is turned off.</td>
        <td>Google Cloud hosts our code and database in its Mumbai data center (<code>asia-south1</code>).</td>
      </tr>
      <tr>
        <td><strong>Server</strong></td>
        <td>A computer with no monitor or keyboard that sits in a cold room, waiting to "serve" files to visitors.</td>
        <td>Google's machines act as the servers that run our Flask app and MySQL engine.</td>
      </tr>
      <tr>
        <td><strong>Browser</strong></td>
        <td>The TV screen (like Chrome on your phone) that turns raw code into pretty buttons and text.</td>
        <td>The student or interviewer opens Chrome and sees the ClubHub website.</td>
      </tr>
      <tr>
        <td><strong>URL</strong></td>
        <td>The contact name in your phonebook (e.g., <code>google.com</code>) so you don't have to remember a 10-digit phone number.</td>
        <td><code>https://club-management-app-326279554484.asia-south1.run.app/</code> mapped via DNS.</td>
      </tr>
      <tr>
        <td><strong>IP Address</strong></td>
        <td>The digital phone number of a computer plugged into the internet (e.g., <code>34.93.241.228</code>).</td>
        <td>The private and public addresses Google uses to route internet traffic to our servers.</td>
      </tr>
      <tr>
        <td><strong>Port</strong></td>
        <td>The specific apartment door number in a giant apartment building.</td>
        <td><strong>Port 443</strong> for secure HTTPS websites; <strong>Port 3306</strong> internally for MySQL.</td>
      </tr>
      <tr>
        <td><strong>HTTP</strong></td>
        <td>The polite rules of speaking on the telephone so computers understand each other.</td>
        <td>How your browser asks Google Cloud Run for web pages.</td>
      </tr>
      <tr>
        <td><strong>HTTP GET</strong></td>
        <td><em>"Please give me that page so I can look at it."</em></td>
        <td>When you click "Dashboard" or "Clubs", your browser sends a GET request.</td>
      </tr>
      <tr>
        <td><strong>HTTP POST</strong></td>
        <td><em>"Here is the form I just filled out; please save it in your records."</em></td>
        <td>When you fill out the form to add a student or membership, your browser sends a POST request.</td>
      </tr>
      <tr>
        <td><strong>HTTP Status Codes</strong></td>
        <td>The server's 3-digit mood indicator.</td>
        <td><strong>200 OK</strong> (Success), <strong>404</strong> (Not found), <strong>500</strong> (Server crashed). Checked on <code>/health</code>.</td>
      </tr>
      <tr>
        <td><strong>Docker Image</strong></td>
        <td>The frozen cake recipe written in a cookbook.</td>
        <td>An immutable blueprint created by our <code>Dockerfile</code> containing Python 3.13, Flask, and libraries.</td>
      </tr>
      <tr>
        <td><strong>Docker Container</strong></td>
        <td>The live, freshly baked cake on your table.</td>
        <td>The running, isolated instance of the Docker image executing in memory inside Cloud Run.</td>
      </tr>
      <tr>
        <td><strong>Stateless / Ephemeral</strong></td>
        <td>A goldfish with a 5-second memory. Every time it blinks, it forgets everything.</td>
        <td>Cloud Run container memory resets on restart; which is why all data must live in Cloud SQL!</td>
      </tr>
      <tr>
        <td><strong>Unix / Linux</strong></td>
        <td>The tough, secure operating system that runs 95% of the world's internet servers.</td>
        <td>Our Docker container runs Debian Linux inside Google's data center.</td>
      </tr>
      <tr>
        <td><strong>Unix Domain Socket</strong></td>
        <td>Passing a secret handwritten note through a private slot in the wall between two adjacent rooms.</td>
        <td>Private connection between Cloud Run and Cloud SQL (<code>/cloudsql/...</code>). Zero open internet IP ports.</td>
      </tr>
      <tr>
        <td><strong>Relational Database</strong></td>
        <td>A set of neatly labeled filing boxes connected by matching ID numbers instead of a messy pile of papers.</td>
        <td>Google Cloud SQL running MySQL 8.0, storing our 8 relational tables.</td>
      </tr>
      <tr>
        <td><strong>Primary Key</strong></td>
        <td>Your College PRN or Aadhar card number. Uniquely identifies YOU and cannot belong to anyone else.</td>
        <td><code>student_id</code> in the Students table; <code>club_id</code> in the Clubs table.</td>
      </tr>
      <tr>
        <td><strong>Foreign Key</strong></td>
        <td>Writing your friend's PRN on an event entry pass to prove who the pass belongs to.</td>
        <td><code>student_id</code> and <code>club_id</code> inside the Memberships table linking Students and Clubs.</td>
      </tr>
      <tr>
        <td><strong>Database View</strong></td>
        <td>A bookmarked filter or special pair of sunglasses that lets you look at a summary of data instantly.</td>
        <td><code>ClubSummary</code> view, which joins Clubs and faculty advisors into one clean screen.</td>
      </tr>
      <tr>
        <td><strong>Database Trigger</strong></td>
        <td>A mouse trap or automatic turnstile. When you step on it, it snaps automatically.</td>
        <td><code>trg_increase_member_count</code>: Adds +1 to <code>Clubs.member_count</code> automatically when a member is added.</td>
      </tr>
      <tr>
        <td><strong>Database Cursor</strong></td>
        <td>A robot finger pointing at a list, moving down one row at a time.</td>
        <td>Used in <code>sp_audit_club_counts</code> to inspect and reconcile club counts one by one.</td>
      </tr>
      <tr>
        <td><strong>SQL Injection</strong></td>
        <td>Tricking a bank teller by writing <em>"Give me all money OR 1=1"</em> on a withdrawal slip.</td>
        <td>Prevented 100% by using <strong>parameterized queries</strong> (<code>%s</code> tuples in Flask routes).</td>
      </tr>
    </tbody>
  </table>

  <div class="page-break"></div>

  <!-- PART 2: GOOGLE CLOUD COMPONENTS -->
  <h3>Part 2: Every Google Cloud Component Explained</h3>

  <pre><code>┌─────────────────────────────────────────────────────────────────────────────┐
│                       GOOGLE CLOUD PROJECT                                  │
│                 (project-a4079d46-9d8b-469f-993)                            │
│                                                                             │
│   ┌─────────────────────┐   Underground Socket   ┌──────────────────────┐   │
│   │   GOOGLE CLOUD RUN  │ ═════════════════════> │   GOOGLE CLOUD SQL   │   │
│   │ (Runs our container)│                        │  (Stores our tables) │   │
│   └──────────┬──────────┘                        └──────────────────────┘   │
│              │                                                              │
│              ▼ Assumes Identity Badge                                       │
│   ┌────────────────────────────────┐                                        │
│   │    IAM SERVICE ACCOUNT         │                                        │
│   │       (club-app-sa)            │                                        │
│   └──────────┬─────────────────────┘                                        │
│              │ Has Permission to read                                       │
│              ▼                                                              │
│   ┌────────────────────────────────┐                                        │
│   │     SECRET MANAGER             │                                        │
│   │   (Holds database password)    │                                        │
│   └────────────────────────────────┘                                        │
└─────────────────────────────────────────────────────────────────────────────┘</code></pre>

  <ol>
    <li><strong>Google Cloud Project (<code>project-a4079d46-9d8b-469f-993</code>):</strong>
      <ul>
        <li><em>Layman:</em> Your company locker or folder. Everything you own in Google Cloud is kept inside this one folder.</li>
        <li><em>Technical:</em> The fundamental organizing entity in GCP. All compute resources, billing allocations, IAM policies, and API activations are bounded inside this project ID.</li>
        <li><em>Role in our project:</em> Houses our Cloud Run service, Cloud SQL instance, and Secret Manager vault.</li>
      </ul>
    </li>
    <li><strong>Google Cloud Run (<code>club-management-app</code>):</strong>
      <ul>
        <li><em>Layman (The Smart Taxi):</em> If you buy a car, you pay for it while it sits parked in your garage. Cloud Run is like an Uber: it only shows up and charges you when a passenger needs a ride. When no one is on your website, it sleeps and costs ₹0.00.</li>
        <li><em>Technical (Serverless Container Runtime):</em> A fully managed compute platform based on Knative that executes stateless HTTP containers. It abstracts all server management, automatically provisions SSL certificates, and handles load balancing.</li>
        <li><em>Configuration in our project:</em> <code>min-instances=0</code> (scales to zero when idle for zero cost), <code>max-instances=2</code> (hard ceiling to protect your wallet against traffic surges), Memory: 512MiB, CPU: 1 vCPU.</li>
      </ul>
    </li>
    <li><strong>Google Cloud SQL (<code>club-mysql-instance</code>):</strong>
      <ul>
        <li><em>Layman (The Permanent Underground Bank Safe):</em> Our Python website in Cloud Run can be shut down or updated at any moment. But this database machine NEVER forgets. It has heavy SSD hard drives that protect our student records forever.</li>
        <li><em>Technical (Managed Relational Database):</em> A fully managed MySQL 8.0 enterprise instance running in Mumbai (<code>asia-south1-a</code>). Google manages hardware provisioning, SSD replication, point-in-time recovery, and daily backups.</li>
        <li><em>Configuration in our project:</em> Database: <code>trial_club</code>, Machine Tier: <code>db-f1-micro</code> (~₹0.85/hour), Storage: 10 GB SSD, Public IP Access: Completely disabled (<code>0.0.0.0/0</code> blocked).</li>
      </ul>
    </li>
    <li><strong>Google Secret Manager (<code>club-db-password</code>):</strong>
      <ul>
        <li><em>Layman (The High-Security Vault):</em> A locked digital safe where we put our MySQL password. Our code doesn't have the password written on it. When the app boots up, it shows its ID badge, grabs the password in memory, and immediately locks the safe.</li>
        <li><em>Technical (Key-Management &amp; Secrets Service):</em> A secure, centralized storage system for sensitive metadata. Secrets are encrypted at rest using AES-256 and accessible only via audited IAM API calls.</li>
        <li><em>Role in our project:</em> Version 2 of <code>club-db-password</code> holds the raw password, injected into Cloud Run as an environment variable at runtime.</li>
      </ul>
    </li>
    <li><strong>IAM Service Account (<code>club-app-sa</code>):</strong>
      <ul>
        <li><em>Layman (The Robot Employee's Security Badge):</em> We didn't give our app your personal Google login. We created a robot employee named <code>club-app-sa</code> and gave it a restricted security badge that only opens two doors.</li>
        <li><em>Technical (Identity &amp; Access Management):</em> A specialized Google identity assumed by server applications to make authenticated calls to Google Cloud APIs using short-lived OAuth 2.0 access tokens.</li>
        <li><em>Principle of Least Privilege:</em> Assigned only <code>roles/cloudsql.client</code> (connects to Cloud SQL via proxy) and <code>roles/secretmanager.secretAccessor</code> (reads database password). <em>It cannot create new servers, alter billing, or delete databases.</em></li>
      </ul>
    </li>
    <li><strong>Cloud Build &amp; Artifact Registry:</strong>
      <ul>
        <li><em>Layman (The Factory and The Warehouse):</em> Cloud Build is the factory robot that read our Dockerfile, downloaded Linux, installed Python, packed our code, and sealed the shipping container. Artifact Registry is the warehouse shelf where the container was placed.</li>
        <li><em>Technical:</em> Google's managed CI/CD build pipeline and OCI-compliant container registry.</li>
      </ul>
    </li>
    <li><strong>Cloud Billing &amp; Safety Budget (<code>Safety-Budget-500INR</code>):</strong>
      <ul>
        <li><em>Layman (The Prepaid Balance &amp; Siren):</em> You deposited ₹1,000 via UPI. We set a loud alarm at ₹450 and ₹500 so you never get an unexpected bill.</li>
        <li><em>Technical:</em> A Google Cloud Billing budget with programmatic threshold rules that triggers email alerts at 90% and 100% of ₹500.</li>
      </ul>
    </li>
  </ol>

  <!-- PART 3: THE 1-SECOND ODYSSEY -->
  <h3>Part 3: The Grand "Putting It All Together" Story (The 1-Second Odyssey)</h3>
  <div class="callout callout-success">
    <div class="callout-title">The Complete Timeline of One Click: What happens when an evaluator visits your site:</div>
    <pre><code>Time: 0.00s  👉  Interviewer clicks link in Chrome (Browser)
Time: 0.05s  👉  Google's Mumbai Edge Load Balancer catches the HTTPS request
Time: 0.10s  👉  Cloud Run wakes up our Docker Container
Time: 0.20s  👉  App presents 'club-app-sa' badge to Secret Manager -> Gets Password
Time: 0.30s  👉  App opens Unix Domain Socket -> Asks Cloud SQL: "Run ClubSummary View!"
Time: 0.40s  👉  MySQL runs query inside Mumbai data center -> Hands back 5 clubs
Time: 0.50s  👉  Flask injects data into Bootstrap HTML template
Time: 0.60s  👉  Google sends HTTP 200 OK back to the interviewer's phone
Time: 0.70s  👉  Interviewer's Chrome browser paints the beautiful dashboard!</code></pre>
    <ol>
      <li><strong>The Click (0.00s):</strong> The interviewer clicks your URL. Their browser sends an <strong>HTTP GET /</strong> request over <strong>Port 443</strong> (secure HTTPS).</li>
      <li><strong>The Front Door (0.05s):</strong> Google's global fiber-optic network catches the request in <strong>Mumbai (<code>asia-south1</code>)</strong>. Google validates the SSL certificate so the browser shows the secure green padlock.</li>
      <li><strong>Waking the Worker (0.10s):</strong> Google Cloud Run notices traffic. If the app was sleeping (<code>scale-to-zero</code>), Google boots up our <strong>Docker Container</strong> in RAM.</li>
      <li><strong>Showing the Badge (0.20s):</strong> The Flask app starts up. It needs to connect to MySQL. It doesn't have the password! The app uses its <strong>IAM Service Account badge</strong> (<code>club-app-sa</code>) to ask Secret Manager: <em>"Please give me club-db-password"</em>. Secret Manager decrypts it and hands it over in memory.</li>
      <li><strong>Walking the Underground Tunnel (0.30s):</strong> Now the app connects to Cloud SQL. But remember: Cloud SQL is closed to the public internet! The app slips through the <strong>Unix Domain Socket</strong> (<code>/cloudsql/...</code>). Google's internal private network routes the query directly to MySQL.</li>
      <li><strong>The Database Engine Answers (0.40s):</strong> MySQL receives the query: <code>SELECT * FROM ClubSummary;</code>. The <strong>SQL View</strong> runs, aggregates the student counts for CSI, EDC, Zephyr, SWD, and CSA, and hands the records back across the Unix socket.</li>
      <li><strong>The Delivery (0.50s - 0.70s):</strong> <strong>Flask</strong> takes those 5 club rows, slides them into the HTML table template, and hands the complete HTML code back to Google. Google replies to the phone: <strong>HTTP 200 OK</strong>. The interviewer's browser renders the navigation bar, live cards, and student counts!</li>
    </ol>
  </div>

  <!-- SECTION II: INTEGRATED DOCS -->
  <div class="page-break"></div>
  <div style="border-top: 2px solid #1e40af; margin-top: 15px; padding-top: 10px;">
    <span class="badge" style="background:#1e40af; color:#fff; font-size:9pt; padding:4px 10px;">SECTION II</span>
    <h2 style="border:none; margin-top:5px; color:#1e3a8a;">100% Comprehensive Integration of Repository Documentation (docs/)</h2>
    <p>Every single markdown document from the project repository has been compiled and integrated below in its entirety:</p>
  </div>

  {"".join(docs_html_sections)}

</body>
</html>
"""

    output_html = os.path.join(os.path.dirname(__file__), "complete_master_guide.html")
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"Generated {output_html} successfully ({len(html_template)} bytes).")

    # 3. Compile to PDF with Headless Chrome
    output_pdf = os.path.join(os.path.dirname(__file__), "complete_cloud_master_guide.pdf")
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    
    cmd = [
        chrome_path,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header",
        f"--print-to-pdf={output_pdf}",
        output_html
    ]
    print("Running Chrome to generate PDF...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if os.path.exists(output_pdf):
        size_kb = os.path.getsize(output_pdf) / 1024
        print(f"SUCCESS: {output_pdf} generated ({size_kb:.1f} KB)!")
    else:
        print(f"ERROR: PDF generation failed! Stderr: {result.stderr}")

if __name__ == "__main__":
    build()
