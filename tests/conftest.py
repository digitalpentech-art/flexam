import pytest
from app import create_app, db

@pytest.fixture
def app():
    app = create_app('testing')
    # Talisman can interfere with test clients, disable for tests if necessary
    app.config['TALISMAN_ENABLED'] = False
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client, tenant):
    # Helper to log in a user for tests
    return client
