import uuid
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.extensions import db

class PracticalTask(db.Model):
    __tablename__ = 'practical_tasks'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_component_id = db.Column(UUID(as_uuid=True), db.ForeignKey('assessment_components.id'), nullable=False)
    
    name = db.Column(db.String(128), nullable=False)
    simulation_type = db.Column(db.String(32), nullable=False) # plugin identifier (e.g., 'network_sim')
    initial_state = db.Column(JSONB)
    scoring_rules = db.Column(JSONB)

class SimulationState(db.Model):
    __tablename__ = 'simulation_states'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id = db.Column(UUID(as_uuid=True), db.ForeignKey('exam_attempts.id'), nullable=False)
    task_id = db.Column(UUID(as_uuid=True), db.ForeignKey('practical_tasks.id'), nullable=False)
    
    state_data = db.Column(JSONB) # current state
    is_complete = db.Column(db.Boolean, default=False)
