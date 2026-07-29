import pytest
from app import create_app, db

@pytest.fixture
def app():
    app = create_app('testing')
    app.config['TALISMAN_ENABLED'] = False
    
    with app.app_context():
        print("DEBUG: Creating DB...")
        db.create_all()
        yield app
        print("DEBUG: Removing session...")
        db.session.remove()
        print("DEBUG: Dropping DB...")
        db.drop_all()
        print("DEBUG: Drop complete.")

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client, tenant):
    # Helper to log in a user for tests
    return client
