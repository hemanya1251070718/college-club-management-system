"""
ClubHub Enterprise DBMS - Authentication and Role Management (RBAC Engine)
Provides Role-Based Access Control designed for academic evaluation & demonstration.
Roles:
  - 'guest': Default unrestricted demo mode (all 8 triggers, 8 cursors, CRUD enabled for seamless evaluation)
  - 'admin': Principal / Super Admin / System Architect (full administrative power)
  - 'president': Club President (executive governance, single-president trigger tests, administrative procedures)
  - 'coordinator': Faculty Coordinator & Club Secretary (charter governance, event management, attendance Trigger 7)
  - 'member': Student Member & Core Member (self-service event registration, verified reviews, Trigger 1 enrolment)
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
        "can_view_triggers": True,
        "allowed_triggers": [1, 2, 3, 4, 5, 6, 7, 8],
        "allowed_procs": [1, 2, 3, 4, 5, 6, 7, 8]
    },
    "admin": {
        "title": "Super Admin / Principal",
        "badge_class": "badge-status success",
        "description": "Full administrative control, database schema initialization, and raw SQL cursor triggers.",
        "can_edit": True,
        "can_execute_procs": True,
        "can_view_triggers": True,
        "allowed_triggers": [1, 2, 3, 4, 5, 6, 7, 8],
        "allowed_procs": [1, 2, 3, 4, 5, 6, 7, 8]
    },
    "president": {
        "title": "Club President",
        "badge_class": "badge-status warning",
        "description": "Executive club governance, single-president enforcement, and administrative procedures.",
        "can_edit": True,
        "can_execute_procs": True,
        "can_view_triggers": True,
        "allowed_triggers": [1, 2, 3, 5, 6, 8],
        "allowed_procs": [1, 6, 7, 8]
    },
    "coordinator": {
        "title": "Faculty Coordinator / Secretary",
        "badge_class": "badge-status info",
        "description": "Authorized to manage student charters, schedule events, record attendance, and run operational procedures.",
        "can_edit": True,
        "can_execute_procs": True,
        "can_view_triggers": True,
        "allowed_triggers": [1, 2, 4, 5, 6, 7],
        "allowed_procs": [2, 3, 4, 5]
    },
    "manager": {  # Backwards compatibility alias for coordinator
        "title": "Faculty Coordinator / Secretary",
        "badge_class": "badge-status info",
        "description": "Authorized to manage student charters, schedule events, record attendance, and run operational procedures.",
        "can_edit": True,
        "can_execute_procs": True,
        "can_view_triggers": True,
        "allowed_triggers": [1, 2, 4, 5, 6, 7],
        "allowed_procs": [2, 3, 4, 5]
    },
    "member": {
        "title": "Student Member / Core Member",
        "badge_class": "badge-status neutral",
        "description": "Exploratory directory access, self-service event registration, and verified review submissions.",
        "can_edit": False,
        "can_execute_procs": False,
        "can_view_triggers": True,
        "allowed_triggers": [1, 5, 6],
        "allowed_procs": []
    }
}

def get_current_role():
    """Retrieve active session role. Returns None if unauthenticated."""
    return session.get("role")

def get_current_user():
    """Retrieve active user display name."""
    return session.get("user_name", "Guest Evaluator")

def get_current_student_id():
    """Retrieve logged-in student's student_id (e.g. 'CE25-0718'), or None."""
    return session.get("student_id")

def can_test_trigger(trigger_num):
    """Checks whether the currently active role is authorized to fire Trigger N."""
    role = get_current_role() or "guest"
    meta = ROLE_METADATA.get(role, ROLE_METADATA["guest"])
    return int(trigger_num) in meta.get("allowed_triggers", [1, 2, 3, 4, 5, 6, 7, 8])

def can_test_procedure(proc_num):
    """Checks whether the currently active role is authorized to execute Procedure N."""
    role = get_current_role() or "guest"
    meta = ROLE_METADATA.get(role, ROLE_METADATA["guest"])
    return int(proc_num) in meta.get("allowed_procs", [1, 2, 3, 4, 5, 6, 7, 8])

def write_required(redirect_endpoint="main.dashboard"):
    """
    Decorator for write endpoints (create, edit, delete).
    Allows 'admin', 'president', 'coordinator', 'manager', and 'guest'.
    Restricts 'member' role and redirects with informative notification.
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            role = get_current_role()
            if role == "member":
                flash("Access Restricted: Student Members cannot modify club charters or core database records. Switch to Coordinator, President, or Guest mode to edit.", "warning")
                return redirect(url_for(redirect_endpoint))
            return view_func(*args, **kwargs)
        return wrapper
    return decorator

def execute_required(redirect_endpoint="main.procedures_hub"):
    """
    Decorator for stored procedure execution.
    Denies 'member' role. Permits 'admin', 'president', 'coordinator', and 'guest'.
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            role = get_current_role()
            if role == "member":
                flash("Access Restricted: Student Members are restricted from running backend stored procedure cursors. Switch to President, Coordinator, or Guest mode.", "warning")
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
        "student_id": session.get("student_id"),
        "club_id": session.get("club_id"),
        "club_role": session.get("club_role"),
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
    Renders login page or processes authentication credentials.
    """
    if request.method == "GET":
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
        session["student_id"] = None
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
    session["student_id"] = user.get("student_id")
    session["prn"] = user.get("prn")
    session["club_id"] = user.get("club_id")
    session["club_role"] = user.get("club_role")
    session.modified = True

    if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "status": "ok",
            "role": user["role"],
            "role_label": user["role_title"],
            "user_name": user["name"],
            "student_id": user.get("student_id"),
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
        flash(err, "danger")
        return render_template("auth/login.html", mode="signup", email=email, name=name, total_users=get_all_users_count()), 400

    # Auto sign-in after successful registration
    session["role"] = user["role"]
    session["user_name"] = user["name"]
    session["user_email"] = user["email"]
    session["student_id"] = user.get("student_id")
    session["prn"] = user.get("prn")
    session.modified = True

    if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "status": "ok",
            "role": user["role"],
            "role_label": user["role_title"],
            "user_name": user["name"],
            "student_id": user.get("student_id"),
            "message": f"Account created! Welcome, {user['name']}.",
            "redirect_url": url_for("main.dashboard")
        }), 200

    flash(f"Account created successfully! Signed in as {user['role_title']}.", "success")
    return redirect(url_for("main.dashboard"))

@auth_bp.route("/guest", methods=["GET", "POST"])
@auth_bp.route("/guest-mode", methods=["GET", "POST"])
def guest_mode():
    """
    Activates unrestricted Guest Evaluator mode.
    Guarantees that evaluators/professors can inspect all 8 triggers, 8 cursors, and CRUD actions.
    """
    session["role"] = "guest"
    session["user_name"] = "Guest Evaluator (Full Demo)"
    session["user_email"] = "guest.evaluator@vit.edu"
    session["student_id"] = None
    session.modified = True
    if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "status": "ok",
            "role": "guest",
            "role_label": "Guest (Full Demo)",
            "user_name": "Guest Evaluator (Full Demo)",
            "redirect_url": url_for("main.dashboard")
        }), 200
    flash("Switched to Guest Evaluator mode: Unrestricted access to all 8 triggers, 8 cursors, and management interfaces.", "success")
    return redirect(url_for("main.dashboard"))

@auth_bp.route("/logout")
def logout():
    """
    Clears session state and redirects to gatekeeper login page.
    """
    session.clear()
    session.modified = True
    flash("You have been signed out. Enter credentials or click Guest to continue.", "info")
    return redirect(url_for("auth.login"))
