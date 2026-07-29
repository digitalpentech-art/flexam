from app import create_app, db
from app.models.core import Tenant, User, Role
from werkzeug.security import generate_password_hash

app = create_app('default')

def seed_data():
    with app.app_context():
        # Removed db.drop_all() and db.create_all() to preserve production data
        
        # Ensure Tenant exists
        tenant = Tenant.query.filter_by(slug='test-uni').first()
        if not tenant:
            tenant = Tenant(name='Test University', slug='test-uni', allow_self_registration=True)
            db.session.add(tenant)
            db.session.commit()
            print("Tenant 'Test University' created.")
        else:
            print("Tenant 'Test University' already exists.")

        # Create/Ensure Roles
        roles_data = {
            'Admin': {'all': True},
            'Examiner': {'manage_exams': True},
            'Student': {'take_exams': True}
        }
        
        created_roles = {}
        for role_name, perms in roles_data.items():
            role = Role.query.filter_by(name=role_name, tenant_id=tenant.id).first()
            if not role:
                role = Role(name=role_name, tenant_id=tenant.id, permissions=perms)
                db.session.add(role)
                db.session.commit()
                print(f"Role '{role_name}' created.")
            else:
                print(f"Role '{role_name}' already exists.")
            created_roles[role_name] = role

        # Create/Ensure Users
        users = [
            {'email': 'admin@test.com', 'role': created_roles['Admin'], 'first': 'Admin', 'last': 'User'},
            {'email': 'examiner@test.com', 'role': created_roles['Examiner'], 'first': 'Exam', 'last': 'User'},
            {'email': 'student@test.com', 'role': created_roles['Student'], 'first': 'Stud', 'last': 'User'}
        ]

        for u_data in users:
            user = User.query.filter_by(email=u_data['email'], tenant_id=tenant.id).first()
            if not user:
                user = User(
                    email=u_data['email'],
                    tenant_id=tenant.id,
                    role_id=u_data['role'].id,
                    first_name=u_data['first'],
                    last_name=u_data['last'],
                    password='password123'
                )
                db.session.add(user)
                print(f"User '{u_data['email']}' created.")
            else:
                print(f"User '{u_data['email']}' already exists.")

        db.session.commit()
        print("Database seeding completed safely.")

if __name__ == '__main__':
    seed_data()
