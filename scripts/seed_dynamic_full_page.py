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

    # Define the Page
    page = PageDefinition.query.filter_by(tenant_id=tenant.id, slug="full-dynamic").first()
    if not page:
        page = PageDefinition(tenant_id=tenant.id, name="Full Dynamic Page", slug="full-dynamic")
        db.session.add(page)
        db.session.flush()

    # Table Component
    table_comp = ComponentDefinition.query.filter_by(tenant_id=tenant.id, name="Users Table").first()
    if not table_comp:
        table_config = {
            "columns": [{"key": "email", "label": "Email"}],
            "data": [{"id": "uuid-1", "email": "test@example.com"}]
        }
        table_comp = ComponentDefinition(tenant_id=tenant.id, name="Users Table", component_type="table", configuration=table_config)
        db.session.add(table_comp)
        db.session.flush()
    
    # Form Component
    form_comp = ComponentDefinition.query.filter_by(tenant_id=tenant.id, name="User Form").first()
    if not form_comp:
        form_config = {
            "submit_url": "/test-submit",
            "fields": [
                {"name": "username", "label": "Username", "field_type": "text", "is_required": True}
            ]
        }
        form_comp = ComponentDefinition(tenant_id=tenant.id, name="User Form", component_type="form", configuration=form_config)
        db.session.add(form_comp)
        db.session.flush()

    # Layouts
    layout1 = LayoutDefinition(tenant_id=tenant.id, page_id=page.id, component_id=table_comp.id, position={'x': 0, 'y': 0, 'w': 12, 'h': 1})
    layout2 = LayoutDefinition(tenant_id=tenant.id, page_id=page.id, component_id=form_comp.id, position={'x': 0, 'y': 1, 'w': 12, 'h': 1})
    db.session.add_all([layout1, layout2])
    db.session.commit()
    print(f"Seeded full dynamic page: {page.slug}. Layouts count: {page.layouts.count()}")
