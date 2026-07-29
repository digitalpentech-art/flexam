from flask import Blueprint, render_template
from flask_login import login_required
from app.core.tenancy import get_current_tenant_id
from app.core.ui_service import get_page_by_slug

dynamic_ui_bp = Blueprint('dynamic_ui', __name__)

@dynamic_ui_bp.route('/p/<slug>')
@login_required
def render_dynamic_page(slug):
    tenant_id = get_current_tenant_id()
    page = get_page_by_slug(tenant_id, slug)
    
    return render_template('dashboard/dynamic_wrapper.html', page=page)

@dynamic_ui_bp.route('/dashboard/<slug>')
@login_required
def render_dynamic_dashboard(slug):
    tenant_id = get_current_tenant_id()
    page = get_page_by_slug(tenant_id, slug)
    
    return render_template('dashboard/dynamic_wrapper.html', page=page)
