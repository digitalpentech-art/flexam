from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.models.core import Tenant, User, AuditLog
from app.extensions import db
from app.utils.superadmin import superadmin_required
from urllib.parse import urlparse
import subprocess
import os
import tempfile
from flask import send_file, Response

superadmin_bp = Blueprint('superadmin', __name__)

@superadmin_bp.route('/superadmin')
@login_required
@superadmin_required
def dashboard():
    tenant_count = Tenant.query.count()
    user_count = User.query.count()
    recent_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(5).all()
    return render_template('superadmin/index.html', 
                           tenant_count=tenant_count, 
                           user_count=user_count,
                           recent_logs=recent_logs)

@superadmin_bp.route('/superadmin/tenants')
@login_required
@superadmin_required
def list_tenants():
    tenants = Tenant.query.all()
    return render_template('superadmin/tenants.html', tenants=tenants)

@superadmin_bp.route('/superadmin/tenants/create', methods=['GET', 'POST'])
@login_required
@superadmin_required
def create_tenant():
    if request.method == 'POST':
        # Create Tenant
        tenant = Tenant(name=request.form['name'], slug=request.form['slug'])
        db.session.add(tenant)
        db.session.flush() # Get tenant ID

        # Create Admin User
        from app.models.core import User, Role
        from app.core.provisioner import SchemaProvisioner
        import json
        
        # Ensure 'Admin' role exists
        admin_role = Role.query.filter_by(tenant_id=tenant.id, name='Admin').first()
        if not admin_role:
            admin_role = Role(name='Admin', tenant_id=tenant.id, permissions={})
            db.session.add(admin_role)
            db.session.flush()

        admin_user = User(
            email=request.form['admin_email'],
            tenant_id=tenant.id,
            role_id=admin_role.id
        )
        admin_user.password = request.form['admin_password']
        db.session.add(admin_user)
        
        # Provision custom schema if provided
        schema_config = request.form.get('schema_config')
        if schema_config:
            try:
                config = json.loads(schema_config)
                SchemaProvisioner.provision(tenant.id, config)
            except Exception as e:
                db.session.rollback()
                flash(f'Tenant created, but schema provisioning failed: {e}', 'error')
                return redirect(url_for('superadmin.list_tenants'))
        
        db.session.commit()
        flash(f'Tenant {tenant.name} and admin {admin_user.email} created successfully', 'success')
        return redirect(url_for('superadmin.list_tenants'))
    return render_template('superadmin/create_tenant.html')

@superadmin_bp.route('/superadmin/tenants/<uuid:tenant_id>/edit', methods=['GET', 'POST'])
@login_required
@superadmin_required
def edit_tenant(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)
    if request.method == 'POST':
        tenant.name = request.form['name']
        tenant.slug = request.form['slug']
        tenant.is_active = 'is_active' in request.form
        db.session.commit()
        flash('Tenant updated', 'success')
        return redirect(url_for('superadmin.list_tenants'))
    return render_template('superadmin/edit_tenant.html', tenant=tenant)

@superadmin_bp.route('/superadmin/tenants/<uuid:tenant_id>/delete', methods=['POST'])
@login_required
@superadmin_required
def delete_tenant(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)
    db.session.delete(tenant)
    db.session.commit()
    flash('Tenant deleted', 'success')
    return redirect(url_for('superadmin.list_tenants'))

@superadmin_bp.route('/superadmin/users')
@login_required
@superadmin_required
def list_users():
    users = User.query.all()
    return render_template('superadmin/users.html', users=users)

@superadmin_bp.route('/superadmin/users/<uuid:user_id>/edit', methods=['GET', 'POST'])
@login_required
@superadmin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.email = request.form['email']
        user.is_superadmin = 'is_superadmin' in request.form
        db.session.commit()
        flash('User updated', 'success')
        return redirect(url_for('superadmin.list_users'))
    return render_template('superadmin/edit_user.html', user=user)

@superadmin_bp.route('/superadmin/users/<uuid:user_id>/delete', methods=['POST'])
@login_required
@superadmin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('superadmin.list_users'))
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('superadmin.list_users'))

@superadmin_bp.route('/superadmin/audit-logs')
@login_required
@superadmin_required
def list_audit_logs():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
    return render_template('superadmin/audit_logs.html', logs=logs)

@superadmin_bp.route('/superadmin/backup')
@login_required
@superadmin_required
def backup_database():
    # Use a secure temporary file
    fd, backup_file_path = tempfile.mkstemp(suffix='.sql')
    os.close(fd)
    
    try:
        db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
        
        # Parse URI: postgresql://username:password@host:port/database
        dialect_prefix = "postgresql"
        if "://" in db_uri:
            dialect_prefix = db_uri.split("://")[0]
            
        parsed = urlparse(db_uri.replace(dialect_prefix + '://', 'http://'))
        
        db_user = parsed.username
        db_password = parsed.password
        db_host = parsed.hostname
        db_port = parsed.port or 5432
        db_name = parsed.path.lstrip('/')
        
        env = os.environ.copy()
        if db_password:
            env['PGPASSWORD'] = db_password
            
        cmd = ['pg_dump']
        if db_host:
            cmd.extend(['-h', db_host])
        if db_port:
            cmd.extend(['-p', str(db_port)])
        if db_user:
            cmd.extend(['-U', db_user])
        cmd.extend(['-F', 'p', '-f', backup_file_path, db_name])
        
        subprocess.run(cmd, env=env, check=True)
        return send_file(backup_file_path, as_attachment=True, download_name='backup.sql')
    except Exception as e:
        flash(f'Backup failed: {e}', 'error')
        return redirect(url_for('superadmin.dashboard'))
    finally:
        if os.path.exists(backup_file_path):
            os.remove(backup_file_path)
