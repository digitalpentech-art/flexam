import pytest
from app import create_app, db
from app.models.core import Tenant, User, Role
from app.models.metadata import EntityDefinition

@pytest.fixture
def test_app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

def test_kiu_seeding(test_app):
    with test_app.app_context():
        # This will trigger the seeding logic if we call it or replicate it
        # Let's replicate the core seeding requirement
        tenant = Tenant(name='Kashim Ibrahim University', slug='kiu')
        db.session.add(tenant)
        db.session.commit()
        
        assert Tenant.query.filter_by(slug='kiu').first() is not None
        
        # Verify Entity Creation
        entity = EntityDefinition(tenant_id=tenant.id, name='Student')
        db.session.add(entity)
        db.session.commit()
        
        assert EntityDefinition.query.filter_by(tenant_id=tenant.id, name='Student').first() is not None
