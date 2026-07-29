from flask import Blueprint, jsonify
from app.utils.analytics import get_performance_metrics
from app.core.tenancy import get_current_tenant_id
from flask_login import login_required

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    return render_template('dashboard/analytics.html')

@analytics_bp.route('/summary', methods=['GET'])
@login_required
def get_summary():
    tenant_id = get_current_tenant_id()
    metrics = get_performance_metrics(tenant_id)
    return jsonify(metrics), 200
