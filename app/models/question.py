import uuid
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.extensions import db

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    component_id = db.Column(UUID(as_uuid=True), db.ForeignKey('assessment_components.id'), nullable=True)
    
    question_type = db.Column(db.String(32), nullable=False) # mcq, essay, etc.
    content = db.Column(JSONB, nullable=False) # Question text/media refs
    marks = db.Column(db.Integer, default=1)
    
    options = db.relationship('QuestionOption', backref='question', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Question {self.id} (Type: {self.question_type})>'

class QuestionOption(db.Model):
    __tablename__ = 'question_options'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = db.Column(UUID(as_uuid=True), db.ForeignKey('questions.id'), nullable=False)
    content = db.Column(db.String(512), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
