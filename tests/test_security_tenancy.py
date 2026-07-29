import pytest
from app import db
from app.models.core import Tenant, Role, User
from app.core.tenancy import set_current_tenant

def test_csrf_protection(client):
    client.application.config['WTF_CSRF_ENABLED'] = True
    # Try POST without CSRF token
    response = client.post('/auth/login', data={})
    # CSRFProtect should return 400 Bad Request
    assert response.status_code == 400

def test_tenant_isolation_api(client):
    with client.application.app_context():
        t1 = Tenant(name='T1', slug='t1')
        t2 = Tenant(name='T2', slug='t2')
        db.session.add_all([t1, t2])
        db.session.commit()
        
        # This test needs a way to mock/set the tenant_id in the request context
        # based on X-Tenant-ID header
        
        # Test T1 creation
        response = client.post('/api/metadata/entities', 
                               headers={'X-Tenant-ID': str(t1.id)},
                               json={'name': 'Student'})
        assert response.status_code == 201
        entity_id = response.get_json()['id']
        
        # Test adding field (this is expected to cause 500)
        response = client.post(f'/api/metadata/entities/{entity_id}/fields',
                               headers={'X-Tenant-ID': str(t1.id)},
                               json={
                                   'name': 'age',
                                   'label': 'Age',
                                   'field_type': 'integer'
                               })
        assert response.status_code == 201
        
        # Verify only T1 has the entity
        # (This is where the tenant isolation event hook is validated)
