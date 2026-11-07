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
from flask import Blueprint, request, session, redirect, url_for, flash, jsonify, render_template
from app.user_model import authenticate_user, register_user, detect_role_from_email, get_all_users_count

auth_bp = Blueprint("auth", __name__)

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
        "title": "Super Admin / Principal",
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
    """Retrieve active session role. Returns None if unauthenticated."""
    return session.get("role")

def get_current_user():
    """Retrieve active user display name."""
    return session.get("user_name", "Guest Evaluator")

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
    role = get_current_role() or "guest"
    meta = ROLE_METADATA.get(role, ROLE_METADATA["guest"])
    return jsonify({
        "role": role,
        "is_authenticated": session.get("role") is not None,
        "user_name": get_current_user(),
        "user_email": session.get("user_email", ""),
        "meta": meta
    })

@auth_bp.route("/api/auth/detect-role", methods=["POST"])
def api_detect_role():
    """Real-time API endpoint to detect role as user types their email."""
    data = request.get_json() or {}
    email = data.get("email", "")
    role, role_title, error = detect_role_from_email(email)
    return jsonify({
        "role": role,
        "role_title": role_title,
        "error": error
    })

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Renders the Switchd-inspired login page or processes authentication credentials.
    """
    if request.method == "GET":
        # If already logged in, redirect to cockpit
        if session.get("role"):
            return redirect(url_for("main.dashboard"))
        mode = request.args.get("mode", "login")
        return render_template("auth/login.html", mode=mode, total_users=get_all_users_count())

    # POST: Process login
    if request.is_json:
        data = request.get_json() or {}
        email = data.get("email", "").strip().lower()
        password = data.get("password", "").strip()
        requested_role = data.get("role", "").strip().lower()
    else:
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        requested_role = request.form.get("role", "").strip().lower()

    # Quick Switcher fallback support
    if requested_role and requested_role in ROLE_METADATA and not email:
        session["role"] = requested_role
        session["user_name"] = ROLE_METADATA[requested_role]["title"]
        session["user_email"] = f"{requested_role}@vit.edu"
        session.modified = True
        return jsonify({
            "status": "ok",
            "role": requested_role,
            "role_label": ROLE_METADATA[requested_role]["title"],
            "user_name": session["user_name"],
            "redirect_url": url_for("main.dashboard")
        }), 200

    err, user = authenticate_user(email, password)
    if err:
        if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"status": "error", "message": err}), 401
        flash(err, "danger")
        return render_template("auth/login.html", mode="login", email=email, total_users=get_all_users_count()), 401

    # Session persistence
    session["role"] = user["role"]
    session["user_name"] = user["name"]
    session["user_email"] = user["email"]
    session.modified = True

    if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "status": "ok",
            "role": user["role"],
            "role_label": user["role_title"],
            "user_name": user["name"],
            "message": f"Welcome back, {user['name']}!",
            "redirect_url": url_for("main.dashboard")
        }), 200

    flash(f"Welcome back, {user['name']}! Signed in as {user['role_title']}.", "success")
    return redirect(url_for("main.dashboard"))

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """
    Renders sign up page or registers a new user with strictly validated VIT email.
    """
    if request.method == "GET":
        if session.get("role"):
            return redirect(url_for("main.dashboard"))
        return render_template("auth/login.html", mode="signup", total_users=get_all_users_count())

    # POST: Process registration
    if request.is_json:
        data = request.get_json() or {}
        name = data.get("name", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "").strip()
    else:
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

    err, user = register_user(email, password, name)
    if err:
        if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"status": "error", "message": err}), 400
        flash(err, "warning")
        return render_template("auth/login.html", mode="signup", name=name, email=email, total_users=get_all_users_count()), 400

    # Auto-login upon registration
    session["role"] = user["role"]
    session["user_name"] = user["name"]
    session["user_email"] = user["email"]
    session.modified = True

    if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "status": "ok",
            "role": user["role"],
            "role_label": user["role_title"],
            "user_name": user["name"],
            "message": f"Account created successfully as {user['role_title']}!",
            "redirect_url": url_for("main.dashboard")
        }), 200

    flash(f"Account registered successfully as {user['role_title']}!", "success")
    return redirect(url_for("main.dashboard"))

@auth_bp.route("/guest", methods=["GET", "POST"])
def guest_mode():
    """
    One-click Guest / Viva demonstration trigger.
    Immediately grants full unrestricted demo access without credentials.
    """
    session["role"] = "guest"
    session["user_name"] = "Guest Evaluator (Unrestricted Demo Mode)"
    session["user_email"] = "guest@vit.edu"
    session.modified = True
    
    if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "status": "ok",
            "role": "guest",
            "role_label": "Guest (Full Demo)",
            "user_name": session["user_name"],
            "message": "Full Unrestricted Demo Access Activated!",
            "redirect_url": url_for("main.dashboard")
        }), 200
        
    flash("Guest Demo Mode Activated: 100% Unrestricted access to all 8 tables, triggers, and cursors.", "success")
    return redirect(url_for("main.dashboard"))

@auth_bp.route("/logout")
def logout():
    """Clears user session and redirects to the gatekeeper login page."""
    session.clear()
    flash("You have been signed out. Please sign in or click Guest to continue.", "info")
    return redirect(url_for("auth.login"))
