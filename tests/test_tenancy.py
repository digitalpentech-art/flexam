import pytest
from app import db
from app.models.core import Tenant, User
from app.core.tenancy import set_current_tenant
from flask import g

def test_tenant_isolation(app):
    with app.app_context():
        # Create two tenants
        t1 = Tenant(name='Tenant 1', slug='t1')
        t2 = Tenant(name='Tenant 2', slug='t2')
        db.session.add_all([t1, t2])
        db.session.commit()
        
        # Create user in tenant 1
        u1 = User(tenant_id=t1.id, email='u1@t1.com', password_hash='hash')
        # Create user in tenant 2
        u2 = User(tenant_id=t2.id, email='u2@t2.com', password_hash='hash')
        db.session.add_all([u1, u2])
        db.session.commit()
        
        # Test isolation
        set_current_tenant(t1.id)
        users_t1 = User.query.all()
        assert len(users_t1) == 1
        assert users_t1[0].email == 'u1@t1.com'
        
        set_current_tenant(t2.id)
        users_t2 = User.query.all()
        assert len(users_t2) == 1
        assert users_t2[0].email == 'u2@t2.com'
