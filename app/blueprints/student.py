from flask import Blueprint, render_template
from flask_login import login_required

student_bp = Blueprint('student', __name__)

@student_bp.route('/student')
@login_required
def dashboard():
    # Placeholder: Fetch assigned exams for current student
    return render_template('dashboard/student.html')
