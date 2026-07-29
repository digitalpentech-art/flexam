import uuid
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.extensions import db

class Assessment(db.Model):
    __tablename__ = 'assessments'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    
    components = db.relationship('AssessmentComponent', backref='assessment', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Assessment {self.name}>'

class AssessmentComponent(db.Model):
    __tablename__ = 'assessment_components'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = db.Column(UUID(as_uuid=True), db.ForeignKey('assessments.id'), nullable=False)
    
    name = db.Column(db.String(64), nullable=False)
    component_type = db.Column(db.String(32), nullable=False) # objective_cbt, theory, etc.
    enforced_question_type = db.Column(db.String(32), nullable=True) # If set, restricts question types in this component
    weight = db.Column(db.Float, default=1.0)
    
    configuration = db.Column(JSONB) # Randomization rules, time allocation
    allowed_response_modes = db.Column(db.ARRAY(db.String(32)), default=['keyboard']) # ['keyboard', 'handwriting', 'file']
    
    questions = db.relationship('Question', backref='component', lazy='dynamic')
