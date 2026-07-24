from flask import Blueprint, render_template
from app.models.metadata import EntityDefinition

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
def dashboard():
    return render_template('dashboard/admin.html')

@admin_bp.route('/admin/entity/<uuid:entity_id>/test-form')
def test_form(entity_id):
    entity = EntityDefinition.query.get_or_404(entity_id)
    return render_template('dashboard/test_form.html', entity=entity)
