from flask import request, g
from sqlalchemy import event, and_
from sqlalchemy.orm import Session, Query
from app.models.core import Tenant
from flask_login import current_user

def get_current_tenant_id():
    """Retrieves the current tenant ID."""
    return getattr(g, 'tenant_id', None)

def set_current_tenant(tenant_id):
    g.tenant_id = tenant_id

# SQLAlchemy events for automatic tenant enforcement
def setup_tenancy_events(db):
    @event.listens_for(Session, "before_flush")
    def before_flush(session, flush_context, instances):
        # Superadmins bypass automatic tenant assignment
        if current_user and current_user.is_authenticated and current_user.is_superadmin:
            return

        tenant_id = get_current_tenant_id()
        if not tenant_id:
            return

        for obj in session.new:
            if hasattr(obj, 'tenant_id') and obj.tenant_id is None:
                obj.tenant_id = tenant_id

    @event.listens_for(Query, "before_compile", retval=True)
    def before_compile(query):
        # Superadmins bypass tenant filtering
        if current_user and current_user.is_authenticated and current_user.is_superadmin:
            return query

        tenant_id = get_current_tenant_id()
        if tenant_id is None:
            return query

        for description in query.column_descriptions:
            entity = description['type']
            if entity and hasattr(entity, 'tenant_id'):
                # Directly set assertions to False to allow adding filters after limit/offset
                query._enable_assertions = False
                query = query.filter(entity.tenant_id == tenant_id)
        return query
