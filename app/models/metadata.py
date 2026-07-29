import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.extensions import db

class SequenceState(db.Model):
    __tablename__ = 'sequence_states'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    entity_definition_id = db.Column(UUID(as_uuid=True), db.ForeignKey('entity_definitions.id'), nullable=False)
    
    # The next available value to assign
    next_value = db.Column(db.Integer, default=1)
    
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'entity_definition_id', name='_tenant_entity_sequence_uc'),
    )

    def __repr__(self):
        return f'<SequenceState {self.next_value} (Tenant: {self.tenant_id}, Entity: {self.entity_definition_id})>'

class EntityDefinition(db.Model):
    __tablename__ = 'entity_definitions'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    name = db.Column(db.String(64), nullable=False) # e.g., "Student", "Course"
    plural_name = db.Column(db.String(64))
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_system = db.Column(db.Boolean, default=False) # True if it's a template entity
    layout_config = db.Column(JSONB, default={}) # New field for storing drag-and-drop layout

    fields = db.relationship('FieldDefinition', 
                             backref='entity', 
                             lazy='dynamic', 
                             cascade='all, delete-orphan',
                             foreign_keys='[FieldDefinition.entity_id]')

    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'name', name='_tenant_entity_uc'),
    )

    def __repr__(self):
        return f'<EntityDefinition {self.name} (Tenant: {self.tenant_id})>'

class FieldDefinition(db.Model):
    __tablename__ = 'field_definitions'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id = db.Column(UUID(as_uuid=True), db.ForeignKey('entity_definitions.id'), nullable=False)
    name = db.Column(db.String(64), nullable=False) # e.g., "first_name", "credit_hours"
    label = db.Column(db.String(128), nullable=False) # e.g., "First Name"
    field_type = db.Column(db.String(32), nullable=False) # text, number, date, boolean, select, reference
    is_required = db.Column(db.Boolean, default=False)
    is_unique = db.Column(db.Boolean, default=False)
    default_value = db.Column(db.String(255))
    validation_rules = db.Column(JSONB) # Regex, min/max, etc.
    choices = db.Column(JSONB) # For select fields
    
    # For reference fields
    related_entity_id = db.Column(UUID(as_uuid=True), db.ForeignKey('entity_definitions.id'))
    
    # UI/Studio configuration
    ui_config = db.Column(JSONB, default={})
    position = db.Column(db.Integer, default=0)

    __table_args__ = (
        db.UniqueConstraint('entity_id', 'name', name='_entity_field_uc'),
    )

    def __repr__(self):
        return f'<FieldDefinition {self.name} for {self.entity_id}>'

class RelationshipDefinition(db.Model):
    __tablename__ = 'relationship_definitions'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    
    source_entity_id = db.Column(UUID(as_uuid=True), db.ForeignKey('entity_definitions.id'), nullable=False)
    target_entity_id = db.Column(UUID(as_uuid=True), db.ForeignKey('entity_definitions.id'), nullable=False)
    
    relationship_type = db.Column(db.String(32), nullable=False) # one_to_one, one_to_many, many_to_many
    
    # For many_to_many, we might need a dynamic junction table approach or a generic RecordLink table.
    # For now, let's stick to the concept.

class Record(db.Model):
    """
    A generic container for a record of a dynamic entity.
    """
    __tablename__ = 'records'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    entity_definition_id = db.Column(UUID(as_uuid=True), db.ForeignKey('entity_definitions.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))

    # Option A: Store all values in a JSONB blob (Fastest to implement, good for search)
    data = db.Column(JSONB, nullable=False, default={})

    def __repr__(self):
        return f'<Record {self.id} (Entity: {self.entity_definition_id})>'

class RecordLink(db.Model):
    """
    Generic many-to-many link table for dynamic records.
    """
    __tablename__ = 'record_links'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    relationship_id = db.Column(UUID(as_uuid=True), db.ForeignKey('relationship_definitions.id'), nullable=False)
    
    source_record_id = db.Column(UUID(as_uuid=True), db.ForeignKey('records.id'), nullable=False)
    target_record_id = db.Column(UUID(as_uuid=True), db.ForeignKey('records.id'), nullable=False)

class PageDefinition(db.Model):
    __tablename__ = 'page_definitions'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    name = db.Column(db.String(64), nullable=False) # e.g., "Student Dashboard"
    slug = db.Column(db.String(64), nullable=False, index=True) # e.g., "student-dashboard"
    
    layouts = db.relationship('LayoutDefinition', backref='page', lazy='dynamic', cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'slug', name='_tenant_page_slug_uc'),
    )

    def __repr__(self):
        return f'<PageDefinition {self.name} ({self.slug})>'

class ComponentDefinition(db.Model):
    __tablename__ = 'component_definitions'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    name = db.Column(db.String(64), nullable=False) # e.g., "TableComponent", "MetricCard"
    component_type = db.Column(db.String(32), nullable=False) # e.g., "table", "chart", "form"
    configuration = db.Column(JSONB, default={}) # Props for the component
    
    # Entity awareness
    entity_id = db.Column(UUID(as_uuid=True), db.ForeignKey('entity_definitions.id'), nullable=True)
    field_ids = db.Column(JSONB, default=[]) # List of FieldDefinition UUIDs to include

    entity = db.relationship('EntityDefinition', foreign_keys=[entity_id])

    def __repr__(self):
        return f'<ComponentDefinition {self.name} ({self.component_type})>'

class LayoutDefinition(db.Model):
    __tablename__ = 'layout_definitions'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    page_id = db.Column(UUID(as_uuid=True), db.ForeignKey('page_definitions.id'), nullable=False)
    component_id = db.Column(UUID(as_uuid=True), db.ForeignKey('component_definitions.id'), nullable=False)
    
    component = db.relationship('ComponentDefinition')
    position = db.Column(JSONB, default={'x': 0, 'y': 0, 'w': 12, 'h': 1})

class ExaminationSettings(db.Model):
    __tablename__ = 'examination_settings'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    examination_id = db.Column(UUID(as_uuid=True), db.ForeignKey('examinations.id'), nullable=False)
    # The JSONB config can store layout preferences or specific UI overrides
    settings = db.Column(JSONB, default={})


class MenuDefinition(db.Model):
    __tablename__ = 'menu_definitions'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    name = db.Column(db.String(64), nullable=False) # e.g., "Admin Sidebar"
    slug = db.Column(db.String(64), nullable=False) # e.g., "admin-sidebar"
    
    items = db.relationship('MenuItem', backref='menu', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<MenuDefinition {self.name}>'

class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    menu_id = db.Column(UUID(as_uuid=True), db.ForeignKey('menu_definitions.id'), nullable=False)
    label = db.Column(db.String(64), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    icon = db.Column(db.String(64))
    order = db.Column(db.Integer, default=0)
    required_role = db.Column(db.String(64)) # Permission check

    def __repr__(self):
        return f'<MenuItem {self.label} in {self.menu_id}>'
