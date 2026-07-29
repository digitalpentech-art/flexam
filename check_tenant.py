from app import create_app, db
from app.models.core import Tenant, User
from app.models.metadata import EntityDefinition

app = create_app('development')
with app.app_context():
    tenant_id = '1de8bca3-a1d2-4e17-b321-bf42702fa29c'
    t = Tenant.query.get(tenant_id)
    if t:
        print(f"Tenant: {t.name} ({t.slug})")
        entities = EntityDefinition.query.filter_by(tenant_id=t.id).all()
        print(f"Entities: {[e.name for e in entities]}")
    else:
        print("Tenant not found")
