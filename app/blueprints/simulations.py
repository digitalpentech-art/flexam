from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.simulation import SimulationState, PracticalTask
from app.models.examination import ExamAttempt
from app.simulations.engine import SimulationEngine
from flask_login import login_required, current_user

simulations_bp = Blueprint('simulations', __name__)

@simulations_bp.route('/<uuid:attempt_id>/state', methods=['POST'])
@login_required
def update_simulation_state(attempt_id):
    data = request.json
    attempt = ExamAttempt.query.get_or_404(attempt_id)
    
    if attempt.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
        
    task = PracticalTask.query.get_or_404(data['task_id'])
    
    # Use Simulation Engine to validate
    plugin = SimulationEngine.get_plugin(task)
    if not plugin.validate_state(data['state_data']):
        return jsonify({"error": "Invalid simulation state"}), 400
        
    state = SimulationState.query.filter_by(attempt_id=attempt.id, task_id=task.id).first()
    if not state:
        state = SimulationState(attempt_id=attempt.id, task_id=task.id, state_data=data['state_data'])
        db.session.add(state)
    else:
        state.state_data = data['state_data']
        
    db.session.commit()
    return jsonify({"message": "State updated"}), 200
