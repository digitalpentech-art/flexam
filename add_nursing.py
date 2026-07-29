from app import create_app, db
from app.models.metadata import EntityDefinition

app = create_app('development')
with app.app_context():
    tenant_id = '1de8bca3-a1d2-4e17-b321-bf42702fa29c'
    entity = EntityDefinition(tenant_id=tenant_id, name='Nursing')
    db.session.add(entity)
    db.session.commit()
    print("Added 'Nursing' entity.")
