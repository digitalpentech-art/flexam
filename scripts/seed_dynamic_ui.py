from app import create_app, db
from app.models.core import Tenant
from app.models.metadata import PageDefinition, ComponentDefinition, LayoutDefinition

app = create_app('development')
with app.app_context():
    tenant = Tenant.query.first()
    if not tenant:
        print("No tenant found!")
        exit(1)

    page = PageDefinition(tenant_id=tenant.id, name="Test Pilot Page", slug="test-pilot")
    db.session.add(page)
    db.session.flush()

    component = ComponentDefinition(tenant_id=tenant.id, name="Test Table", component_type="table", configuration={"items": []})
    db.session.add(component)
    db.session.flush()

    layout = LayoutDefinition(tenant_id=tenant.id, page_id=page.id, component_id=component.id, position={'x': 0, 'y': 0, 'w': 12, 'h': 1})
    db.session.add(layout)
    db.session.commit()
    print(f"Seeded dynamic UI: Page ID {page.id}, Component ID {component.id}")
