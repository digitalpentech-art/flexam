import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.extensions import db

class EntityDefinition(db.Model):
    __tablename__ = 'entity_definitions'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    name = db.Column(db.String(64), nullable=False) # e.g., "Student", "Course"
    plural_name = db.Column(db.String(64))
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_system = db.Column(db.Boolean, default=False) # True if it's a template entity

    fields = db.relationship('FieldDefinition', backref='entity', lazy='dynamic', cascade='all, delete-orphan')

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
    
    order = db.Column(db.Integer, default=0)

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
