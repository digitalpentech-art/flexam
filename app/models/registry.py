import uuid
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.extensions import db

class ComponentRegistry(db.Model):
    """
    Acts as a blueprint/schema for component types.
    Defines what properties/configurations a component type accepts.
    """
    __tablename__ = 'component_registry'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # e.g., 'table', 'form', 'chart'
    component_type = db.Column(db.String(64), unique=True, nullable=False)
    
    # JSON schema defining required/optional props
    # e.g., {"entity_id": {"type": "reference", "required": true}, "show_search": {"type": "boolean"}}
    property_schema = db.Column(JSONB, default={})
    
    # UI configuration for the builder itself (e.g., icon, group)
    ui_metadata = db.Column(JSONB, default={})

    def __repr__(self):
        return f'<ComponentRegistry {self.component_type}>'
