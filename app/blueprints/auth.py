from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.core import User, Tenant
from app import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'], defaults={'tenant_slug': None})
@auth.route('/login/<tenant_slug>', methods=['GET', 'POST'])
def login(tenant_slug):
    tenant = Tenant.query.filter_by(slug=tenant_slug).first() if tenant_slug else None
    
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and user.verify_password(password):
            login_user(user)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            # Role/Status-based redirection
            if user.is_superadmin:
                return redirect(url_for('superadmin.dashboard'))
            elif user.role and user.role.name == 'Admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role and user.role.name == 'Examiner':
                return redirect(url_for('examiner.dashboard'))
            elif user.role and user.role.name == 'Student':
                return redirect(url_for('student.dashboard'))
            else:
                return redirect(url_for('public.index'))
        else:
            flash('Invalid email or password.')
            
    return render_template('auth/login.html', tenant=tenant)

@auth.route('/register/<tenant_slug>', methods=['GET', 'POST'])
def register(tenant_slug):
    tenant = Tenant.query.filter_by(slug=tenant_slug).first_or_404()
    
    if not tenant.allow_self_registration:
        flash("Self-registration is not allowed for this organization.")
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user already exists in this tenant
        if User.query.filter_by(email=email, tenant_id=tenant.id).first():
            flash("User already exists.")
            return redirect(url_for('auth.register', tenant_slug=tenant_slug))
            
        new_user = User(email=email, tenant_id=tenant.id)
        new_user.password = password
        db.session.add(new_user)
        db.session.commit()
        
        flash("Registration successful. Please login.")
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', tenant=tenant)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
