from flask import request, g
from app.extensions import db
from app.models.core import AuditLog
from app.core.tenancy import get_current_tenant_id
from flask_login import current_user

def log_action(action, entity_type, entity_id, changes=None):
    """
    Utility to record an audit log entry for sensitive actions.
    """
    tenant_id = get_current_tenant_id()
    user_id = current_user.id if current_user.is_authenticated else None
    remote_addr = request.remote_addr
    
    log_entry = AuditLog(
        tenant_id=tenant_id,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        changes=changes,
        remote_addr=remote_addr
    )
    db.session.add(log_entry)
    db.session.commit()
