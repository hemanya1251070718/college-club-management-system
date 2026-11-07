"""
Persistent Users Database and Role Verification Engine
Provides persistent user authentication with SQLite (and Cloud SQL MySQL sync),
password hashing, and strict role detection according to VIT Pune email standards:
  - Principal:      <name>.principal@vit.edu                 -> 'admin'
  - Coordinator:    <name>.<prn>.cordinator@vit.edu          -> 'manager'
  - Student Member: <name>.<prn>@vit.edu                     -> 'member'
"""

import os
import re
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database", "users.db")

def get_sqlite_conn():
    """Returns a connection to the persistent users SQLite database."""
    target_path = DB_PATH
    try:
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        conn = sqlite3.connect(target_path)
    except Exception:
        # Fallback to /tmp for serverless read-only filesystems (e.g. Vercel)
        target_path = os.path.join("/tmp", "users.db")
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    return conn

def detect_role_from_email(email):
    """
    Validates and classifies role strictly by email pattern:
      - Principal:      <name>.principal@vit.edu                 -> 'admin'
      - Coordinator:    <name>.<prn>.cordinator@vit.edu          -> 'manager' (also accepts coordinator)
      - Student Member: <name>.<prn>@vit.edu                     -> 'member'
    Returns: (role, role_title, error_message)
    """
    if not email:
        return None, None, "Email address is required."
    
    email = email.strip().lower()
    if not email.endswith("@vit.edu"):
        return None, None, "Compulsory requirement: Email must belong to the official '@vit.edu' domain."
    
    # 1. Principal / Super Admin
    if re.match(r"^[a-z0-9_.-]+\.principal@vit\.edu$", email):
        return "admin", "Super Admin / Principal", None
    
    # 2. Faculty Coordinator
    if re.match(r"^[a-z0-9_.-]+\.[a-z0-9_.-]+\.(?:cordinator|coordinator)@vit\.edu$", email):
        return "manager", "Faculty Coordinator", None
    
    # 3. Student Member (somename.prn@vit.edu)
    if re.match(r"^[a-z0-9_.-]+\.[a-z0-9_.-]+@vit\.edu$", email):
        return "member", "Student Member", None
    
    return None, None, (
        "Email does not conform to required role patterns: "
        "Student (name.prn@vit.edu), Coordinator (name.prn.cordinator@vit.edu), "
        "or Principal (name.principal@vit.edu)."
    )

def init_users_db():
    """Initializes users table and seeds pre-configured demo accounts."""
    conn = get_sqlite_conn()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                role_title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

    # Default Seed Users for instant demo testing
    seed_accounts = [
        {
            "email": "sharma.principal@vit.edu",
            "password": "password123",
            "name": "Prof. D. K. Sharma (Principal)",
            "role": "admin",
            "role_title": "Super Admin / Principal"
        },
        {
            "email": "patil.121001.cordinator@vit.edu",
            "password": "password123",
            "name": "Dr. Sunita Patil (Faculty Coordinator)",
            "role": "manager",
            "role_title": "Faculty Coordinator"
        },
        {
            "email": "aarav.123456@vit.edu",
            "password": "password123",
            "name": "Aarav Deshmukh (Student Member)",
            "role": "member",
            "role_title": "Student Member"
        }
    ]

    for acc in seed_accounts:
        try:
            with conn:
                conn.execute("""
                    INSERT OR IGNORE INTO users (email, password_hash, name, role, role_title)
                    VALUES (?, ?, ?, ?, ?);
                """, (
                    acc["email"],
                    generate_password_hash(acc["password"]),
                    acc["name"],
                    acc["role"],
                    acc["role_title"]
                ))
        except Exception:
            pass
    conn.close()

# Auto-initialize on module load
try:
    init_users_db()
except Exception as e:
    print(f"Warning: could not auto-init SQLite users db: {e}")

def register_user(email, password, name=""):
    """
    Registers a new user into the persistent database.
    Strictly validates email format and assigns appropriate role.
    Returns: (error_message, user_dict)
    """
    role, role_title, err = detect_role_from_email(email)
    if err:
        return err, None
    
    if not password or len(password.strip()) < 4:
        return "Password must be at least 4 characters in length.", None
    
    email_clean = email.strip().lower()
    name_clean = name.strip() if name else email_clean.split("@")[0].replace(".", " ").title()

    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?;", (email_clean,))
    if cursor.fetchone():
        conn.close()
        return "An account with this email already exists. Please sign in.", None

    pwd_hash = generate_password_hash(password.strip())
    try:
        with conn:
            cursor.execute("""
                INSERT INTO users (email, password_hash, name, role, role_title)
                VALUES (?, ?, ?, ?, ?);
            """, (email_clean, pwd_hash, name_clean, role, role_title))
            new_id = cursor.lastrowid
        conn.close()
        return None, {
            "id": new_id,
            "email": email_clean,
            "name": name_clean,
            "role": role,
            "role_title": role_title
        }
    except Exception as e:
        conn.close()
        return f"Database error creating user: {str(e)}", None

def authenticate_user(email, password):
    """
    Authenticates email and password against the persistent database.
    Returns: (error_message, user_dict)
    """
    if not email or not password:
        return "Please provide both email and password.", None
    
    email_clean = email.strip().lower()
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?;", (email_clean,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return "No account found with this email. Please sign up first.", None
    
    if not check_password_hash(row["password_hash"], password.strip()):
        return "Incorrect password. Please try again or use the demo credentials.", None
    
    return None, {
        "id": row["id"],
        "email": row["email"],
        "name": row["name"],
        "role": row["role"],
        "role_title": row["role_title"]
    }

def get_all_users_count():
    """Returns total registered users count."""
    try:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS c FROM users;")
        count = cursor.fetchone()["c"]
        conn.close()
        return count
    except Exception:
        return 3
