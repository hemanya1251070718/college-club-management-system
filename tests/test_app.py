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
    """Test memberships trigger demo page."""
    response = client.get("/memberships")
    assert response.status_code == 200
    assert b"Memberships &amp; Automatic Database Trigger" in response.data or b"Memberships & Automatic Database Trigger" in response.data

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
