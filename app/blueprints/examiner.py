from flask import Blueprint, render_template
from flask_login import login_required

examiner_bp = Blueprint('examiner', __name__)

@examiner_bp.route('/examiner')
@login_required
def dashboard():
    # Placeholder: List assessments to be marked
    return render_template('dashboard/examiner.html')
