import pytest
from app import db
from app.models.core import User
from app.models.metadata import EntityDefinition

@pytest.fixture
def auth_client(client, app):
    with app.app_context():
        # Setup a dummy admin user
        from app.models.core import Tenant, Role
        tenant = Tenant(name="TestTenant", slug="test-tenant")
        db.session.add(tenant)
        db.session.commit()

        admin_role = Role(name="Admin", tenant_id=tenant.id)
        db.session.add(admin_role)
        db.session.commit()

        user = User(email="admin@test.com", tenant_id=tenant.id, is_superadmin=True, role_id=admin_role.id)
        user.password = "password"
        db.session.add(user)
        db.session.commit()

        # Add some entities
        entity1 = EntityDefinition(tenant_id=tenant.id, name="Entity1")
        entity2 = EntityDefinition(tenant_id=tenant.id, name="Entity2")
        db.session.add_all([entity1, entity2])
        db.session.commit()
        
    client.post('/auth/login', data={'email': 'admin@test.com', 'password': 'password'})
    return client

def test_manage_entities_rendering(auth_client):
    response = auth_client.get("/admin/entities")
    
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    
    # Verify entity names are in the HTML
    assert "Entity1" in html
    assert "Entity2" in html
    
    # Verify the table exists
    assert 'id="entities-table"' in html
    
    print("Entities rendered in HTML response successfully.")
