import pytest
from app import create_app
from app.config import Config

class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-secret-key"

@pytest.fixture
def app():
    app = create_app(TestConfig)
    return app

@pytest.fixture
def client(app):
    return app.test_client()
