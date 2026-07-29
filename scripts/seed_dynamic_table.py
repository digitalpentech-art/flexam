from app import create_app, db
from app.models.core import Tenant
from app.models.metadata import PageDefinition, ComponentDefinition, LayoutDefinition
import uuid

app = create_app('development')
with app.app_context():
    tenant = Tenant.query.first()
    if not tenant:
        print("No tenant found!")
        exit(1)

    # 1. Define the Page
    page = PageDefinition(tenant_id=tenant.id, name="Test Dynamic Table Page", slug="test-dynamic-table")
    db.session.add(page)
    db.session.flush()

    # 2. Define the Component with Table Config
    config = {
        "columns": [
            {"key": "email", "label": "Email"},
            {"key": "role", "label": "Role"}
        ],
        "actions": [
            {
                "label": "Edit",
                "url_template": "/admin/users/{{ id }}/edit",
                "css_class": "text-blue-500 hover:underline"
            },
            {
                "label": "Delete",
                "url_template": "/admin/users/{{ id }}/delete",
                "css_class": "text-red-500 hover:underline"
            }
        ],
        "data": [
            {"id": str(uuid.uuid4()), "email": "test@example.com", "role": "Admin"},
            {"id": str(uuid.uuid4()), "email": "user@example.com", "role": "Student"}
        ]
    }
    component = ComponentDefinition(tenant_id=tenant.id, name="User Management Table", component_type="table", configuration=config)
    db.session.add(component)
    db.session.flush()

    # 3. Create Layout
    layout = LayoutDefinition(tenant_id=tenant.id, page_id=page.id, component_id=component.id, position={'x': 0, 'y': 0, 'w': 12, 'h': 1})
    db.session.add(layout)
    db.session.commit()
    print(f"Seeded dynamic table: Page Slug: {page.slug}, Component ID: {component.id}")
