import pytest
import json
from app import db
from app.models.core import User, Tenant
from app.models.metadata import EntityDefinition, PageDefinition, ComponentDefinition, LayoutDefinition

@pytest.fixture
def e2e_data(app):
    with app.app_context():
        # Setup Tenant & Admin User
        tenant = Tenant(name="E2E Tenant", slug="e2e-tenant")
        db.session.add(tenant)
        db.session.commit()
        tenant_id = tenant.id
        
        user = User(email="admin@e2e.com", tenant_id=tenant_id)
        user.password = "password"
        db.session.add(user)
        
        # Setup Dynamic Entity
        entity = EntityDefinition(name="Task", tenant_id=tenant_id)
        db.session.add(entity)
        db.session.flush()
        entity_name = entity.name
        
        # Setup Page & Layout
        page = PageDefinition(tenant_id=tenant_id, name="E2E Dashboard", slug="e2e-dashboard")
        db.session.add(page)
        db.session.flush()
        page_slug = page.slug
        
        comp = ComponentDefinition(tenant_id=tenant_id, name="Task Table", component_type="table", configuration={
            "columns": [{"key": "title", "label": "Title"}],
            "data": []
        })
        db.session.add(comp)
        db.session.flush()
        
        layout = LayoutDefinition(tenant_id=tenant_id, page_id=page.id, component_id=comp.id)
        db.session.add(layout)
        db.session.commit()
        
        return tenant_id, entity_name, page_slug

def test_full_dynamic_flow(client, e2e_data):
    tenant_id, entity_name, page_slug = e2e_data
    
    # 1. Login
    client.post('/auth/login', data={'email': 'admin@e2e.com', 'password': 'password'})
    
    # 2. Access Dynamic Dashboard
    response = client.get(f"/dashboard/{page_slug}")
    assert response.status_code == 200
    assert "Task Table" in response.data.decode('utf-8')
    
    # 3. Perform Dynamic CRUD (Create Record)
    crud_url = f"/api/crud/{entity_name}/create"
    response = client.post(crud_url, json={"title": "E2E Task"}, 
                           headers={"Content-Type": "application/json", "X-CSRFToken": "dummy"})
    assert response.status_code == 201
    
    # 4. Verify Persistence
    response = client.get(f"/api/crud/{entity_name}/read")
    assert response.status_code == 200
    records = json.loads(response.data)
    assert len(records) == 1
    assert records[0]["data"]["title"] == "E2E Task"
