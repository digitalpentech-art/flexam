from app.extensions import db
from app.models.metadata import EntityDefinition, FieldDefinition

class SchemaProvisioner:
    @staticmethod
    def provision(tenant_id, schema_config):
        """
        Creates entity and field definitions based on a JSON config.
        """
        if not schema_config:
            return
            
        # Basic Validation
        if 'entities' not in schema_config or not isinstance(schema_config['entities'], list):
            raise ValueError("Invalid schema configuration: 'entities' must be a list.")

        for entity_data in schema_config['entities']:
            if 'name' not in entity_data:
                raise ValueError("Entity definition missing required key: 'name'")
                
            # 1. Create or get EntityDefinition
            entity = EntityDefinition.query.filter_by(
                tenant_id=tenant_id, 
                name=entity_data['name']
            ).first()
            
            if not entity:
                entity = EntityDefinition(
                    tenant_id=tenant_id,
                    name=entity_data['name'],
                    plural_name=entity_data.get('plural_name'),
                    description=entity_data.get('description')
                )
                db.session.add(entity)
                db.session.flush()

            # 2. Create Fields
            for field_data in entity_data.get('fields', []):
                if 'name' not in field_data or 'label' not in field_data or 'field_type' not in field_data:
                    raise ValueError(f"Field in entity {entity_data['name']} missing required keys ('name', 'label', 'field_type')")
                    
                field = FieldDefinition.query.filter_by(
                    entity_id=entity.id,
                    name=field_data['name']
                ).first()
                
                if not field:
                    field = FieldDefinition(
                        entity_id=entity.id,
                        name=field_data['name'],
                        label=field_data['label'],
                        field_type=field_data['field_type'],
                        is_required=field_data.get('is_required', False)
                    )
                    db.session.add(field)
            
        db.session.commit()
