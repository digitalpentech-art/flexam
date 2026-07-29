import pytest
from app import db
from app.models.metadata import EntityDefinition, FieldDefinition
from app.models.core import Tenant

def test_metadata_engine_crud(app):
    with app.app_context():
        # Setup
        tenant = Tenant(name="TestTenant", slug="test-tenant")
        db.session.add(tenant)
        db.session.commit()

        # Test Entity Creation
        entity = EntityDefinition(name="TestEntity", tenant_id=tenant.id)
        db.session.add(entity)
        db.session.commit()
        
        # Test Field Creation
        field = FieldDefinition(entity_id=entity.id, name="test_field", label="Test Field", field_type="text")
        db.session.add(field)
        db.session.commit()
        
        assert EntityDefinition.query.filter_by(name="TestEntity").first() is not None
        assert FieldDefinition.query.filter_by(name="test_field").first() is not None

def test_tenancy_isolation(app):
    with app.app_context():
        # Setup
        tenant1 = Tenant(name="Tenant1", slug="t1")
        tenant2 = Tenant(name="Tenant2", slug="t2")
        db.session.add_all([tenant1, tenant2])
        db.session.commit()
        
        # Create records for different tenants
        e1 = EntityDefinition(name="Entity1", tenant_id=tenant1.id)
        e2 = EntityDefinition(name="Entity2", tenant_id=tenant2.id)
        db.session.add_all([e1, e2])
        db.session.commit()
        
        # Simulate tenant context (needs UI Service / Tenancy setup)
        from app.core.tenancy import set_current_tenant
        
        set_current_tenant(tenant1.id)
        results = EntityDefinition.query.all()
        assert len(results) == 1
        assert results[0].name == "Entity1"
