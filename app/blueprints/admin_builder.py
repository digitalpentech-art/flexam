from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models.metadata import RelationshipDefinition, EntityDefinition
from app.models.security import SecurityPolicy
from app.models.core import Role
from app.core.tenancy import get_current_tenant_id
from app.utils.auth import roles_required

admin_builder_bp = Blueprint('admin_builder', __name__)

@admin_builder_bp.route('/admin/relationships', methods=['GET', 'POST'])
@login_required
@roles_required(['Admin'])
def manage_relationships():
    tenant_id = get_current_tenant_id()
    if request.method == 'POST':
        rel = RelationshipDefinition(
            tenant_id=tenant_id,
            name=request.form['name'],
            source_entity_id=request.form['source_entity_id'],
            target_entity_id=request.form['target_entity_id'],
            relationship_type=request.form['relationship_type']
        )
        db.session.add(rel)
        db.session.commit()
        flash('Relationship defined.')
        return redirect(url_for('admin_builder.manage_relationships'))
    
    entities = EntityDefinition.query.filter_by(tenant_id=tenant_id).all()
    relationships = RelationshipDefinition.query.filter_by(tenant_id=tenant_id).all()
    return render_template('dashboard/manage_relationships.html', entities=entities, relationships=relationships)

@admin_builder_bp.route('/admin/security', methods=['GET', 'POST'])
@login_required
@roles_required(['Admin'])
def manage_security():
    tenant_id = get_current_tenant_id()
    if request.method == 'POST':
        print(f"DEBUG: Form data: {request.form}")
        policy = SecurityPolicy(
            tenant_id=tenant_id,
            entity_definition_id=request.form['entity_definition_id'],
            role_id=request.form['role_id'],
            action=request.form['action'],
            filter_rules=[{'db_column': request.form['db_column'], 'operator': '==', 'user_attribute_key': request.form['user_attribute_key']}]
        )
        db.session.add(policy)
        db.session.commit()
        print(f"DEBUG: Policy committed: {policy}")
        flash('Security policy defined.')
        return redirect(url_for('admin_builder.manage_security'))
    
    entities = EntityDefinition.query.filter_by(tenant_id=tenant_id).all()
    roles = Role.query.filter_by(tenant_id=tenant_id).all()
    policies = SecurityPolicy.query.filter_by(tenant_id=tenant_id).all()
    return render_template('dashboard/manage_security.html', entities=entities, roles=roles, policies=policies)
