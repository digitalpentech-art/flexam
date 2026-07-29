from app import create_app, db
from app.models.core import Tenant, User, Role
from werkzeug.security import generate_password_hash

app = create_app('default')

def seed_data():
    with app.app_context():
        # Clear existing data (optional, for testing purposes)
        db.drop_all()
        db.create_all()

        # Create Tenant
        tenant = Tenant(name='Test University', slug='test-uni', allow_self_registration=True)
        db.session.add(tenant)
        db.session.commit()

        # Create Roles
        admin_role = Role(name='Admin', tenant_id=tenant.id, permissions={'all': True})
        examiner_role = Role(name='Examiner', tenant_id=tenant.id, permissions={'manage_exams': True})
        student_role = Role(name='Student', tenant_id=tenant.id, permissions={'take_exams': True})
        db.session.add_all([admin_role, examiner_role, student_role])
        db.session.commit()

        # Create Users
        users = [
            {'email': 'admin@test.com', 'role': admin_role, 'first': 'Admin', 'last': 'User'},
            {'email': 'examiner@test.com', 'role': examiner_role, 'first': 'Exam', 'last': 'User'},
            {'email': 'student@test.com', 'role': student_role, 'first': 'Stud', 'last': 'User'}
        ]

        for u_data in users:
            user = User(
                email=u_data['email'],
                tenant_id=tenant.id,
                role_id=u_data['role'].id,
                first_name=u_data['first'],
                last_name=u_data['last'],
                password='password123'
            )
            db.session.add(user)

        db.session.commit()
        print("Database seeded successfully.")

if __name__ == '__main__':
    seed_data()
