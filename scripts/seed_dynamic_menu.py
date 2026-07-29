from app import create_app, db
from app.models.core import Tenant
from app.models.metadata import MenuDefinition, MenuItem

app = create_app('development')
with app.app_context():
    tenant = Tenant.query.first()
    if not tenant:
        print("No tenant found!")
        exit(1)

    # Define Menu
    menu = MenuDefinition(tenant_id=tenant.id, name="Main Sidebar", slug="main-sidebar")
    db.session.add(menu)
    db.session.flush()

    # Define Items
    items = [
        MenuItem(menu_id=menu.id, label="Super Admin", url="/superadmin", required_role="SuperAdmin", order=1),
        MenuItem(menu_id=menu.id, label="Tenant Admin", url="/admin", required_role="Admin", order=2),
        MenuItem(menu_id=menu.id, label="Examiner", url="/examiner", required_role="Examiner", order=3),
        MenuItem(menu_id=menu.id, label="Student", url="/student", required_role="Student", order=4),
    ]
    db.session.add_all(items)
    db.session.commit()
    print(f"Seeded dynamic menu: {menu.slug} with {len(items)} items.")
