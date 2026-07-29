import uuid
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.extensions import db

class SecurityPolicy(db.Model):
    """
    Defines programmatic access rules for dynamic entities.
    Example: Role 'Examiner' can READ 'Record' IF 'department_id' == user.department_id
    """
    __tablename__ = 'security_policies'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    
    # Metadata scope
    entity_definition_id = db.Column(UUID(as_uuid=True), db.ForeignKey('entity_definitions.id'), nullable=False)
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey('roles.id'), nullable=False)
    
    # Action (READ, CREATE, UPDATE, DELETE)
    action = db.Column(db.String(32), nullable=False)
    
    # Filtering rules (JSONB: {'db_column': '...', 'operator': '==', 'user_attribute_key': '...'})
    filter_rules = db.Column(JSONB, default=[])

    def __repr__(self):
        return f'<SecurityPolicy {self.action} on {self.entity_definition_id} for role {self.role_id}>'
