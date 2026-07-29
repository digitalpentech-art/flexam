from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.utils.auth import roles_required
from app.models.examination import Examination

examiner_bp = Blueprint('examiner', __name__)

@examiner_bp.route('/examiner')
@login_required
@roles_required(['Examiner', 'Admin'])
def dashboard():
    # Fetch examinations for the current tenant
    examinations = Examination.query.filter_by(tenant_id=current_user.tenant_id).all()
    return render_template('dashboard/examiner.html', examinations=examinations)
