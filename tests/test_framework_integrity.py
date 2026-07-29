import pytest
from app import db
from app.models.core import User, Role, Tenant
from app.models.metadata import EntityDefinition, Record
from app.models.security import SecurityPolicy
from app.core.crud_service import CrudService
from app.core.tenancy import set_current_tenant

@pytest.fixture
def auth_client(client, app):
    with app.app_context():
        # Setup KIU tenant and admin
        tenant = Tenant(name="KIU", slug="kiu")
        db.session.add(tenant)
        db.session.commit()
        
        admin_role = Role(name="Admin", tenant_id=tenant.id)
        examiner_role = Role(name="Examiner", tenant_id=tenant.id)
        db.session.add_all([admin_role, examiner_role])
        db.session.commit()
        
        admin = User(email="admin@test.com", tenant_id=tenant.id, is_superadmin=True, role_id=admin_role.id)
        admin.password = "password"
        
        examiner = User(email="exam@test.com", tenant_id=tenant.id, role_id=examiner_role.id)
        examiner.password = "password"
        
        db.session.add_all([admin, examiner])
        db.session.commit()
        
        # Entities
        entity = EntityDefinition(tenant_id=tenant.id, name="TestEntity")
        db.session.add(entity)
        db.session.commit()
        
        # Records
        record1 = Record(tenant_id=tenant.id, entity_definition_id=entity.id, data={'dept': 'CS'})
        record2 = Record(tenant_id=tenant.id, entity_definition_id=entity.id, data={'dept': 'Math'})
        db.session.add_all([record1, record2])
        db.session.commit()
        
        # Capture IDs inside the context
        t_id, e_id, ex_id, ad_id, er_id = tenant.id, entity.id, examiner.id, admin.id, examiner.role_id
        
    # Return IDs
    return client, t_id, e_id, ex_id, ad_id, er_id

def test_framework_integrity(auth_client):
    client, tenant_id, entity_id, examiner_id, admin_id, examiner_role_id = auth_client
    
    # 1. Test Admin Builder Routes
    resp = client.post('/admin/relationships', data={
        'name': 'TestRel',
        'source_entity_id': str(entity_id),
        'target_entity_id': str(entity_id),
        'relationship_type': 'one_to_one'
    }, follow_redirects=True)
    assert resp.status_code == 200
    
    # 2. Test Security Policy Creation
    print(f"DEBUG: Examiner role ID: {examiner_role_id}")
    resp = client.post('/admin/security', data={
        'csrf_token': 'test_token',
        'entity_definition_id': str(entity_id),
        'role_id': str(examiner_role_id),
        'action': 'READ',
        'db_column': 'dept',
        'user_attribute_key': 'first_name' 
    }, follow_redirects=True)
    assert resp.status_code == 200
    
    # 3. Test Security Policy Enforcement in CrudService
    with client.application.app_context():
        # Update user first_name
        from app.models.core import User
        examiner = User.query.get(examiner_id)
        print(f"DEBUG: User role ID: {examiner.role_id}")
        examiner.first_name = 'CS'
        db.session.commit()
        
        # Authenticate as examiner
        client.post('/auth/login', data={'email': 'exam@test.com', 'password': 'password'})
        
        # Manually set current_user for the test context
        from flask_login import login_user
        from unittest.mock import patch
        
        examiner = User.query.get(examiner_id)
        
        # Use patch to mock current_user
        with patch('app.core.crud_service.current_user', examiner):
            set_current_tenant(tenant_id)
            
            # Should only see record with dept 'CS'
            all_policies = SecurityPolicy.query.all()
            print(f"DEBUG: All policies in DB: {all_policies}")
            records = CrudService.read_records(entity_id)
            assert len(records) == 1

            assert records[0].data['dept'] == 'CS'
            
        print("Framework integrity verified: Policy enforced.")
