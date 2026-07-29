import pytest
from app import create_app, db
from app.models.core import User, Tenant

@pytest.fixture
def auth_client(client, app):
    with app.app_context():
        # Setup a dummy user and page to authenticate
        tenant = Tenant(name="TestTenant", slug="test-tenant")
        db.session.add(tenant)
        db.session.commit()
        
        user = User(email="test@example.com", tenant_id=tenant.id)
        user.password = "password"
        db.session.add(user)
        
        # Seed page, components, and layouts for dynamic routing test
        from app.models.metadata import PageDefinition, ComponentDefinition, LayoutDefinition
        page = PageDefinition(tenant_id=tenant.id, name="Full Dynamic Page", slug="full-dynamic")
        db.session.add(page)
        db.session.flush()

        table_comp = ComponentDefinition(tenant_id=tenant.id, name="Users Table", component_type="table", configuration={
            "columns": [{"key": "email", "label": "Email"}],
            "data": [{"id": "uuid-1", "email": "test@example.com"}]
        })
        db.session.add(table_comp)
        
        form_comp = ComponentDefinition(tenant_id=tenant.id, name="User Form", component_type="form", configuration={
            "submit_url": "/test-submit",
            "fields": [{"name": "username", "label": "Username", "field_type": "text"}]
        })
        db.session.add(form_comp)
        db.session.flush()

        layout1 = LayoutDefinition(tenant_id=tenant.id, page_id=page.id, component_id=table_comp.id, position={'x': 0, 'y': 0, 'w': 12, 'h': 1})
        layout2 = LayoutDefinition(tenant_id=tenant.id, page_id=page.id, component_id=form_comp.id, position={'x': 0, 'y': 1, 'w': 12, 'h': 1})
        db.session.add_all([layout1, layout2])
        db.session.commit()
        
    client.post('/auth/login', data={'email': 'test@example.com', 'password': 'password'})
    return client

def test_dynamic_page_rendering_client(auth_client):
    response = auth_client.get("/p/full-dynamic")
    
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    print(html) # Debug
    
    # Verify table rendering
    assert "Users Table" in html
    assert "test@example.com" in html
    
    # Verify form rendering
    assert "User Form" in html
    assert 'name="username"' in html
    assert 'type="submit"' in html
