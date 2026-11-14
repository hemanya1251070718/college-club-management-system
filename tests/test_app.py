import pytest
from app.config import Config

def test_health_json_endpoint(client):
    """Test the /health endpoint returning JSON metadata."""
    response = client.get("/health?format=json")
    # Health returns 200 if connected or 503 if DB disconnected in test env
    assert response.status_code in [200, 503]
    data = response.get_json()
    assert "status" in data
    assert "database" in data
    assert "details" in data
    assert "mode" in data["details"]

def test_config_connection_modes(monkeypatch):
    """Test dual-mode connection configuration (Local TCP vs Cloud SQL Unix Socket)."""
    # 1. Local TCP Mode
    monkeypatch.delenv("INSTANCE_CONNECTION_NAME", raising=False)
    from app.config import Config as C1
    assert C1.INSTANCE_CONNECTION_NAME is None or C1.INSTANCE_CONNECTION_NAME == ""

    # 2. Cloud SQL Unix Socket Mode
    monkeypatch.setenv("INSTANCE_CONNECTION_NAME", "my-project:asia-south1:my-db")
    import importlib
    import app.config
    importlib.reload(app.config)
    assert app.config.Config.INSTANCE_CONNECTION_NAME == "my-project:asia-south1:my-db"

def test_dashboard_renders(client):
    """Test dashboard route returns successful HTTP status."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Club Management Dashboard" in response.data or b"ClubHub" in response.data

def test_clubs_page_renders(client):
    """Test clubs listing page."""
    response = client.get("/clubs")
    assert response.status_code == 200
    assert b"Clubs Management" in response.data

def test_students_page_renders(client):
    """Test students directory page."""
    response = client.get("/students")
    assert response.status_code == 200
    assert b"Students Directory" in response.data

def test_memberships_page_renders(client):
    """Test memberships directory page."""
    response = client.get("/memberships")
    assert response.status_code == 200
    assert b"Club Memberships Directory" in response.data or b"Memberships" in response.data

def test_events_page_renders(client):
    """Test events listing page."""
    response = client.get("/events")
    assert response.status_code == 200
    assert b"Campus Events Management" in response.data

def test_triggers_page_renders(client):
    """Test triggers architecture and catalog page."""
    response = client.get("/triggers")
    assert response.status_code == 200
    assert b"8 Database Triggers Architecture" in response.data
    assert b"trg_after_membership_insert_sync_count" in response.data
    assert b"trg_prevent_multiple_presidents" in response.data
    assert b"trg_auto_create_club_profile" in response.data

def test_procedures_hub_renders(client):
    """Test stored procedures & cursors hub page."""
    response = client.get("/procedures")
    assert response.status_code == 200
    assert b"Stored Procedures &amp; Database Cursors Hub" in response.data or b"Stored Procedures & Database Cursors Hub" in response.data
    assert b"sp_audit_club_counts" in response.data
    assert b"sp_recruitment_leads_and_auto_invite" in response.data
    assert b"sp_reconcile_event_budgets" in response.data

def test_execute_proc_endpoint(client):
    """Test execution endpoint handles procedures gracefully even with disconnected DB."""
    response = client.post("/procedures/execute/audit", data={"p_fix": "0"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"sp_audit_club_counts" in response.data

def test_custom_404_page(client):
    """Test 404 error handler suppresses server trace and renders custom template."""
    response = client.get("/this-route-does-not-exist")
    assert response.status_code == 404
    assert b"Resource Not Found" in response.data


def test_guest_mode_endpoint(client):
    """Test the one-click /guest endpoint for unrestricted demo access."""
    response = client.get("/guest", follow_redirects=True)
    assert response.status_code == 200
    # JSON access
    res_json = client.get("/api/auth/status")
    assert res_json.status_code == 200
    data = res_json.get_json()
    assert data["role"] == "guest"
    assert data["meta"]["can_execute_procs"] is True

def test_login_demo_persona_switch(client):
    """Test switching demo personas via /login."""
    response = client.post("/login", json={"role": "admin"})
    assert response.status_code == 200
    assert response.get_json()["role"] == "admin"


def test_member_role_restrictions(client):
    """Verify that Student Member role cannot edit, create, or delete clubs."""
    with client.session_transaction() as sess:
        sess["role"] = "member"
        sess["user_name"] = "Aarav Deshmukh (Student Member)"

    # Attempt to open Add Club form
    res_create = client.get("/clubs/new", follow_redirects=False)
    assert res_create.status_code == 302
    assert "/clubs" in res_create.headers["Location"]

    # Attempt to open Edit Club form
    res_edit = client.get("/clubs/CSI/edit", follow_redirects=False)
    assert res_edit.status_code == 302
    assert "/clubs" in res_edit.headers["Location"]

    # Switch back to guest
    with client.session_transaction() as sess:
        sess["role"] = "guest"
    res_guest = client.get("/clubs")
    assert res_guest.status_code == 200


def test_login_page_renders(client):
    """Test gatekeeper login page renders with status 200."""
    response = client.get("/login")
    assert response.status_code == 200
    assert b"ClubHub DBMS" in response.data
    assert b"Welcome Back" in response.data

def test_login_authentication_by_role_emails(client):
    """Test login authentication for Principal, Coordinator, and Student Member."""
    # 1. Principal
    res_prin = client.post("/login", json={"email": "sharma.principal@vit.edu", "password": "password123"})
    assert res_prin.status_code == 200
    assert res_prin.get_json()["role"] == "admin"

    # 2. Coordinator
    res_coord = client.post("/login", json={"email": "patil.121001.cordinator@vit.edu", "password": "password123"})
    assert res_coord.status_code == 200
    assert res_coord.get_json()["role"] == "manager"

    # 3. Student Member
    res_mem = client.post("/login", json={"email": "aarav.123456@vit.edu", "password": "password123"})
    assert res_mem.status_code == 200
    assert res_mem.get_json()["role"] == "member"

def test_signup_validation_and_registration(client):
    """Test signup validation strictly enforces @vit.edu role formats."""
    # Invalid domain
    res_invalid = client.post("/signup", json={"email": "hacker@gmail.com", "password": "password123", "name": "Fake User"})
    assert res_invalid.status_code == 400

    # Valid Student Registration (using unique PRN to remain idempotent across test runs)
    import time
    unique_email = f"sneha.{int(time.time() * 1000)}@vit.edu"
    res_valid = client.post("/signup", json={"email": unique_email, "password": "mypassword123", "name": "Sneha Kulkarni"})
    assert res_valid.status_code == 200
    assert res_valid.get_json()["role"] == "member"

def test_all_75_students_preseeded_and_username_equals_password(client):
    """
    Verifies that all 75 students are pre-seeded in the authentication catalog,
    and can log in directly with username == password (or 'password123').
    """
    from app.user_model import authenticate_user, MEMORY_USERS, get_all_users_count
    
    # Check that at least 76 accounts (75 students + 1 principal) exist in catalog
    assert len(MEMORY_USERS) >= 76
    assert get_all_users_count() >= 76

    # Test multi-role student login returning SELECT_ROLE with all assigned club personas
    err, result = authenticate_user("hemanya.1251070718@vit.edu", "hemanya.1251070718@vit.edu")
    assert err == "SELECT_ROLE"
    assert len(result["personas"]) == 3
    persona_clubs = [p["club_id"] for p in result["personas"]]
    assert "CSI" in persona_clubs
    assert "EDC" in persona_clubs
    assert "ZEPHYR" in persona_clubs

    # Test direct authentication with bypass_role_select=True
    err_direct, user_direct = authenticate_user(
        "hemanya.1251070718@vit.edu", "hemanya.1251070718@vit.edu", bypass_role_select=True
    )
    assert err_direct is None
    assert user_direct["student_id"] == "CE25-0718"

    # Test single-member student login with username == password
    err_mem, user_mem = authenticate_user("ishan.1251070277@vit.edu", "ishan.1251070277@vit.edu")
    assert err_mem is None
    assert user_mem["role"] == "member"

    # Test president login with username == password
    err_pres, user_pres = authenticate_user("aditya.12410214.president@vit.edu", "aditya.12410214.president@vit.edu")
    assert err_pres is None
    assert user_pres["role"] == "president"

    # Test coordinator login with username == password
    err_coord, user_coord = authenticate_user("priya.12410219.secretary@vit.edu", "priya.12410219.secretary@vit.edu")
    assert err_coord is None
    assert user_coord["role"] == "coordinator"

def test_role_based_trigger_and_procedure_permissions(client):
    """
    Verifies granular authorization for Triggers and Procedures:
    - Member: Triggers 1, 5, 6; Procedures 0
    - Coordinator: Triggers 1, 2, 4, 5, 6, 7; Procedures 2, 3, 5, 6
    - President: Triggers 1, 2, 3, 5, 6, 8; Procedures 1, 4, 7, 8
    - Admin/Guest: All 8 Triggers and all 8 Procedures
    """
    from app.auth import can_test_trigger, can_test_procedure
    from flask import session

    with client.application.test_request_context():
        # Member persona
        session["role"] = "member"
        assert can_test_trigger(1) is True
        assert can_test_trigger(5) is True
        assert can_test_trigger(6) is True
        assert can_test_trigger(2) is False
        assert can_test_trigger(3) is False
        assert can_test_procedure(1) is False

        # Coordinator persona
        session["role"] = "coordinator"
        assert can_test_trigger(1) is True
        assert can_test_trigger(2) is True
        assert can_test_trigger(3) is False  # Only President can test multiple presidents
        assert can_test_procedure(2) is True

        # President persona
        session["role"] = "president"
        assert can_test_trigger(3) is True   # President bylaws trigger
        assert can_test_procedure(1) is True # sp_audit_club_counts

        # Guest / Admin persona
        session["role"] = "guest"
        for i in range(1, 9):
            assert can_test_trigger(i) is True
            assert can_test_procedure(i) is True

def test_multi_role_login_and_persona_selection_flow(client):
    """
    Tests that a multi-role student logging in via HTTP gets a 'select_role'
    response with available club personas, and posting to /api/auth/select-role
    sets the chosen persona session and grants appropriate permissions.
    """
    resp = client.post(
        "/login",
        data={"email": "hemanya.1251070718@vit.edu", "password": "hemanya.1251070718@vit.edu"},
        headers={"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"}
    )
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert json_data["status"] == "select_role"
    assert len(json_data["roles"]) == 3

    sel_resp = client.post(
        "/api/auth/select-role",
        json={
            "club_id": "CSI",
            "club_name": "Computer Society of India",
            "club_role": "Secretary",
            "role_tier": "coordinator",
            "role_title": "Secretary of Computer Society of India"
        }
    )
    assert sel_resp.status_code == 200
    sel_data = sel_resp.get_json()
    assert sel_data["success"] is True
    assert sel_data["role"] == "coordinator"
    assert sel_data["club_id"] == "CSI"

def test_database_records_retention_and_tables(client):
    """
    Verifies that all 8 tables and records are retained and queryable:
    Students (75), Clubs (5), Events (>=10), Memberships (>=90).
    """
    from app.db import get_db_connection
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS c FROM Students;")
        assert cur.fetchone()["c"] >= 75
        cur.execute("SELECT COUNT(*) AS c FROM Clubs;")
        assert cur.fetchone()["c"] >= 5
        cur.execute("SELECT COUNT(*) AS c FROM Events;")
        assert cur.fetchone()["c"] >= 10
        cur.execute("SELECT COUNT(*) AS c FROM Memberships;")
        assert cur.fetchone()["c"] >= 90
    conn.close()

    # Also verify that events and students page render with records in HTML
    client.get("/guest")
    events_html = client.get("/events").data.decode()
    assert "No events found." not in events_html
    assert "EVT-" in events_html or "TechFest" in events_html or "E-Summit" in events_html

    students_html = client.get("/students").data.decode()
    assert "No students found." not in students_html
    assert "CE25-" in students_html


def test_student_department_filters_and_dom_attributes(client):
    """
    Verifies that the students directory contains exact department attributes
    and pills for CE, ME, EE, ELE to prevent multi-filter collisions.
    """
    client.get("/guest")
    resp = client.get("/students")
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")

    # Check that department pills exist
    assert 'data-filter="all"' in html
    assert 'data-filter="CE"' in html
    assert 'data-filter="ME"' in html
    assert 'data-filter="EE"' in html
    assert 'data-filter="ELE"' in html

    # Check KPI cards
    assert 'data-kpi-filter="all"' in html
    assert 'data-kpi-filter="CE"' in html
    assert 'data-kpi-filter="ME"' in html
    assert 'data-kpi-filter="CIRCUITS"' in html

    # Check row data attributes
    assert 'data-dept="CE"' in html
    assert 'data-dept="ME"' in html
    assert 'data-dept="EE"' in html
    assert 'data-dept="ELE"' in html

    # Verify counts: CE (52), ME (9), EE (8), ELE (6)
    assert 'CE (52)' in html
    assert 'ME (9)' in html
    assert 'EE (8)' in html
    assert 'ELE (6)' in html


def test_theme_toggle_and_trigger_pill_buttons(client):
    """
    Verifies that the new theme toggle button, Outfit typography,
    and rounded pill action buttons on triggers and procedures are present.
    """
    client.get("/guest")
    
    # 1. Base template has theme toggle button and font
    base_html = client.get("/").data.decode("utf-8")
    assert 'id="theme-toggle-btn"' in base_html
    assert 'Outfit' in base_html
    assert 'Plus+Jakarta+Sans' in base_html

    # 2. Triggers page has rounded pill action buttons (btn-trigger-pill)
    triggers_html = client.get("/triggers").data.decode("utf-8")
    assert 'btn-trigger-pill' in triggers_html
    assert 'btn-cyan' in triggers_html
    assert 'Auto-increments Club member count' in triggers_html

    # 3. Procedures page has condensed, punchy descriptions
    proc_html = client.get("/procedures").data.decode("utf-8")
    assert 'Audits cached club member counts' in proc_html
    assert 'Auto-enrolls them as club volunteers' in proc_html or 'auto-enrolls them' in proc_html


def test_light_theme_high_contrast_and_resilient_events(client):
    """
    Verifies that high-contrast light theme rules, solid borders,
    and resilient data loading for events and students are all active.
    """
    client.get("/guest")

    # 1. Check Events page loads all 12 events
    events_html = client.get("/events").data.decode("utf-8")
    assert 'CSI TechFest 26' in events_html
    assert 'E-Summit 26' in events_html
    assert 'CodeStorm Hackathon 26' in events_html
    assert 'table-surface-card' in events_html

    # 2. Check tokens.css has solid slate borders in light mode
    with open("app/static/css/tokens.css", "r", encoding="utf-8") as f:
        tokens_css = f.read()
    assert '[data-theme="light"]' in tokens_css
    assert '--border: #CBD5E1;' in tokens_css
    assert '--border-strong: #94A3B8;' in tokens_css
    assert '--text-1: #0F172A;' in tokens_css

    # 3. Check components.css has crisp boundaries and text-white safety override
    with open("app/static/css/components.css", "r", encoding="utf-8") as f:
        comp_css = f.read()
    assert '[data-theme="light"] .table-surface-card' in comp_css
    assert '1.5px solid #CBD5E1 !important;' in comp_css
    assert '[data-theme="light"] .tesla-table thead' in comp_css
    assert 'border-bottom: 2px solid #94A3B8 !important;' in comp_css
    assert '[data-theme="light"] .text-white' in comp_css

    # 4. Check base.html has cache-busting version params
    base_html = client.get("/").data.decode("utf-8")
    assert 'tokens.css?v=' in base_html
    assert 'components.css?v=' in base_html
    assert 'main.js?v=' in base_html




