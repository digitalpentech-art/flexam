import uuid
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.extensions import db

class GradingRule(db.Model):
    __tablename__ = 'grading_rules'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    
    name = db.Column(db.String(64), nullable=False) # e.g., "Default Secondary Scale"
    rules = db.Column(JSONB, nullable=False) # e.g., {"A": {"min": 70}, "B": {"min": 60}}

    def __repr__(self):
        return f'<GradingRule {self.name} (Tenant: {self.tenant_id})>'
