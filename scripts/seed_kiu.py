import uuid
from app import create_app, db
from app.models.core import Tenant, User, Role
from app.models.metadata import EntityDefinition, FieldDefinition
from app.models.assessment import Assessment, AssessmentComponent
from app.models.examination import Examination
from app.models.question import Question, QuestionOption
from datetime import datetime, timedelta

def seed_kiu():
    app = create_app('development')
    with app.app_context():
        # Clear existing to avoid duplicate issues on re-run
        db.drop_all()
        db.create_all()

        # 1. Create Tenant (KIU)
        tenant = Tenant(name='Kashim Ibrahim University', slug='kiu', allow_self_registration=True)
        db.session.add(tenant)
        db.session.flush()

        # 2. Roles
        roles = {
            'Admin': Role(name='Admin', tenant_id=tenant.id, permissions={'all': True}),
            'Examiner': Role(name='Examiner', tenant_id=tenant.id, permissions={'manage_exams': True}),
            'Student': Role(name='Student', tenant_id=tenant.id, permissions={'take_exams': True})
        }
        db.session.add_all(roles.values())
        db.session.flush()

        # 3. Users
        users = [
            {'email': 'admin@kiu.edu.ng', 'role': roles['Admin'], 'first': 'Admin', 'last': 'User'},
            {'email': 'examiner@kiu.edu.ng', 'role': roles['Examiner'], 'first': 'Exam', 'last': 'User'},
            {'email': 'student@kiu.edu.ng', 'role': roles['Student'], 'first': 'Stud', 'last': 'User'}
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
        db.session.flush()

        # 4. Entities
        entities = [
            {'name': 'Department', 'fields': [{'name': 'name', 'label': 'Department Name', 'field_type': 'string'}]},
            {'name': 'Course', 'fields': [{'name': 'title', 'label': 'Course Title', 'field_type': 'string'}, {'name': 'code', 'label': 'Course Code', 'field_type': 'string'}]}
        ]
        for ent_data in entities:
            entity = EntityDefinition(tenant_id=tenant.id, name=ent_data['name'])
            db.session.add(entity)
            db.session.flush()
            for f_data in ent_data['fields']:
                field = FieldDefinition(entity_id=entity.id, **f_data)
                db.session.add(field)

        # 5. Assessments & Components
        flex_assess = Assessment(name='Introduction to Computer Science (CBT)', tenant_id=tenant.id)
        db.session.add(flex_assess)
        db.session.flush()
        flex_comp = AssessmentComponent(
            assessment_id=flex_assess.id, 
            name='Part A: MCQ', 
            component_type='objective_cbt',
            enforced_question_type='mcq',
            configuration={'randomize': True}
        )
        db.session.add(flex_comp)
        db.session.flush()

        # Add questions
        q1 = Question(
            tenant_id=tenant.id, 
            component_id=flex_comp.id, 
            question_type='mcq', 
            content={'text': 'What is the capital of Nigeria?'}, 
            marks=1
        )
        db.session.add(q1)
        db.session.flush()
        
        opt1 = QuestionOption(question_id=q1.id, content='Abuja', is_correct=True)
        opt2 = QuestionOption(question_id=q1.id, content='Lagos', is_correct=False)
        db.session.add_all([opt1, opt2])

        # Non-flexible
        non_flex_assess = Assessment(name='Advanced Mathematics (Theory)', tenant_id=tenant.id)
        db.session.add(non_flex_assess)
        db.session.flush()
        non_flex_comp = AssessmentComponent(
            assessment_id=non_flex_assess.id, 
            name='Section A: Structured', 
            component_type='theory'
        )
        db.session.add(non_flex_comp)
        
        # 6. Examinations
        exam1 = Examination(name='CS101 Mid-term', assessment_id=flex_assess.id, tenant_id=tenant.id, start_time=datetime.utcnow(), end_time=datetime.utcnow() + timedelta(minutes=60), duration_minutes=60)
        exam2 = Examination(name='MTH202 Final Exam', assessment_id=non_flex_assess.id, tenant_id=tenant.id, start_time=datetime.utcnow(), end_time=datetime.utcnow() + timedelta(minutes=120), duration_minutes=120)
        db.session.add_all([exam1, exam2])

        db.session.commit()
        print("Kashim Ibrahim University seeded successfully.")

if __name__ == '__main__':
    seed_kiu()
