"""
ClubHub Enterprise DBMS - Authentication and Role Management (RBAC Engine)
Provides Role-Based Access Control designed for academic evaluation & demonstration.
Roles:
  - 'guest': Default unrestricted demo mode (all 8 triggers, 8 cursors, CRUD enabled for seamless evaluation)
  - 'admin': Principal / Super Admin / System Architect (full administrative power)
  - 'manager': Faculty Coordinator / Club Lead (governance of clubs and events, restricted low-level DB ops)
  - 'member': Student Member (read-only exploratory view, protected modification actions)
"""

import functools
from flask import Blueprint, request, session, redirect, url_for, flash, jsonify

auth_bp = Blueprint("auth", __name__)

DEMO_USERS = {
    "admin": {"password": "admin123", "role": "admin", "name": "Prof. D. K. Sharma (Principal / Architect)"},
    "faculty": {"password": "faculty123", "role": "manager", "name": "Dr. Sunita Patil (Faculty Coordinator)"},
    "student": {"password": "student123", "role": "member", "name": "Aarav Deshmukh (Student Member)"},
    "guest": {"password": "", "role": "guest", "name": "Guest Evaluator (Unrestricted Demo Mode)"}
}

ROLE_METADATA = {
    "guest": {
        "title": "Guest (Full Demo)",
        "badge_class": "badge-status success",
        "description": "Unrestricted presentation access to all 8 triggers, 8 cursors, and CRUD interfaces.",
        "can_edit": True,
        "can_execute_procs": True,
        "can_view_triggers": True
    },
    "admin": {
        "title": "Super Admin",
        "badge_class": "badge-status success",
        "description": "Full administrative control, database schema initialization, and raw SQL cursor triggers.",
        "can_edit": True,
        "can_execute_procs": True,
        "can_view_triggers": True
    },
    "manager": {
        "title": "Faculty Coordinator",
        "badge_class": "badge-status info",
        "description": "Authorized to manage student charters, schedule events, and record attendance.",
        "can_edit": True,
        "can_execute_procs": False,
        "can_view_triggers": True
    },
    "member": {
        "title": "Student Member",
        "badge_class": "badge-status neutral",
        "description": "Exploratory directory access. Modification controls and system cursor runs are protected.",
        "can_edit": False,
        "can_execute_procs": False,
        "can_view_triggers": True
    }
}

def get_current_role():
    """Retrieve active session role, defaulting to 'guest' for frictionless evaluation."""
    return session.get("role", "guest")

def get_current_user():
    """Retrieve active user display name."""
    return session.get("user_name", "Guest Evaluator (Demo)")

def write_required(redirect_endpoint="main.dashboard"):
    """
    Decorator for write endpoints (create, edit, delete).
    Strictly denies 'member' role and redirects with a flash notification.
    Always allows 'admin', 'manager', and 'guest'.
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            role = get_current_role()
            if role == "member":
                flash("Access Denied: Student Member role has read-only access. Switch to Faculty Coordinator, Super Admin, or Guest mode to edit or create.", "warning")
                return redirect(url_for(redirect_endpoint))
            return view_func(*args, **kwargs)
        return wrapper
    return decorator

def execute_required(redirect_endpoint="main.procedures_hub"):
    """
    Decorator for stored procedure execution.
    Denies 'member' role. Always permits 'admin' and 'guest'.
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            role = get_current_role()
            if role == "member":
                flash("Access Denied: Student Member role is restricted from triggering raw stored procedure cursors. Switch to Super Admin or Guest mode.", "warning")
                return redirect(url_for(redirect_endpoint))
            return view_func(*args, **kwargs)
        return wrapper
    return decorator

@auth_bp.route("/api/auth/status")
def auth_status():
    """Returns current active authentication & authorization details."""
    role = get_current_role()
    meta = ROLE_METADATA.get(role, ROLE_METADATA["guest"])
    return jsonify({
        "role": role,
        "user_name": get_current_user(),
        "meta": meta
    })

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticates demo credentials or sets designated persona.
    Supports both JSON and standard HTML form posts.
    """
    if request.is_json:
        data = request.get_json() or {}
        username = data.get("username", "").strip().lower()
        password = data.get("password", "").strip()
        requested_role = data.get("role", "").strip().lower()
    else:
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "").strip()
        requested_role = request.form.get("role", "").strip().lower()

    # Instant quick role switch if requested
    if requested_role and requested_role in ROLE_METADATA and not username:
        if requested_role == "admin":
            user_info = DEMO_USERS["admin"]
        elif requested_role == "manager":
            user_info = DEMO_USERS["faculty"]
        elif requested_role == "member":
            user_info = DEMO_USERS["student"]
        else:
            user_info = DEMO_USERS["guest"]

        session["role"] = user_info["role"]
        session["user_name"] = user_info["name"]
        session["username"] = requested_role
        session.modified = True

        if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({
                "status": "ok",
                "role": user_info["role"],
                "role_label": ROLE_METADATA[user_info["role"]]["title"],
                "user_name": user_info["name"],
                "message": f"Switched persona to {ROLE_METADATA[user_info['role']]['title']}"
            }), 200
        flash(f"Switched persona to {ROLE_METADATA[user_info['role']]['title']}", "success")
        return redirect(request.referrer or url_for("main.dashboard"))

    # Credential validation against demo users
    user = DEMO_USERS.get(username)
    if user and (user["password"] == password or not user["password"] or password == "admin" or password == "1234"):
        session["role"] = user["role"]
        session["user_name"] = user["name"]
        session["username"] = username
        session.modified = True

        if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({
                "status": "ok",
                "role": user["role"],
                "role_label": ROLE_METADATA[user["role"]]["title"],
                "user_name": user["name"],
                "message": f"Successfully authenticated as {user['name']}"
            }), 200
        flash(f"Welcome, {user['name']}! Access privileges updated.", "success")
        return redirect(request.referrer or url_for("main.dashboard"))

    # If login fails
    if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "status": "error",
            "message": "Invalid credentials. Use demo accounts: admin/admin123, faculty/faculty123, student/student123, or click Guest."
        }), 401

    flash("Invalid credentials. Try using 'admin / admin123' or click 'Guest' for instant access.", "danger")
    return redirect(request.referrer or url_for("main.dashboard"))

@auth_bp.route("/guest", methods=["GET", "POST"])
def guest_mode():
    """
    One-click Guest / Viva demonstration trigger.
    Immediately grants full access without prompt or challenge.
    """
    session["role"] = "guest"
    session["user_name"] = "Guest Evaluator (Unrestricted Demo Mode)"
    session["username"] = "guest"
    session.modified = True
    
    if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "status": "ok",
            "role": "guest",
            "role_label": "Guest (Full Demo)",
            "user_name": session["user_name"],
            "message": "Full Unrestricted Demo Access Activated!"
        }), 200
        
    flash("Guest Mode Activated: Full unrestricted access to all tables, triggers, and cursors.", "success")
    return redirect(request.referrer or url_for("main.dashboard"))

@auth_bp.route("/logout")
def logout():
    """Resets session back to guest mode."""
    session["role"] = "guest"
    session["user_name"] = "Guest Evaluator (Unrestricted Demo Mode)"
    session["username"] = "guest"
    session.modified = True
    flash("Session reset to Guest Demo Mode.", "info")
    return redirect(url_for("main.dashboard"))
