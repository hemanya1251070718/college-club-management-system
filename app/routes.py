import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.db import get_db_connection, check_db_health

main_bp = Blueprint("main", __name__)

# -------------------------------------------------------------
# HEALTH CHECK ROUTE (Required for Cloud Run & Monitoring)
# -------------------------------------------------------------
@main_bp.route("/health")
def health():
    healthy, msg, details = check_db_health()
    status_code = 200 if healthy else 503
    if request.headers.get("Accept") == "application/json" or request.args.get("format") == "json":
        return jsonify({
            "status": "UP" if healthy else "DOWN",
            "database": msg,
            "details": details
        }), status_code
    return render_template("health.html", healthy=healthy, msg=msg, details=details), status_code


@main_bp.route("/init-db")
def init_db_endpoint():
    """
    Self-healing database initialization endpoint.
    Executes base schema, 8 triggers, views, and 8 cursor procedures directly inside Cloud Run.
    """
    import load_schema
    try:
        load_schema.initialize_database()
        return jsonify({
            "status": "success",
            "message": "Cloud SQL database successfully initialized with 8 tables, 8 triggers, and 8 cursor procedures."
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Initialization failed: {str(e)}"
        }), 500


# -------------------------------------------------------------
# DASHBOARD (Overview with ClubSummary View & Statistics)
# -------------------------------------------------------------
@main_bp.route("/")
def dashboard():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 1. Fetch club summaries using the database VIEW 'ClubSummary'
            cursor.execute("""
                SELECT club_id, club_name, category, member_count, faculty_coordinator
                FROM ClubSummary
                ORDER BY member_count DESC;
            """)
            club_summaries = cursor.fetchall()

            # 2. Key statistics
            cursor.execute("SELECT COUNT(*) AS total_students FROM Students;")
            total_students = cursor.fetchone()["total_students"]

            cursor.execute("SELECT COUNT(*) AS total_clubs FROM Clubs;")
            total_clubs = cursor.fetchone()["total_clubs"]

            cursor.execute("SELECT COUNT(*) AS total_memberships FROM Memberships WHERE status = 'Active';")
            total_memberships = cursor.fetchone()["total_memberships"]

            cursor.execute("SELECT COUNT(*) AS total_events FROM Events;")
            total_events = cursor.fetchone()["total_events"]

            # 3. Upcoming / Recent Events
            cursor.execute("""
                SELECT e.event_id, e.event_name, e.event_date, e.venue, e.status, c.club_name
                FROM Events e
                JOIN Clubs c ON e.club_id = c.club_id
                ORDER BY e.event_date DESC
                LIMIT 5;
            """)
            recent_events = cursor.fetchall()

        conn.close()
        return render_template(
            "dashboard.html",
            club_summaries=club_summaries,
            total_students=total_students,
            total_clubs=total_clubs,
            total_memberships=total_memberships,
            total_events=total_events,
            recent_events=recent_events
        )
    except Exception as e:
        flash(f"Database error loading dashboard: {str(e)}", "danger")
        return render_template("dashboard.html", club_summaries=[], total_students=0, total_clubs=0, total_memberships=0, total_events=0, recent_events=[])


# -------------------------------------------------------------
# CLUBS CRUD
# -------------------------------------------------------------
@main_bp.route("/clubs")
def list_clubs():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT c.club_id, c.club_name, c.category, c.faculty_id, c.description, c.member_count,
                       f.name AS faculty_name, f.email AS faculty_email,
                       cp.official_email, cp.instagram_handle
                FROM Clubs c
                LEFT JOIN FacultyCoordinators f ON c.faculty_id = f.faculty_id
                LEFT JOIN ClubProfile cp ON c.club_id = cp.club_id
                ORDER BY c.club_name;
            """)
            clubs = cursor.fetchall()
        conn.close()
        return render_template("clubs/list.html", clubs=clubs)
    except Exception as e:
        flash(f"Error fetching clubs: {str(e)}", "danger")
        return render_template("clubs/list.html", clubs=[])


@main_bp.route("/clubs/new", methods=["GET", "POST"])
def create_club():
    conn = get_db_connection()
    if request.method == "POST":
        club_id = request.form.get("club_id", "").strip().upper()
        club_name = request.form.get("club_name", "").strip()
        category = request.form.get("category", "").strip()
        faculty_id = request.form.get("faculty_id", "").strip()
        description = request.form.get("description", "").strip()
        official_email = request.form.get("official_email", "").strip()
        instagram_handle = request.form.get("instagram_handle", "").strip()

        # Validation
        if not club_id or not club_name or not category or not faculty_id:
            flash("Club ID, Name, Category, and Faculty Coordinator are required.", "warning")
            return redirect(url_for("main.create_club"))

        try:
            with conn.cursor() as cursor:
                # INSERT club (Trigger 8: trg_auto_create_club_profile auto-provisions profile row)
                cursor.execute("""
                    INSERT INTO Clubs (club_id, club_name, category, faculty_id, description, member_count)
                    VALUES (%s, %s, %s, %s, %s, 0);
                """, (club_id, club_name, category, faculty_id, description))

                if official_email or instagram_handle:
                    cursor.execute("""
                        INSERT INTO ClubProfile (club_id, official_email, instagram_handle)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            official_email = VALUES(official_email),
                            instagram_handle = VALUES(instagram_handle);
                    """, (club_id, official_email or None, instagram_handle or None))

            conn.close()
            flash(f"Club '{club_name}' created successfully! Database Trigger 8 (trg_auto_create_club_profile) auto-provisioned club profile.", "success")
            return redirect(url_for("main.list_clubs"))
        except Exception as e:
            flash(f"Error creating club: {str(e)}", "danger")

    # GET: fetch faculty coordinators for the dropdown
    with conn.cursor() as cursor:
        cursor.execute("SELECT faculty_id, name, dept_name FROM FacultyCoordinators ORDER BY name;")
        coordinators = cursor.fetchall()
    conn.close()
    return render_template("clubs/form.html", club=None, coordinators=coordinators, title="Add New Club")


@main_bp.route("/clubs/<club_id>/edit", methods=["GET", "POST"])
def edit_club(club_id):
    conn = get_db_connection()
    if request.method == "POST":
        club_name = request.form.get("club_name", "").strip()
        category = request.form.get("category", "").strip()
        faculty_id = request.form.get("faculty_id", "").strip()
        description = request.form.get("description", "").strip()
        official_email = request.form.get("official_email", "").strip()
        instagram_handle = request.form.get("instagram_handle", "").strip()

        if not club_name or not category or not faculty_id:
            flash("Club Name, Category, and Faculty Coordinator are required.", "warning")
            return redirect(url_for("main.edit_club", club_id=club_id))

        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE Clubs
                    SET club_name = %s, category = %s, faculty_id = %s, description = %s
                    WHERE club_id = %s;
                """, (club_name, category, faculty_id, description, club_id))

                # Upsert profile
                cursor.execute("""
                    INSERT INTO ClubProfile (club_id, official_email, instagram_handle)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE official_email = VALUES(official_email), instagram_handle = VALUES(instagram_handle);
                """, (club_id, official_email or None, instagram_handle or None))

            conn.close()
            flash(f"Club '{club_name}' updated successfully!", "success")
            return redirect(url_for("main.list_clubs"))
        except Exception as e:
            flash(f"Error updating club: {str(e)}", "danger")

    # GET: Fetch existing club data
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT c.*, cp.official_email, cp.instagram_handle
            FROM Clubs c
            LEFT JOIN ClubProfile cp ON c.club_id = cp.club_id
            WHERE c.club_id = %s;
        """, (club_id,))
        club = cursor.fetchone()

        cursor.execute("SELECT faculty_id, name, dept_name FROM FacultyCoordinators ORDER BY name;")
        coordinators = cursor.fetchall()
    conn.close()

    if not club:
        flash("Club not found.", "warning")
        return redirect(url_for("main.list_clubs"))

    return render_template("clubs/form.html", club=club, coordinators=coordinators, title=f"Edit Club: {club['club_name']}")


@main_bp.route("/clubs/<club_id>/delete", methods=["POST"])
def delete_club(club_id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Check for existing memberships or events first
            cursor.execute("SELECT COUNT(*) AS count FROM Memberships WHERE club_id = %s;", (club_id,))
            if cursor.fetchone()["count"] > 0:
                flash(f"Cannot delete club '{club_id}': active student memberships exist. Remove memberships first.", "warning")
                conn.close()
                return redirect(url_for("main.list_clubs"))

            # Delete profile then club
            cursor.execute("DELETE FROM ClubProfile WHERE club_id = %s;", (club_id,))
            cursor.execute("DELETE FROM Clubs WHERE club_id = %s;", (club_id,))
        conn.close()
        flash(f"Club '{club_id}' deleted successfully.", "info")
    except Exception as e:
        flash(f"Error deleting club: {str(e)}", "danger")
    return redirect(url_for("main.list_clubs"))


# -------------------------------------------------------------
# STUDENTS CRUD
# -------------------------------------------------------------
@main_bp.route("/students")
def list_students():
    search = request.args.get("q", "").strip()
    dept = request.args.get("dept", "").strip()
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            query = "SELECT * FROM Students WHERE 1=1"
            params = []
            if search:
                query += " AND (name LIKE %s OR prn_number LIKE %s OR student_id LIKE %s)"
                params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
            if dept:
                query += " AND dept_id = %s"
                params.append(dept)
            query += " ORDER BY student_id LIMIT 100;"

            cursor.execute(query, tuple(params))
            students = cursor.fetchall()

            cursor.execute("SELECT DISTINCT dept_id, dept_name FROM Students ORDER BY dept_id;")
            departments = cursor.fetchall()
        conn.close()
        return render_template("students/list.html", students=students, departments=departments, search=search, selected_dept=dept)
    except Exception as e:
        flash(f"Error fetching students: {str(e)}", "danger")
        return render_template("students/list.html", students=[], departments=[], search="", selected_dept="")


@main_bp.route("/students/new", methods=["GET", "POST"])
def create_student():
    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip().upper()
        prn_number = request.form.get("prn_number", "").strip()
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip() or None
        dept_id = request.form.get("dept_id", "").strip().upper()
        dept_name = request.form.get("dept_name", "").strip()
        year_of_study = request.form.get("year_of_study", "").strip()

        if not student_id or not prn_number or not name or not email or not dept_id or not year_of_study:
            flash("All fields except phone are required.", "warning")
            return redirect(url_for("main.create_student"))

        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Students (student_id, prn_number, name, email, phone, dept_id, dept_name, year_of_study)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """, (student_id, prn_number, name, email, phone, dept_id, dept_name, int(year_of_study)))
            conn.close()
            flash(f"Student '{name}' added successfully!", "success")
            return redirect(url_for("main.list_students"))
        except Exception as e:
            flash(f"Error adding student: {str(e)}", "danger")

    return render_template("students/form.html", student=None, title="Add Student")


@main_bp.route("/students/<student_id>/edit", methods=["GET", "POST"])
def edit_student(student_id):
    conn = get_db_connection()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip() or None
        dept_id = request.form.get("dept_id", "").strip().upper()
        dept_name = request.form.get("dept_name", "").strip()
        year_of_study = request.form.get("year_of_study", "").strip()

        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE Students
                    SET name = %s, email = %s, phone = %s, dept_id = %s, dept_name = %s, year_of_study = %s
                    WHERE student_id = %s;
                """, (name, email, phone, dept_id, dept_name, int(year_of_study), student_id))
            conn.close()
            flash(f"Student '{name}' updated successfully!", "success")
            return redirect(url_for("main.list_students"))
        except Exception as e:
            flash(f"Error updating student: {str(e)}", "danger")

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM Students WHERE student_id = %s;", (student_id,))
        student = cursor.fetchone()
    conn.close()

    if not student:
        flash("Student not found.", "warning")
        return redirect(url_for("main.list_students"))

    return render_template("students/form.html", student=student, title=f"Edit Student: {student['name']}")


@main_bp.route("/students/<student_id>/delete", methods=["POST"])
def delete_student(student_id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Check for memberships or registrations
            cursor.execute("SELECT COUNT(*) AS count FROM Memberships WHERE student_id = %s;", (student_id,))
            if cursor.fetchone()["count"] > 0:
                flash(f"Cannot delete student '{student_id}': active club memberships exist.", "warning")
                conn.close()
                return redirect(url_for("main.list_students"))

            cursor.execute("DELETE FROM Students WHERE student_id = %s;", (student_id,))
        conn.close()
        flash(f"Student '{student_id}' deleted successfully.", "info")
    except Exception as e:
        flash(f"Error deleting student: {str(e)}", "danger")
    return redirect(url_for("main.list_students"))


# -------------------------------------------------------------
# MEMBERSHIPS CRUD (SHOWCASES LIVE AUTOMATIC DATABASE TRIGGERS)
# -------------------------------------------------------------
@main_bp.route("/memberships")
def list_memberships():
    club_filter = request.args.get("club", "").strip()
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            query = """
                SELECT m.membership_id, m.student_id, m.club_id, m.role, m.join_date, m.status,
                       s.name AS student_name, s.prn_number, s.dept_name,
                       c.club_name, c.member_count
                FROM Memberships m
                JOIN Students s ON m.student_id = s.student_id
                JOIN Clubs c ON m.club_id = c.club_id
            """
            params = []
            if club_filter:
                query += " WHERE m.club_id = %s"
                params.append(club_filter)
            query += " ORDER BY m.join_date DESC LIMIT 100;"

            cursor.execute(query, tuple(params))
            memberships = cursor.fetchall()

            cursor.execute("SELECT club_id, club_name, member_count FROM Clubs ORDER BY club_name;")
            clubs = cursor.fetchall()
        conn.close()
        return render_template("memberships/list.html", memberships=memberships, clubs=clubs, selected_club=club_filter)
    except Exception as e:
        flash(f"Error loading memberships: {str(e)}", "danger")
        return render_template("memberships/list.html", memberships=[], clubs=[], selected_club="")


@main_bp.route("/memberships/new", methods=["GET", "POST"])
def create_membership():
    conn = get_db_connection()
    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip()
        club_id = request.form.get("club_id", "").strip()
        role = request.form.get("role", "Member").strip()
        join_date = request.form.get("join_date", "").strip()
        status = request.form.get("status", "Active").strip()

        if not student_id or not club_id or not join_date:
            flash("Student, Club, and Join Date are required.", "warning")
            return redirect(url_for("main.create_membership"))

        # Generate readable membership ID, e.g. MEM-CSI-CE250112
        clean_sid = re.sub(r'[^A-Z0-9]', '', student_id)
        membership_id = f"MEM-{club_id}-{clean_sid}"

        try:
            with conn.cursor() as cursor:
                # Check initial club member_count before insert
                cursor.execute("SELECT member_count FROM Clubs WHERE club_id = %s;", (club_id,))
                count_before = cursor.fetchone()["member_count"]

                # INSERT - TRIGGER 'trg_after_membership_insert_sync_count' and 'trg_prevent_multiple_presidents' FIRE!
                cursor.execute("""
                    INSERT INTO Memberships (membership_id, student_id, club_id, role, join_date, status)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """, (membership_id, student_id, club_id, role, join_date, status))

                # Check club member_count after insert to verify trigger execution
                cursor.execute("SELECT member_count FROM Clubs WHERE club_id = %s;", (club_id,))
                count_after = cursor.fetchone()["member_count"]

            conn.close()
            flash(
                f"Membership created! Database Trigger 'trg_after_membership_insert_sync_count' fired: "
                f"Club '{club_id}' member_count automatically increased from {count_before} to {count_after}.",
                "success"
            )
            return redirect(url_for("main.list_memberships"))
        except Exception as e:
            err_msg = str(e)
            if "Integrity Violation: A club cannot have more than ONE active President" in err_msg:
                flash("Trigger 3 Rejection (trg_prevent_multiple_presidents): A club cannot have more than ONE active President simultaneously.", "danger")
            else:
                flash(f"Error creating membership (Trigger halted or duplicate entry): {err_msg}", "danger")

    with conn.cursor() as cursor:
        cursor.execute("SELECT student_id, name, prn_number FROM Students ORDER BY name;")
        students = cursor.fetchall()
        cursor.execute("SELECT club_id, club_name FROM Clubs ORDER BY club_name;")
        clubs = cursor.fetchall()
    conn.close()
    return render_template("memberships/form.html", membership=None, students=students, clubs=clubs, title="Add Member")


@main_bp.route("/memberships/<membership_id>/edit", methods=["GET", "POST"])
def edit_membership(membership_id):
    conn = get_db_connection()
    if request.method == "POST":
        role = request.form.get("role", "Member").strip()
        status = request.form.get("status", "Active").strip()
        join_date = request.form.get("join_date", "").strip()

        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT club_id, status FROM Memberships WHERE membership_id = %s;", (membership_id,))
                old_row = cursor.fetchone()
                club_id = old_row["club_id"]
                old_status = old_row["status"]

                # UPDATE - TRIGGER 'trg_adjust_member_count_on_status_change' fires on status change!
                cursor.execute("""
                    UPDATE Memberships
                    SET role = %s, status = %s, join_date = %s
                    WHERE membership_id = %s;
                """, (role, status, join_date, membership_id))

                cursor.execute("SELECT member_count FROM Clubs WHERE club_id = %s;", (club_id,))
                new_count = cursor.fetchone()["member_count"]

            conn.close()
            if old_status != status:
                flash(f"Membership updated! Trigger 4 (trg_adjust_member_count_on_status_change) dynamically adjusted '{club_id}' count to {new_count}.", "success")
            else:
                flash("Membership updated successfully.", "success")
            return redirect(url_for("main.list_memberships"))
        except Exception as e:
            flash(f"Error updating membership: {str(e)}", "danger")

    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT m.*, s.name AS student_name, c.club_name
            FROM Memberships m
            JOIN Students s ON m.student_id = s.student_id
            JOIN Clubs c ON m.club_id = c.club_id
            WHERE m.membership_id = %s;
        """, (membership_id,))
        membership = cursor.fetchone()
    conn.close()

    if not membership:
        flash("Membership record not found.", "warning")
        return redirect(url_for("main.list_memberships"))

    return render_template("memberships/form.html", membership=membership, students=[], clubs=[], title="Edit Membership")


@main_bp.route("/memberships/<membership_id>/delete", methods=["POST"])
def delete_membership(membership_id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT club_id, status FROM Memberships WHERE membership_id = %s;", (membership_id,))
            row = cursor.fetchone()
            if not row:
                flash("Membership record not found.", "warning")
                conn.close()
                return redirect(url_for("main.list_memberships"))

            club_id = row["club_id"]
            cursor.execute("SELECT member_count FROM Clubs WHERE club_id = %s;", (club_id,))
            count_before = cursor.fetchone()["member_count"]

            # DELETE - TRIGGER 'trg_after_membership_delete_sync_count' WILL FIRE AUTOMATICALLY!
            cursor.execute("DELETE FROM Memberships WHERE membership_id = %s;", (membership_id,))

            cursor.execute("SELECT member_count FROM Clubs WHERE club_id = %s;", (club_id,))
            count_after = cursor.fetchone()["member_count"]

        conn.close()
        flash(
            f"Membership removed! Database Trigger 'trg_after_membership_delete_sync_count' fired: "
            f"Club '{club_id}' member_count automatically decremented from {count_before} to {count_after}.",
            "info"
        )
    except Exception as e:
        flash(f"Error deleting membership: {str(e)}", "danger")
    return redirect(url_for("main.list_memberships"))


# -------------------------------------------------------------
# EVENTS CRUD
# -------------------------------------------------------------
@main_bp.route("/events")
def list_events():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT e.*, c.club_name,
                       (SELECT COUNT(*) FROM EventRegistrations er WHERE er.event_id = e.event_id) AS attendee_count
                FROM Events e
                JOIN Clubs c ON e.club_id = c.club_id
                ORDER BY e.event_date DESC;
            """)
            events = cursor.fetchall()
        conn.close()
        return render_template("events/list.html", events=events)
    except Exception as e:
        flash(f"Error fetching events: {str(e)}", "danger")
        return render_template("events/list.html", events=[])


@main_bp.route("/events/new", methods=["GET", "POST"])
def create_event():
    conn = get_db_connection()
    if request.method == "POST":
        event_id = request.form.get("event_id", "").strip().upper()
        club_id = request.form.get("club_id", "").strip()
        event_name = request.form.get("event_name", "").strip()
        event_date = request.form.get("event_date", "").strip() or None
        venue = request.form.get("venue", "").strip() or None
        budget = request.form.get("budget_allocated", "0").strip()
        event_type = request.form.get("event_type", "").strip() or None
        status = request.form.get("status", "Planned").strip()

        if not event_id or not club_id or not event_name:
            flash("Event ID, Club, and Event Name are required.", "warning")
            return redirect(url_for("main.create_event"))

        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Events (event_id, club_id, event_name, event_date, venue, budget_allocated, event_type, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """, (event_id, club_id, event_name, event_date, venue, float(budget), event_type, status))
            conn.close()
            flash(f"Event '{event_name}' created successfully!", "success")
            return redirect(url_for("main.list_events"))
        except Exception as e:
            flash(f"Error creating event: {str(e)}", "danger")

    with conn.cursor() as cursor:
        cursor.execute("SELECT club_id, club_name FROM Clubs ORDER BY club_name;")
        clubs = cursor.fetchall()
    conn.close()
    return render_template("events/form.html", event=None, clubs=clubs, title="Create Event")


@main_bp.route("/events/<event_id>/edit", methods=["GET", "POST"])
def edit_event(event_id):
    conn = get_db_connection()
    if request.method == "POST":
        club_id = request.form.get("club_id", "").strip()
        event_name = request.form.get("event_name", "").strip()
        event_date = request.form.get("event_date", "").strip() or None
        venue = request.form.get("venue", "").strip() or None
        budget = request.form.get("budget_allocated", "0").strip()
        event_type = request.form.get("event_type", "").strip() or None
        status = request.form.get("status", "Planned").strip()

        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE Events
                    SET club_id = %s, event_name = %s, event_date = %s, venue = %s, budget_allocated = %s, event_type = %s, status = %s
                    WHERE event_id = %s;
                """, (club_id, event_name, event_date, venue, float(budget), event_type, status, event_id))
            conn.close()
            flash(f"Event '{event_name}' updated successfully!", "success")
            return redirect(url_for("main.list_events"))
        except Exception as e:
            flash(f"Error updating event: {str(e)}", "danger")

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM Events WHERE event_id = %s;", (event_id,))
        event = cursor.fetchone()
        cursor.execute("SELECT club_id, club_name FROM Clubs ORDER BY club_name;")
        clubs = cursor.fetchall()
    conn.close()

    if not event:
        flash("Event not found.", "warning")
        return redirect(url_for("main.list_events"))

    return render_template("events/form.html", event=event, clubs=clubs, title=f"Edit Event: {event['event_name']}")


@main_bp.route("/events/<event_id>/delete", methods=["POST"])
def delete_event(event_id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Delete registrations first to respect foreign key
            cursor.execute("DELETE FROM EventRegistrations WHERE event_id = %s;", (event_id,))
            cursor.execute("DELETE FROM Feedback WHERE event_id = %s;", (event_id,))
            cursor.execute("DELETE FROM Events WHERE event_id = %s;", (event_id,))
        conn.close()
        flash(f"Event '{event_id}' deleted successfully.", "info")
    except Exception as e:
        flash(f"Error deleting event: {str(e)}", "danger")
    return redirect(url_for("main.list_events"))


# -------------------------------------------------------------
# EVENT REGISTRATIONS & ATTENDANCE (SHOWCASES TRIGGERS 5 & 7)
# -------------------------------------------------------------
@main_bp.route("/events/<event_id>/registrations")
def event_registrations(event_id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT e.*, c.club_name
                FROM Events e
                JOIN Clubs c ON e.club_id = c.club_id
                WHERE e.event_id = %s;
            """, (event_id,))
            event = cursor.fetchone()

            cursor.execute("""
                SELECT er.registration_id, er.event_id, er.student_id, er.registration_date, er.attendance_status,
                       s.name AS student_name, s.dept_name
                FROM EventRegistrations er
                JOIN Students s ON er.student_id = s.student_id
                WHERE er.event_id = %s
                ORDER BY er.registration_date DESC;
            """, (event_id,))
            registrations = cursor.fetchall()

            cursor.execute("SELECT student_id, name FROM Students ORDER BY name;")
            all_students = cursor.fetchall()
        conn.close()

        if not event:
            flash("Event not found.", "warning")
            return redirect(url_for("main.list_events"))

        return render_template("events/registrations.html", event=event, registrations=registrations, all_students=all_students)
    except Exception as e:
        flash(f"Error loading registrations: {str(e)}", "danger")
        return redirect(url_for("main.list_events"))


@main_bp.route("/events/<event_id>/register", methods=["POST"])
def register_for_event(event_id):
    student_id = request.form.get("student_id", "").strip()
    if not student_id:
        flash("Please select a student to register.", "warning")
        return redirect(url_for("main.event_registrations", event_id=event_id))

    clean_sid = re.sub(r'[^A-Z0-9]', '', student_id)
    clean_eid = re.sub(r'[^A-Z0-9]', '', event_id)
    reg_id = f"REG-{clean_eid[:6]}-{clean_sid[:8]}"

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # TRIGGER 5 (trg_prevent_registration_for_completed_event) WILL INTERCEPT!
            cursor.execute("""
                INSERT INTO EventRegistrations (registration_id, event_id, student_id, registration_date, attendance_status)
                VALUES (%s, %s, %s, CURRENT_DATE, 'Registered');
            """, (reg_id, event_id, student_id))
        conn.close()
        flash(f"Student '{student_id}' registered successfully for event '{event_id}'!", "success")
    except Exception as e:
        err_msg = str(e)
        if "Cannot register for an event that is already Completed or Cancelled" in err_msg:
            flash("Trigger 5 Rejection (trg_prevent_registration_for_completed_event): Cannot register for an event that is already Completed or Cancelled.", "danger")
        else:
            flash(f"Registration error: {err_msg}", "danger")

    return redirect(url_for("main.event_registrations", event_id=event_id))


@main_bp.route("/events/<event_id>/attendance/<reg_id>", methods=["POST"])
def mark_attendance(event_id, reg_id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT status FROM Events WHERE event_id = %s;", (event_id,))
            status_before = cursor.fetchone()["status"]

            # TRIGGER 7 (trg_auto_progress_event_on_attendance) FIRES on attendance update!
            cursor.execute("""
                UPDATE EventRegistrations
                SET attendance_status = 'Attended'
                WHERE registration_id = %s;
            """, (reg_id,))

            cursor.execute("SELECT status FROM Events WHERE event_id = %s;", (event_id,))
            status_after = cursor.fetchone()["status"]
        conn.close()

        if status_before == 'Planned' and status_after == 'Ongoing':
            flash(f"Attendance marked! Trigger 7 (trg_auto_progress_event_on_attendance) automatically progressed event status from 'Planned' to 'Ongoing'!", "success")
        else:
            flash("Attendance marked as Attended.", "success")
    except Exception as e:
        flash(f"Error marking attendance: {str(e)}", "danger")

    return redirect(url_for("main.event_registrations", event_id=event_id))


# -------------------------------------------------------------
# EVENT FEEDBACK & REVIEWS (SHOWCASES TRIGGER 6 & CURSOR 8)
# -------------------------------------------------------------
@main_bp.route("/events/<event_id>/feedback")
def event_feedback(event_id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT e.*, c.club_name
                FROM Events e
                JOIN Clubs c ON e.club_id = c.club_id
                WHERE e.event_id = %s;
            """, (event_id,))
            event = cursor.fetchone()

            cursor.execute("""
                SELECT f.*, s.name AS student_name
                FROM Feedback f
                JOIN Students s ON f.student_id = s.student_id
                WHERE f.event_id = %s
                ORDER BY f.feedback_date DESC;
            """, (event_id,))
            feedbacks = cursor.fetchall()

            cursor.execute("SELECT student_id, name FROM Students ORDER BY name;")
            all_students = cursor.fetchall()
        conn.close()

        if not event:
            flash("Event not found.", "warning")
            return redirect(url_for("main.list_events"))

        return render_template("events/feedback.html", event=event, feedbacks=feedbacks, all_students=all_students)
    except Exception as e:
        flash(f"Error loading event feedback: {str(e)}", "danger")
        return redirect(url_for("main.list_events"))


@main_bp.route("/events/<event_id>/feedback/submit", methods=["POST"])
def submit_event_feedback(event_id):
    student_id = request.form.get("student_id", "").strip()
    rating = request.form.get("rating", "5").strip()
    comments = request.form.get("comments", "").strip()

    if not student_id:
        flash("Student selection is required for feedback.", "warning")
        return redirect(url_for("main.event_feedback", event_id=event_id))

    clean_sid = re.sub(r'[^A-Z0-9]', '', student_id)
    clean_eid = re.sub(r'[^A-Z0-9]', '', event_id)
    feedback_id = f"FB-{clean_eid[:6]}-{clean_sid[:8]}"

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT club_id FROM Events WHERE event_id = %s;", (event_id,))
            club_id = cursor.fetchone()["club_id"]

            # TRIGGER 6 (trg_verify_feedback_registration) INTERCEPTS HERE!
            cursor.execute("""
                INSERT INTO Feedback (feedback_id, student_id, club_id, event_id, feedback_type, rating, comments, feedback_date)
                VALUES (%s, %s, %s, %s, 'Event', %s, %s, CURRENT_DATE);
            """, (feedback_id, student_id, club_id, event_id, int(rating), comments or None))
        conn.close()
        flash("Feedback review accepted and verified by Trigger 6!", "success")
    except Exception as e:
        err_msg = str(e)
        if "Student must be registered for the event before submitting event feedback" in err_msg:
            flash("Trigger 6 Rejection (trg_verify_feedback_registration): Student must be registered for the event before submitting event feedback.", "danger")
        else:
            flash(f"Feedback error: {err_msg}", "danger")

    return redirect(url_for("main.event_feedback", event_id=event_id))


# -------------------------------------------------------------
# DATABASE TRIGGERS SHOWCASE
# -------------------------------------------------------------
@main_bp.route("/triggers")
def list_triggers():
    return render_template("triggers/list.html")


# -------------------------------------------------------------
# STORED PROCEDURES & CURSORS SUITE (8 CURSOR PROCEDURES)
# -------------------------------------------------------------
@main_bp.route("/procedures")
def procedures_hub():
    return render_template("procedures/index.html", results=None, proc_name=None)


@main_bp.route("/procedures/execute/<proc_id>", methods=["POST"])
def execute_proc(proc_id):
    results = []
    proc_name = ""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            if proc_id == "audit":
                p_fix = int(request.form.get("p_fix", 0))
                cursor.callproc("sp_audit_club_counts", (p_fix,))
                results = cursor.fetchall()
                proc_name = f"sp_audit_club_counts(p_fix={p_fix})"
                flash(f"Executed {proc_name}: {'Database repaired!' if p_fix == 1 else 'Preview audit complete.'}", "success")

            elif proc_id == "recruitment":
                p_min_events = int(request.form.get("p_min_events", 2))
                p_auto_invite = int(request.form.get("p_auto_invite", 0))
                cursor.callproc("sp_recruitment_leads_and_auto_invite", (p_min_events, p_auto_invite))
                results = cursor.fetchall()
                proc_name = f"sp_recruitment_leads_and_auto_invite(min_events={p_min_events}, auto_invite={p_auto_invite})"
                flash(f"Executed {proc_name}: {'Leads auto-enrolled as Volunteers!' if p_auto_invite == 1 else 'Candidate leads identified.'}", "success")

            elif proc_id == "budget":
                p_min_rating = float(request.form.get("p_min_rating", 4.50))
                p_bonus_pct = float(request.form.get("p_bonus_pct", 10.0))
                p_apply = int(request.form.get("p_apply", 0))
                cursor.callproc("sp_reconcile_event_budgets", (p_min_rating, p_bonus_pct, p_apply))
                results = cursor.fetchall()
                proc_name = f"sp_reconcile_event_budgets(min_rating={p_min_rating}, bonus={p_bonus_pct}%, apply={p_apply})"
                flash(f"Executed {proc_name}: {'Performance budget bonuses committed!' if p_apply == 1 else 'Bonus preview calculated.'}", "success")

            elif proc_id == "close_events":
                p_cutoff_date = request.form.get("p_cutoff_date", "2026-10-31").strip()
                p_apply = int(request.form.get("p_apply", 0))
                cursor.callproc("sp_close_past_events", (p_cutoff_date, p_apply))
                results = cursor.fetchall()
                proc_name = f"sp_close_past_events(cutoff='{p_cutoff_date}', apply={p_apply})"
                flash(f"Executed {proc_name}: {'Past events reconciled in Events table!' if p_apply == 1 else 'Closure preview ready.'}", "success")

            elif proc_id == "deactivate":
                p_max_missed_events = int(request.form.get("p_max_missed_events", 2))
                p_apply = int(request.form.get("p_apply", 0))
                cursor.callproc("sp_deactivate_inactive_members", (p_max_missed_events, p_apply))
                results = cursor.fetchall()
                proc_name = f"sp_deactivate_inactive_members(max_missed={p_max_missed_events}, apply={p_apply})"
                flash(f"Executed {proc_name}: {'Chronic absentees deactivated in Memberships!' if p_apply == 1 else 'Absentee audit complete.'}", "success")

            elif proc_id == "promote":
                p_student_id = request.form.get("p_student_id", "ALL").strip() or "ALL"
                p_min_attended = int(request.form.get("p_min_attended", 3))
                p_apply = int(request.form.get("p_apply", 0))
                cursor.callproc("sp_award_active_contributors", (p_student_id, p_min_attended, p_apply))
                results = cursor.fetchall()
                proc_name = f"sp_award_active_contributors(student='{p_student_id}', min_attended={p_min_attended}, apply={p_apply})"
                flash(f"Executed {proc_name}: {'Active contributors promoted to Core Members!' if p_apply == 1 else 'Merit evaluation complete.'}", "success")

            elif proc_id == "grad":
                p_grad_year = int(request.form.get("p_grad_year", 4))
                p_apply = int(request.form.get("p_apply", 0))
                cursor.callproc("sp_senior_graduation_rollout", (p_grad_year, p_apply))
                results = cursor.fetchall()
                proc_name = f"sp_senior_graduation_rollout(grad_year={p_grad_year}, apply={p_apply})"
                flash(f"Executed {proc_name}: {'Year 4 seniors transitioned to Alumni status!' if p_apply == 1 else 'Graduation preview ready.'}", "success")

            elif proc_id == "privacy":
                p_low_rating_threshold = int(request.form.get("p_low_rating_threshold", 2))
                p_apply = int(request.form.get("p_apply", 0))
                cursor.callproc("sp_anonymize_sensitive_feedback", (p_low_rating_threshold, p_apply))
                results = cursor.fetchall()
                proc_name = f"sp_anonymize_sensitive_feedback(threshold={p_low_rating_threshold}, apply={p_apply})"
                flash(f"Executed {proc_name}: {'Critical reviews protected with anonymous standard tags!' if p_apply == 1 else 'Privacy audit preview complete.'}", "success")

        conn.close()
    except Exception as e:
        flash(f"Error executing procedure: {str(e)}", "danger")

    return render_template("procedures/index.html", results=results, proc_name=proc_name)


@main_bp.route("/procedures/student-clubs")
def proc_student_clubs():
    student_id = request.args.get("student_id", "").strip()
    results = []
    selected_student = None

    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT student_id, name, prn_number FROM Students ORDER BY name;")
        all_students = cursor.fetchall()

        if student_id:
            cursor.execute("SELECT * FROM Students WHERE student_id = %s;", (student_id,))
            selected_student = cursor.fetchone()
            
            # Execute Stored Procedure 'GetStudentClubs'
            cursor.callproc("GetStudentClubs", (student_id,))
            results = cursor.fetchall()

    conn.close()
    return render_template(
        "procedures/student_clubs.html",
        all_students=all_students,
        selected_student=selected_student,
        results=results,
        student_id=student_id
    )


@main_bp.route("/procedures/audit", methods=["GET", "POST"])
def proc_audit():
    action = request.form.get("action", "check") if request.method == "POST" else "check"
    fix_flag = 1 if action == "repair" else 0
    audit_results = []
    error = None

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Execute Stored Procedure 'sp_audit_club_counts' from cursor.sql
            cursor.callproc("sp_audit_club_counts", (fix_flag,))
            audit_results = cursor.fetchall()
        conn.close()
        if fix_flag == 1:
            flash("Audit and repair executed: any mismatches have been corrected to match actual Memberships count.", "success")
    except Exception as e:
        error = str(e)
        flash(f"Stored procedure execution: {str(e)}", "warning")

    return render_template("procedures/audit.html", audit_results=audit_results, fix_flag=fix_flag, error=error)
