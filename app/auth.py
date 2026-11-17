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
from app.memberships_data import get_student_personas, classify_role_tier
from app.seed_users import SEED_USERS

auth_bp = Blueprint("auth", __name__)

ROLE_METADATA = {
    "guest": {
        "title": "Guest (Full Demo)",
        "badge_class": "badge-status success",
        "description": "Unrestricted presentation access to all 8 triggers, 8 cursors, and CRUD interfaces across all clubs.",
        "can_edit": True,
        "can_execute_procs": True,
        "can_view_triggers": True,
        "can_events": True,
        "can_memberships": True,
        "can_leads": True,
        "allowed_triggers": [1, 2, 3, 4, 5, 6, 7, 8],
        "allowed_procs": ["audit", "recruitment", "budget", "close_events", "deactivate", "promote", "grad", "privacy", 1, 2, 3, 4, 5, 6, 7, 8]
    },
    "admin": {
        "title": "Super Admin / Principal",
        "badge_class": "badge-status success",
        "description": "Full administrative control, database schema management, and raw SQL cursor triggers campus-wide.",
        "can_edit": True,
        "can_execute_procs": True,
        "can_view_triggers": True,
        "can_events": True,
        "can_memberships": True,
        "can_leads": True,
        "allowed_triggers": [1, 2, 3, 4, 5, 6, 7, 8],
        "allowed_procs": ["audit", "recruitment", "budget", "close_events", "deactivate", "promote", "grad", "privacy", 1, 2, 3, 4, 5, 6, 7, 8]
    },
    "president": {
        "title": "Club President",
        "badge_class": "badge-status warning",
        "description": "Executive club governance: full operational authority over their designated club's events, memberships, and procedures.",
        "can_edit": True,
        "can_execute_procs": True,
        "can_view_triggers": True,
        "can_events": True,
        "can_memberships": True,
        "can_leads": True,
        "allowed_triggers": [1, 2, 3, 4, 5, 6, 7, 8],
        "allowed_procs": ["audit", "recruitment", "budget", "close_events", "deactivate", "promote", "grad", "privacy", 1, 2, 3, 4, 5, 6, 7, 8]
    },
    "lead": {
        "title": "Club Lead",
        "badge_class": "badge-status info",
        "description": "Club leadership: authorized for club charter updates, event management, membership roster records, and triggers/procedures.",
        "can_edit": True,
        "can_execute_procs": True,
        "can_view_triggers": True,
        "can_events": True,
        "can_memberships": True,
        "can_leads": True,
        "allowed_triggers": [1, 2, 3, 4, 5, 6, 7, 8],
        "allowed_procs": ["audit", "recruitment", "budget", "close_events", "deactivate", "promote", "grad", "privacy", 1, 2, 3, 4, 5, 6, 7, 8]
    },
    "coordinator": {
        "title": "Event Coordinator",
        "badge_class": "badge-status info",
        "description": "Event management and attendance operations for their designated club. (Cannot modify memberships or club charters).",
        "can_edit": True,
        "can_execute_procs": True,
        "can_view_triggers": True,
        "can_events": True,
        "can_memberships": False,
        "can_leads": False,
        "allowed_triggers": [1, 2, 4, 5, 6, 7],
        "allowed_procs": ["recruitment", "budget", "close_events", "deactivate", "promote", "privacy", 2, 3, 4, 5, 6, 8]
    },
    "secretary": {
        "title": "Club Secretary",
        "badge_class": "badge-status info",
        "description": "Membership roster management and student enrollment for their designated club. (Cannot create/manage events or charters).",
        "can_edit": True,
        "can_execute_procs": True,
        "can_view_triggers": True,
        "can_events": False,
        "can_memberships": True,
        "can_leads": False,
        "allowed_triggers": [1, 2, 3, 4],
        "allowed_procs": ["audit", "recruitment", "deactivate", "promote", 1, 2, 5, 6]
    },
    "manager": {  # Backwards compatibility alias for lead
        "title": "Club Lead / Manager",
        "badge_class": "badge-status info",
        "description": "Club leadership operations.",
        "can_edit": True,
        "can_execute_procs": True,
        "can_view_triggers": True,
        "can_events": True,
        "can_memberships": True,
        "can_leads": True,
        "allowed_triggers": [1, 2, 3, 4, 5, 6, 7, 8],
        "allowed_procs": ["audit", "recruitment", "budget", "close_events", "deactivate", "promote", "grad", "privacy", 1, 2, 3, 4, 5, 6, 7, 8]
    },
    "member": {
        "title": "Student Member",
        "badge_class": "badge-status neutral",
        "description": "Exploratory directory access, self-service event registration, and verified review submissions.",
        "can_edit": False,
        "can_execute_procs": False,
        "can_view_triggers": True,
        "can_events": False,
        "can_memberships": False,
        "can_leads": False,
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

def is_club_authorized(target_club_id):
    """
    Tenant Boundary Guard:
    Verifies if active user is authorized to perform operations for target_club_id.
    - 'admin' and 'guest' have campus-wide access across all clubs.
    - 'president', 'lead', 'coordinator', and 'secretary' are strictly locked to session['club_id'].
    """
    role = get_current_role() or "guest"
    if role in ["admin", "guest"]:
        return True
    user_club = session.get("club_id")
    if not user_club or not target_club_id:
        return False
    return str(target_club_id).strip().upper() == str(user_club).strip().upper()

def can_manage_events():
    """Event operations can ONLY be handled by President, Lead, and Coordinator (plus Admin and Guest)."""
    role = get_current_role() or "guest"
    return role in ["admin", "guest", "president", "lead", "coordinator", "manager"]

def can_manage_memberships():
    """Membership operations (Secretary duties) can ONLY be handled by Secretary, President, and Lead (plus Admin and Guest)."""
    role = get_current_role() or "guest"
    return role in ["admin", "guest", "president", "lead", "secretary", "manager"]

def can_manage_lead():
    """Club charter & lead operations can ONLY be handled by Lead and President (plus Admin and Guest)."""
    role = get_current_role() or "guest"
    return role in ["admin", "guest", "president", "lead", "manager"]

def can_test_trigger(trigger_num):
    """Checks whether the currently active role is authorized to fire Trigger N."""
    role = get_current_role() or "guest"
    meta = ROLE_METADATA.get(role, ROLE_METADATA["guest"])
    return int(trigger_num) in meta.get("allowed_triggers", [1, 2, 3, 4, 5, 6, 7, 8])

def can_test_procedure(proc_id):
    """Checks whether the currently active role is authorized to execute Procedure N."""
    role = get_current_role() or "guest"
    meta = ROLE_METADATA.get(role, ROLE_METADATA["guest"])
    allowed = meta.get("allowed_procs", [])
    try:
        p_int = int(proc_id)
        if p_int in allowed:
            return True
    except (ValueError, TypeError):
        pass
    return str(proc_id).strip().lower() in [str(x).strip().lower() for x in allowed]

def event_write_required(redirect_endpoint="main.list_events"):
    """
    Decorator for Event CRUD operations.
    Allowed: 'admin', 'guest', 'president', 'lead', 'coordinator'.
    Denied: 'secretary', 'member'.
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            role = get_current_role()
            if role == "secretary":
                flash("Access Restricted: Club Secretaries handle membership records and cannot create, edit, or delete campus events. Event operations are reserved for Event Coordinators, Leads, and Presidents.", "warning")
                return redirect(url_for(redirect_endpoint))
            elif role == "member":
                flash("Access Restricted: Student Members cannot create, edit, or delete campus events. Switch to Coordinator, Lead, President, or Guest mode.", "warning")
                return redirect(url_for(redirect_endpoint))
            elif not can_manage_events():
                flash("Access Restricted: Insufficient privileges for event operations.", "warning")
                return redirect(url_for(redirect_endpoint))
            return view_func(*args, **kwargs)
        return wrapper
    return decorator

def membership_write_required(redirect_endpoint="main.list_memberships"):
    """
    Decorator for Membership CRUD operations.
    Allowed: 'admin', 'guest', 'president', 'lead', 'secretary'.
    Denied: 'coordinator', 'member'.
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            role = get_current_role()
            if role == "coordinator":
                flash("Access Restricted: Event Coordinators manage event logistics and cannot modify membership rosters or enroll members. Membership operations are reserved for Club Secretaries, Leads, and Presidents.", "warning")
                return redirect(url_for(redirect_endpoint))
            elif role == "member":
                flash("Access Restricted: Student Members cannot enroll, edit, or delete club memberships. Switch to Secretary, Lead, President, or Guest mode.", "warning")
                return redirect(url_for(redirect_endpoint))
            elif not can_manage_memberships():
                flash("Access Restricted: Insufficient privileges for membership operations.", "warning")
                return redirect(url_for(redirect_endpoint))
            return view_func(*args, **kwargs)
        return wrapper
    return decorator

def lead_write_required(redirect_endpoint="main.list_clubs"):
    """
    Decorator for Club Charter operations.
    Allowed: 'admin', 'guest', 'president', 'lead'.
    Denied: 'coordinator', 'secretary', 'member'.
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            role = get_current_role()
            if not can_manage_lead():
                flash("Access Restricted: Club charter updates require Club Lead or President authority. Coordinators, Secretaries, and Members cannot modify charters.", "warning")
                return redirect(url_for(redirect_endpoint))
            return view_func(*args, **kwargs)
        return wrapper
    return decorator

def write_required(redirect_endpoint="main.dashboard"):
    """
    General write decorator for legacy routes.
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            role = get_current_role()
            if role == "member":
                flash("Access Restricted: Student Members cannot modify core database records. Switch to Lead, President, or Guest mode to edit.", "warning")
                return redirect(url_for(redirect_endpoint))
            return view_func(*args, **kwargs)
        return wrapper
    return decorator

def execute_required(redirect_endpoint="main.procedures_hub"):
    """
    Decorator for stored procedure execution.
    Denies 'member' role.
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            role = get_current_role()
            if role == "member":
                flash("Access Restricted: Student Members are restricted from running backend stored procedure cursors. Switch to President, Lead, Coordinator, Secretary, or Guest mode.", "warning")
                return redirect(url_for(redirect_endpoint))
            return view_func(*args, **kwargs)
        return wrapper
    return decorator

@auth_bp.app_context_processor
def inject_auth_helpers():
    return {
        "is_club_authorized": is_club_authorized,
        "can_manage_events": can_manage_events,
        "can_manage_memberships": can_manage_memberships,
        "can_manage_lead": can_manage_lead,
        "can_test_trigger": can_test_trigger,
        "can_test_procedure": can_test_procedure,
        "current_role": get_current_role(),
        "current_user_name": get_current_user(),
        "current_club_id": session.get("club_id"),
        "current_club_name": session.get("club_name")
    }

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
        "club_name": session.get("club_name"),
        "club_role": session.get("club_role"),
        "role_title": session.get("role_title"),
        "available_roles": session.get("available_roles", []),
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
    
    # Check if student holds multiple memberships and needs to select active persona
    if err == "SELECT_ROLE":
        user_info = user["user"]
        personas = user["personas"]
        if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({
                "status": "select_role",
                "user_name": user_info["name"],
                "student_id": user_info.get("student_id"),
                "email": user_info["email"],
                "message": f"Welcome back, {user_info['name']}! Please choose your active operating persona:",
                "roles": personas
            }), 200
        return render_template(
            "auth/login.html",
            mode="select_role",
            roles=personas,
            user_name=user_info["name"],
            student_id=user_info.get("student_id"),
            email=user_info["email"],
            total_users=get_all_users_count()
        )

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
    session["club_name"] = user.get("club_name")
    session["club_role"] = user.get("club_role")
    session["role_title"] = user.get("role_title")
    session["available_roles"] = user.get("personas", [])
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

@auth_bp.route("/api/auth/select-role", methods=["POST"])
def select_role():
    """
    Selects or switches student persona.
    Sets active authorization tier strictly based on selected club role:
      - President: 'president' tier
      - Secretary / Coordinator / Treasurer: 'coordinator' tier
      - Core Member / Member: 'member' tier
    """
    data = request.get_json() or {}
    club_id = data.get("club_id")
    club_name = data.get("club_name", club_id)
    club_role = data.get("club_role", "Member")
    role_tier = data.get("role_tier") or classify_role_tier(club_role)
    student_id = data.get("student_id") or session.get("student_id")
    email = data.get("email") or session.get("user_email")
    user_name = data.get("user_name") or session.get("user_name")

    if not user_name and email:
        for u in SEED_USERS:
            if u["email"].lower() == email.lower() or email.lower() in [a.lower() for a in u.get("aliases", [])]:
                user_name = u["name"]
                student_id = u.get("student_id")
                break

    personas = get_student_personas(student_id=student_id, email=email)

    session["role"] = role_tier
    session["club_id"] = club_id
    session["club_name"] = club_name
    session["club_role"] = club_role
    session["role_title"] = f"{club_role} — {club_name}"
    if user_name:
        session["user_name"] = user_name
    if email:
        session["user_email"] = email
    if student_id:
        session["student_id"] = student_id
    session["available_roles"] = personas
    session.modified = True

    return jsonify({
        "status": "ok",
        "success": True,
        "role": role_tier,
        "club_id": club_id,
        "role_label": session["role_title"],
        "user_name": session.get("user_name"),
        "student_id": session.get("student_id"),
        "message": f"Operating persona activated: {club_role} ({club_name})",
        "redirect_url": url_for("main.dashboard")
    }), 200

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
