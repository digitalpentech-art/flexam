from app import create_app, db
from app.models.core import Tenant, User, Role
from app.models.assessment import Assessment, AssessmentComponent
from app.models.question import Question, QuestionOption
from app.core.types import FieldType

app = create_app('default')

with app.app_context():
    print("Clearing database...")
    db.drop_all()
    db.create_all()

    # 1. Create Super Admin
    # Note: Tenant is required, will create a "System" tenant for global superadmin
    system_tenant = Tenant(name="System", slug="system", allow_self_registration=False)
    db.session.add(system_tenant)
    db.session.commit()

    superadmin = User(email="super@flexam.com", tenant_id=system_tenant.id, is_superadmin=True)
    superadmin.password = "password"
    db.session.add(superadmin)

    # 2. Seed Universities (Tenants)
    universities = [
        {"name": "University of Maiduguri", "slug": "unimaid"},
        {"name": "Kashim Ibrahim University", "slug": "kiu"}
    ]

    for uni in universities:
        print(f"Seeding {uni['name']}...")
        tenant = Tenant(name=uni['name'], slug=uni['slug'], allow_self_registration=True)
        db.session.add(tenant)
        db.session.commit()

        # Create Roles
        roles = ['Admin', 'Examiner', 'Student']
        role_map = {}
        for r_name in roles:
            role = Role(name=r_name, tenant_id=tenant.id, permissions={})
            db.session.add(role)
            db.session.flush()
            role_map[r_name] = role.id

        # Create Users
        users = [
            {"email": f"admin@{uni['slug']}.com", "role": "Admin"},
            {"email": f"examiner@{uni['slug']}.com", "role": "Examiner"},
            {"email": f"student@{uni['slug']}.com", "role": "Student"},
        ]
        
        for u in users:
            user = User(email=u['email'], tenant_id=tenant.id, role_id=role_map[u['role']])
            user.password = "password"
            db.session.add(user)

        # Create Assessment
        assessment = Assessment(name=f"Standard Exam - {uni['name']}", tenant_id=tenant.id)
        db.session.add(assessment)
        db.session.flush()

        component = AssessmentComponent(assessment_id=assessment.id, name="General Knowledge", component_type="mcq", weight=1.0)
        db.session.add(component)
        db.session.flush()

        # Create 5 Questions
        for i in range(1, 6):
            q = Question(tenant_id=tenant.id, content={"text": f"Question {i} for {uni['name']}"}, question_type="mcq", marks=10)
            component.questions.append(q)
            # Add options
            for j in range(1, 5):
                opt = QuestionOption(content=f"Option {j}")
                q.options.append(opt)

    db.session.commit()
    print("Seeding complete.")
