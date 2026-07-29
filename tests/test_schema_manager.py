import pytest
import uuid
from app import create_app, db
from app.models.metadata import EntityDefinition, FieldDefinition
from app.models.core import Tenant
from app.core.schema_manager import SchemaManager

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

def test_schema_manager_sync(app):
    with app.app_context():
        # Setup
        tenant = Tenant(name="TestTenant", slug="test-tenant")
        db.session.add(tenant)
        db.session.commit()
        
        entity = EntityDefinition(name="TestEntity", tenant_id=tenant.id)
        db.session.add(entity)
        db.session.commit()
        
        # Initial Layout Payload (Adding two fields)
        layout_data = {
            'fields': [
                {'field_type': 'text', 'position': {'x': 0, 'y': 0, 'width': 4, 'height': 1}},
                {'field_type': 'number', 'position': {'x': 4, 'y': 0, 'width': 4, 'height': 1}}
            ]
        }
        
        SchemaManager.sync_schema(entity.id, layout_data)
        
        # Sort by ID to ensure consistent order
        fields = sorted(FieldDefinition.query.filter_by(entity_id=entity.id).all(), key=lambda f: f.id)
        assert len(fields) == 2
        
        # Update/Delete Layout Payload (Keep one, delete one, add one)
        # We want to keep the one that was text, and delete the one that was number.
        text_field = next(f for f in fields if f.field_type == 'text')
        number_field = next(f for f in fields if f.field_type == 'number')
        
        new_layout = {
            'fields': [
                {'field_id': str(text_field.id), 'field_type': 'text', 'position': {'x': 0, 'y': 0, 'width': 2, 'height': 1}},
                {'field_type': 'text', 'position': {'x': 0, 'y': 1, 'width': 4, 'height': 1}}
            ]
        }
        
        SchemaManager.sync_schema(entity.id, new_layout)
        
        # Sort by ID to ensure consistent order
        updated_fields = sorted(FieldDefinition.query.filter_by(entity_id=entity.id).all(), key=lambda f: f.id)
        assert len(updated_fields) == 2
        
        # Verify the updated field (assuming the first one is the one we updated)
        # We need to find the correct one by ID.
        updated_field = FieldDefinition.query.filter_by(id=text_field.id).first()
        assert updated_field.ui_config['w'] == 2
        
        # Verify number field is deleted
        deleted_field = FieldDefinition.query.filter_by(id=number_field.id).first()
        assert deleted_field is None
        
        # Verify new text field exists
        new_text_fields = FieldDefinition.query.filter_by(entity_id=entity.id, field_type='text').all()
        assert len(new_text_fields) == 2
