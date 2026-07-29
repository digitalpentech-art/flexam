from app.extensions import db
from app.models.metadata import FieldDefinition, EntityDefinition
from sqlalchemy.orm.attributes import flag_modified

class SchemaManager:
    @staticmethod
    def sync_schema(entity_id, layout_data):
        """
        Synchronizes the Entity's FieldDefinition records with the provided layout.
        """
        provided_field_ids = []
        
        # 1. Handle Additions and Updates
        for field_layout in layout_data.get('fields', []):
            field_id = field_layout.get('field_id')
            position = field_layout.get('position', {})
            field_type = field_layout.get('field_type')
            
            if field_id:
                # Update existing
                field = FieldDefinition.query.filter_by(id=field_id, entity_id=entity_id).first()
            else:
                # Add new
                field = FieldDefinition(
                    entity_id=entity_id,
                    name=f"field_{field_type}_{len(FieldDefinition.query.filter_by(entity_id=entity_id).all()) + 1}",
                    label=f"New {field_type.capitalize()} Field",
                    field_type=field_type
                )
                db.session.add(field)
                db.session.flush() # Get ID
            
            if field:
                ui_config = field.ui_config or {}
                # Update positioning
                ui_config.update({
                    'x': position.get('x'),
                    'y': position.get('y'),
                    'w': position.get('width'),
                    'h': position.get('height')
                })
                # Update styling (if provided in the payload)
                if 'styling' in field_layout:
                    ui_config['styling'] = field_layout['styling']
                
                field.ui_config = ui_config
                flag_modified(field, 'ui_config') # MARK AS DIRTY
                provided_field_ids.append(field.id)
        
        # 2. Handle Deletions (remove fields not in provided layout)
        existing_fields = FieldDefinition.query.filter_by(entity_id=entity_id).all()
        for field in existing_fields:
            if field.id not in provided_field_ids:
                db.session.delete(field)
        
        db.session.commit()

