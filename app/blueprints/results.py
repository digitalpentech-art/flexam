from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from app.models.examination import ExamAttempt
from app.models.results import Result

results_bp = Blueprint('results', __name__)

@results_bp.route('/<uuid:attempt_id>')
@login_required
def view_result(attempt_id):
    attempt = ExamAttempt.query.get_or_404(attempt_id)
    
    if attempt.user_id != current_user.id:
        abort(403)
        
    result = Result.query.filter_by(exam_attempt_id=attempt.id).first_or_404()
    
    return render_template('dashboard/results.html', result=result, attempt=attempt)
