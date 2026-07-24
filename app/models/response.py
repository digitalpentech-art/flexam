import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.extensions import db

class Response(db.Model):
    __tablename__ = 'responses'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id = db.Column(UUID(as_uuid=True), db.ForeignKey('exam_attempts.id'), nullable=False)
    component_id = db.Column(UUID(as_uuid=True), db.ForeignKey('assessment_components.id'), nullable=False)
    question_id = db.Column(UUID(as_uuid=True), db.ForeignKey('questions.id'), nullable=True)
    
    response_mode = db.Column(db.String(32), nullable=False) # keyboard, handwriting, file, simulation, etc.
    content = db.Column(JSONB) # Structured data: e.g., {'text': '...'} or {'strokes': [...]} or {'file_url': '...'}
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    version = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f'<Response {self.id} (Mode: {self.response_mode})>'
