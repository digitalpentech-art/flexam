from app import create_app, db
from app.models.core import Tenant
from app.models.metadata import EntityDefinition, FieldDefinition

app = create_app('development')
with app.app_context():
    tenant = Tenant.query.first()
    if not tenant:
        print("No tenant found!")
        exit(1)

    # 1. Define 'User Profile' Entity
    entity = EntityDefinition.query.filter_by(tenant_id=tenant.id, name="User Profile").first()
    if not entity:
        entity = EntityDefinition(tenant_id=tenant.id, name="User Profile", plural_name="User Profiles")
        db.session.add(entity)
        db.session.flush()

    # 2. Define Profile Fields
    fields = [
        {"name": "first_name", "label": "First Name", "field_type": "text"},
        {"name": "last_name", "label": "Last Name", "field_type": "text"},
        {"name": "bio", "label": "Biography", "field_type": "text"}
    ]
    
    for field_data in fields:
        field = FieldDefinition.query.filter_by(entity_id=entity.id, name=field_data["name"]).first()
        if not field:
            field = FieldDefinition(
                entity_id=entity.id,
                name=field_data["name"],
                label=field_data["label"],
                field_type=field_data["field_type"]
            )
            db.session.add(field)
    
    db.session.commit()
    print(f"Seeded 'User Profile' entity with ID: {entity.id}")
