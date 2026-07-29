import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.extensions import db

class Examination(db.Model):
    __tablename__ = 'examinations'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    assessment_id = db.Column(UUID(as_uuid=True), db.ForeignKey('assessments.id'), nullable=False)
    assessment = db.relationship('Assessment', backref='examinations')
    
    name = db.Column(db.String(128), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f'<Examination {self.name}>'

class ExamAttempt(db.Model):
    __tablename__ = 'exam_attempts'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    examination_id = db.Column(UUID(as_uuid=True), db.ForeignKey('examinations.id'), nullable=False)
    examination = db.relationship('Examination', backref='attempts')
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref='attempts')
    
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(32), default='in_progress') # in_progress, completed, timed_out
    
    def __repr__(self):
        return f'<ExamAttempt {self.id} (Status: {self.status})>'

class IntegrityLog(db.Model):
    __tablename__ = 'integrity_logs'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id = db.Column(UUID(as_uuid=True), db.ForeignKey('exam_attempts.id'), nullable=False)
    
    event_type = db.Column(db.String(64), nullable=False) # e.g., 'tab_switch', 'fullscreen_exit'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    event_metadata = db.Column(JSONB, default={})
