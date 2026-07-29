import pytest
from app.core.provisioner import SchemaProvisioner
from app.models.metadata import EntityDefinition, FieldDefinition
from app.extensions import db

def test_schema_provisioner(app):
    """
    Test that the SchemaProvisioner correctly creates entities and fields.
    """
    with app.app_context():
        # Create a dummy tenant
        from app.models.core import Tenant
        tenant = Tenant(name="Test Tenant", slug="test-tenant")
        db.session.add(tenant)
        db.session.commit()
        
        # Define a schema
        schema_config = {
            "entities": [
                {
                    "name": "Inventory",
                    "plural_name": "Inventories",
                    "fields": [
                        {"name": "item_name", "label": "Item Name", "field_type": "string"},
                        {"name": "quantity", "label": "Quantity", "field_type": "integer"}
                    ]
                }
            ]
        }
        
        # Run provisioner
        SchemaProvisioner.provision(tenant.id, schema_config)
        
        # Verify
        entity = EntityDefinition.query.filter_by(tenant_id=tenant.id, name="Inventory").first()
        assert entity is not None
        assert entity.plural_name == "Inventories"
        
        fields = FieldDefinition.query.filter_by(entity_id=entity.id).all()
        assert len(fields) == 2
        
        field_names = [f.name for f in fields]
        assert "item_name" in field_names
        assert "quantity" in field_names
