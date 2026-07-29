from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

def roles_required(role_names):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role.name not in role_names:
                flash("You do not have permission to access this page.")
                return redirect(url_for('public.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def permissions_required(permission_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if current_user.is_superadmin:
                return f(*args, **kwargs)
            
            # Check permissions map in the role
            role = current_user.role
            if role and role.permissions and role.permissions.get(permission_name):
                return f(*args, **kwargs)
            
            flash("You do not have the required permission.")
            return redirect(url_for('public.index'))
        return decorated_function
    return decorator
