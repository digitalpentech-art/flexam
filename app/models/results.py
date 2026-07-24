import uuid
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.extensions import db

class Result(db.Model):
    __tablename__ = 'results'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    exam_attempt_id = db.Column(UUID(as_uuid=True), db.ForeignKey('exam_attempts.id'), nullable=False)
    
    total_score = db.Column(db.Float, default=0.0)
    final_grade = db.Column(db.String(10))
    is_published = db.Column(db.Boolean, default=False)
    
    components = db.relationship('ResultComponent', backref='result', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Result {self.id} (Score: {self.total_score})>'

class ResultComponent(db.Model):
    __tablename__ = 'result_components'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    result_id = db.Column(UUID(as_uuid=True), db.ForeignKey('results.id'), nullable=False)
    assessment_component_id = db.Column(UUID(as_uuid=True), db.ForeignKey('assessment_components.id'), nullable=False)
    assessment_component = db.relationship('AssessmentComponent')
    
    score = db.Column(db.Float, default=0.0)
    raw_data = db.Column(JSONB) # For storing specific response details
