from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.results import Result, ResultComponent
from app.models.examination import ExamAttempt
from app.models.assessment import AssessmentComponent
from flask_login import login_required
from app.utils.grading import compute_grade

markings_bp = Blueprint('markings', __name__)

@markings_bp.route('/component/<uuid:attempt_id>/<uuid:component_id>', methods=['POST'])
@login_required
def submit_component_mark(attempt_id, component_id):
    # ... (existing function) ...
    data = request.json
    attempt = ExamAttempt.query.get_or_404(attempt_id)
    component = AssessmentComponent.query.get_or_404(component_id)
    
    # Logic: If automated, compare response with answer key
    # If manual, examiner submits score
    
    result = Result.query.filter_by(exam_attempt_id=attempt.id).first()
    if not result:
        result = Result(tenant_id=attempt.examination.tenant_id, exam_attempt_id=attempt.id)
        db.session.add(result)
        db.session.flush()
        
    res_comp = ResultComponent.query.filter_by(result_id=result.id, assessment_component_id=component.id).first()
    if not res_comp:
        res_comp = ResultComponent(result_id=result.id, assessment_component_id=component.id)
        db.session.add(res_comp)
        
    res_comp.score = data['score']
    db.session.commit()
    
    return jsonify({"message": "Mark submitted"}), 200

@markings_bp.route('/finalize/<uuid:attempt_id>', methods=['POST'])
@login_required
def finalize_result(attempt_id):
    result = Result.query.filter_by(exam_attempt_id=attempt_id).first_or_404()
    
    # Aggregate component scores based on weights
    total = 0.0
    for res_comp in result.components.all():
        total += (res_comp.score * res_comp.assessment_component.weight)
        
    result.total_score = total
    # Use the grading service
    result.final_grade = compute_grade(result.tenant_id, total)
    
    db.session.commit()
    return jsonify({"message": "Result finalized", "total_score": total, "grade": result.final_grade}), 200
