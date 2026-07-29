import pytest
from app import db
from app.models.core import Tenant
from app.models.metadata import EntityDefinition, PageDefinition, Record
from app.core.ui_service import get_page_by_slug
from app.core.crud_service import CrudService
from app.core.tenancy import set_current_tenant

@pytest.fixture
def test_data(app):
    with app.app_context():
        tenant = Tenant(name="TestTenant", slug="t1")
        db.session.add(tenant)
        db.session.commit()
        tenant_id = tenant.id
        
        # Setup Page for Routing Test
        page = PageDefinition(tenant_id=tenant_id, name="TestPage", slug="test-page")
        db.session.add(page)
        
        # Setup Entity for CRUD Test
        entity = EntityDefinition(name="TestEntity", tenant_id=tenant_id)
        db.session.add(entity)
        db.session.commit()
        
        return tenant_id, page.id, entity.id

def test_dynamic_mapping_routing(app, test_data):
    tenant_id, page_id, entity_id = test_data
    with app.app_context():
        set_current_tenant(tenant_id)
        
        # Test routing lookup
        resolved_page = get_page_by_slug(tenant_id, "test-page")
        assert resolved_page.id == page_id

def test_generic_crud_engine(app, test_data):
    tenant_id, page_id, entity_id = test_data
    with app.app_context():
        set_current_tenant(tenant_id)
        
        # Test Create
        data = {"field1": "value1"}
        record = CrudService.create_record(entity_id, data)
        assert record.id is not None
        
        # Test Read
        records = CrudService.read_records(entity_id)
        assert len(records) == 1
        assert records[0].data["field1"] == "value1"
        
        # Test Update
        CrudService.update_record(record.id, {"field1": "updated"})
        updated_record = Record.query.get(record.id)
        assert updated_record.data["field1"] == "updated"
        
        # Test Delete
        CrudService.delete_record(record.id)
        assert len(CrudService.read_records(entity_id)) == 0
