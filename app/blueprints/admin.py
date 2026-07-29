from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_wtf.csrf import generate_csrf
from app.models.metadata import EntityDefinition, FieldDefinition
from app.models.assessment import Assessment
from app.models.core import User, Role
from app import db
from app.utils.auth import roles_required
from app.core.types import FieldType

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_required
@roles_required(['Admin'])
def dashboard():
    assessments = Assessment.query.filter_by(tenant_id=current_user.tenant_id).all()
    return render_template('dashboard/admin.html', tenant=current_user.tenant, assessments=assessments)

@admin_bp.route('/admin/tenant/toggle-registration', methods=['POST'])
@login_required
@roles_required(['Admin'])
def toggle_registration():
    tenant = current_user.tenant
    tenant.allow_self_registration = not tenant.allow_self_registration
    db.session.commit()
    flash(f"Self-registration is now {'enabled' if tenant.allow_self_registration else 'disabled'}.")
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/admin/entities')
@login_required
@roles_required(['Admin'])
def manage_entities():
    print(f"DEBUG: Current User: {current_user.email}, Tenant ID: {current_user.tenant_id}")
    entities = EntityDefinition.query.filter_by(tenant_id=current_user.tenant_id).all()
    print(f"DEBUG: Entities found: {entities}")
    return render_template('dashboard/manage_entities.html', entities=entities)

@admin_bp.route('/admin/entities/create', methods=['POST'])
@login_required
@roles_required(['Admin'])
def create_entity():
    name = request.form.get('name')
    if EntityDefinition.query.filter_by(tenant_id=current_user.tenant_id, name=name).first():
        flash('Entity with this name already exists.')
    else:
        db.session.add(EntityDefinition(tenant_id=current_user.tenant_id, name=name))
        db.session.commit()
        flash('Entity created.')
    return redirect(url_for('admin.manage_entities'))

@admin_bp.route('/admin/entities/<uuid:entity_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required(['Admin'])
def edit_entity(entity_id):
    entity = EntityDefinition.query.filter_by(id=entity_id, tenant_id=current_user.tenant_id).first_or_404()
    if request.method == 'POST':
        entity.name = request.form['name']
        entity.plural_name = request.form['plural_name']
        entity.description = request.form['description']
        db.session.commit()
        flash('Entity updated.')
        return redirect(url_for('admin.manage_entities'))
    return render_template('dashboard/edit_entity.html', entity=entity)

@admin_bp.route('/admin/entities/<uuid:entity_id>/delete', methods=['POST'])
@login_required
@roles_required(['Admin'])
def delete_entity(entity_id):
    entity = EntityDefinition.query.filter_by(id=entity_id, tenant_id=current_user.tenant_id).first_or_404()
    db.session.delete(entity)
    db.session.commit()
    flash('Entity deleted.')
    return redirect(url_for('admin.manage_entities'))

@admin_bp.route('/admin/roles', methods=['GET', 'POST'])
@login_required
@roles_required(['Admin'])
def manage_roles():
    roles = Role.query.filter_by(tenant_id=current_user.tenant_id).all()
    if request.method == 'POST':
        # Simple role creation/update logic
        name = request.form['name']
        permissions = {perm: True for perm in request.form.getlist('permissions')}
        role = Role(name=name, tenant_id=current_user.tenant_id, permissions=permissions)
        db.session.add(role)
        db.session.commit()
        flash('Role created.')
        return redirect(url_for('admin.manage_roles'))
    return render_template('dashboard/manage_roles.html', roles=roles)

@admin_bp.route('/admin/entities/<uuid:entity_id>/fields', methods=['GET', 'POST'])
@login_required
@roles_required(['Admin'])
def manage_fields(entity_id):
    entity = EntityDefinition.query.filter_by(id=entity_id, tenant_id=current_user.tenant_id).first_or_404()
    if request.method == 'POST':
        # Add Field Logic
        field = FieldDefinition(
            entity_id=entity.id,
            name=request.form['name'],
            label=request.form['label'],
            field_type=request.form['field_type']
        )
        db.session.add(field)
        db.session.commit()
        flash('Field added.')
        return redirect(url_for('admin.manage_fields', entity_id=entity.id))
    
    return render_template('dashboard/manage_fields.html', entity=entity, field_types=FieldType.list(), EntityDefinition=EntityDefinition)

@admin_bp.route('/admin/assessments/build', methods=['GET'])
@login_required
@roles_required(['Admin'])
def build_assessment():
    assessments = Assessment.query.filter_by(tenant_id=current_user.tenant_id).all()
    return render_template('dashboard/build_assessment.html', assessments=assessments)

@admin_bp.route('/admin/assessments/<uuid:assessment_id>/delete', methods=['POST'])
@login_required
@roles_required(['Admin'])
def delete_assessment(assessment_id):
    assessment = Assessment.query.filter_by(id=assessment_id, tenant_id=current_user.tenant_id).first_or_404()
    db.session.delete(assessment)
    db.session.commit()
    flash('Assessment deleted successfully.', 'success')
    return redirect(url_for('admin.build_assessment'))

@admin_bp.route('/admin/assessments/<uuid:assessment_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required(['Admin'])
def edit_assessment(assessment_id):
    assessment = Assessment.query.filter_by(id=assessment_id, tenant_id=current_user.tenant_id).first_or_404()
    if request.method == 'POST':
        assessment.name = request.form['name']
        db.session.commit()
        flash('Assessment updated successfully.')
        return redirect(url_for('admin.build_assessment'))
    return render_template('dashboard/edit_assessment.html', assessment=assessment)

@admin_bp.route('/admin/components')
@login_required
@roles_required(['Admin'])
def manage_components():
    from app.models.metadata import ComponentDefinition
    components = ComponentDefinition.query.filter_by(tenant_id=current_user.tenant_id).all()
    return render_template('dashboard/manage_components.html', components=components)

@admin_bp.route('/admin/components/<uuid:component_id>/edit', methods=['GET'])
@login_required
@roles_required(['Admin'])
def edit_component(component_id):
    from app.models.metadata import ComponentDefinition, EntityDefinition
    component = ComponentDefinition.query.filter_by(id=component_id, tenant_id=current_user.tenant_id).first_or_404()
    entities = EntityDefinition.query.filter_by(tenant_id=current_user.tenant_id).all()
    return render_template('dashboard/edit_component.html', component=component, entities=entities)

@admin_bp.route('/admin/users')
@login_required
@roles_required(['Admin'])
def manage_users():
    users = User.query.filter_by(tenant_id=current_user.tenant_id).all()
    
    user_data = []
    csrf_token = generate_csrf()
    for user in users:
        user_data.append({
            'id': str(user.id),
            'email': user.email,
            'role': user.role.name if user.role else 'No Role',
            'actions': f'''
                <div class="flex gap-3 justify-end">
                    <a href="{url_for('admin.edit_user', user_id=user.id)}" title="Edit" class="text-gray-500 hover:text-primary transition">Edit</a>
                    <form action="{url_for('admin.delete_user', user_id=user.id)}" method="POST" onsubmit="return confirm('Delete user?');">
                        <input type="hidden" name="csrf_token" value="{csrf_token}"/>
                        <button type="submit" title="Delete" class="text-gray-500 hover:text-red-600 transition">Delete</button>
                    </form>
                </div>
            '''
        })
    return render_template('dashboard/manage_users.html', users=user_data)

@admin_bp.route('/admin/users/<uuid:user_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required(['Admin'])
def edit_user(user_id):
    user = User.query.filter_by(id=user_id, tenant_id=current_user.tenant_id).first_or_404()
    roles = Role.query.filter_by(tenant_id=current_user.tenant_id).all()
    if request.method == 'POST':
        user.email = request.form['email']
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.role_id = request.form.get('role_id')
        db.session.commit()
        flash('User updated.')
        return redirect(url_for('admin.manage_users'))
    return render_template('dashboard/edit_user.html', user=user, roles=roles)

@admin_bp.route('/admin/users/<uuid:user_id>/delete', methods=['POST'])
@login_required
@roles_required(['Admin'])
def delete_user(user_id):
    user = User.query.filter_by(id=user_id, tenant_id=current_user.tenant_id).first_or_404()
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin.manage_users'))
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/admin/ui-builder/<uuid:page_id>/edit', methods=['GET'])
@login_required
@roles_required(['Admin'])
def edit_ui_builder(page_id):
    from app.models.metadata import PageDefinition
    page = PageDefinition.query.filter_by(id=page_id, tenant_id=current_user.tenant_id).first_or_404()
    return render_template('dashboard/ui_builder_edit.html', page=page)

@admin_bp.route('/admin/ui-builder')
@login_required
@roles_required(['Admin'])
def ui_builder_selector():
    from app.models.metadata import EntityDefinition
    entities = EntityDefinition.query.filter_by(tenant_id=current_user.tenant_id).all()
    return render_template('dashboard/ui_builder_selector.html', entities=entities)
