import uuid
from datetime import datetime
from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID

class Attachment(db.Model):
    __tablename__ = 'attachments'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(512), nullable=False)
    mime_type = db.Column(db.String(128))
    
    # Polymorphic association to link to Questions or AssessmentComponents
    owner_id = db.Column(UUID(as_uuid=True), nullable=False)
    owner_type = db.Column(db.String(64), nullable=False) # 'question' or 'component'
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Attachment {self.filename}>'
