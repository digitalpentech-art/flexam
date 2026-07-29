from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.extensions import db
from app.models.examination import ExamAttempt
from app.models.results import Result, ResultComponent
from app.models.response import Response
from app.utils.auth import roles_required
from app.utils.grading import calculate_score

grading_bp = Blueprint('grading', __name__)

@grading_bp.route('/grading/list', methods=['GET'])
@login_required
@roles_required(['Examiner', 'Admin'])
def list_pending_grading():
    # Find all attempts that are 'completed' and not fully graded
    # This is a simplified query; in production, you might track 'grading_status'
    attempts = ExamAttempt.query.filter_by(status='completed').all()
    return render_template('dashboard/grading_list.html', attempts=attempts)

@grading_bp.route('/grading/attempt/<uuid:attempt_id>', methods=['GET', 'POST'])
@login_required
@roles_required(['Examiner', 'Admin'])
def grade_attempt(attempt_id):
    attempt = ExamAttempt.query.get_or_404(attempt_id)
    result = Result.query.filter_by(exam_attempt_id=attempt.id).first_or_404()
    
    if request.method == 'POST':
        # Expecting JSON like {component_id: score}
        scores = request.json
        for comp_id, score in scores.items():
            res_comp = ResultComponent.query.filter_by(
                result_id=result.id, 
                assessment_component_id=comp_id
            ).first()
            if res_comp:
                res_comp.score = float(score)
        
        db.session.commit()
        # Recalculate total score
        calculate_score(attempt.id)
        return jsonify({"message": "Scores updated successfully"})
        
    responses = Response.query.filter_by(attempt_id=attempt.id).all()
    return render_template('dashboard/grade_attempt.html', attempt=attempt, result=result, responses=responses)
