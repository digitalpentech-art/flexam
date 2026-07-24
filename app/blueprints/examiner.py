from flask import Blueprint, render_template

examiner_bp = Blueprint('examiner', __name__)

@examiner_bp.route('/examiner')
def dashboard():
    # Placeholder: List assessments to be marked
    return render_template('dashboard/examiner.html')
