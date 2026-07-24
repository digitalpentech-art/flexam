from flask import request, g
from sqlalchemy import event, and_
from sqlalchemy.orm import Session, Query
from app.models.core import Tenant

def get_current_tenant_id():
    """Retrieves the current tenant ID."""
    return getattr(g, 'tenant_id', None)

def set_current_tenant(tenant_id):
    g.tenant_id = tenant_id

# SQLAlchemy events for automatic tenant enforcement
def setup_tenancy_events(db):
    @event.listens_for(Session, "before_flush")
    def before_flush(session, flush_context, instances):
        tenant_id = get_current_tenant_id()
        if not tenant_id:
            return

        for obj in session.new:
            if hasattr(obj, 'tenant_id') and obj.tenant_id is None:
                obj.tenant_id = tenant_id

    @event.listens_for(Query, "before_compile", retval=True)
    def before_compile(query):
        tenant_id = get_current_tenant_id()
        if tenant_id is None:
            return query

        for mapper in query._entities:
            if hasattr(mapper.entity, 'tenant_id'):
                query = query.filter(mapper.entity.tenant_id == tenant_id)
        return query
