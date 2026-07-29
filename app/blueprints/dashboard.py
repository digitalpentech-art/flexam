from flask import Blueprint, render_template
from app.models.metadata import EntityDefinition
from app.core.tenancy import get_current_tenant_id

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/ui-builder/<uuid:entity_id>')
def ui_builder(entity_id):
    tenant_id = get_current_tenant_id()
    entity = EntityDefinition.query.filter_by(id=entity_id, tenant_id=tenant_id).first_or_404()
    return render_template('dashboard/ui_builder.html', entity=entity)
