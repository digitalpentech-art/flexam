from app import create_app, db
from app.models.core import Tenant, User, Role
from app.models.assessment import Assessment, AssessmentComponent
from app.core.tenancy import set_current_tenant
from datetime import datetime

def seed_semester_assessments():
    app = create_app('development')
    with app.app_context():
        tenant = Tenant.query.filter_by(slug='kiu').first()
        if not tenant:
            print("KIU tenant not found. Please run seed_kiu first.")
            return

        set_current_tenant(tenant.id)

        # 1. First Semester Assessment (7 sections)
        first_sem = Assessment(name='First Semester Examination', tenant_id=tenant.id)
        db.session.add(first_sem)
        db.session.flush()

        for i in range(1, 8):
            comp = AssessmentComponent(
                assessment_id=first_sem.id,
                name=f'Section {i}',
                component_type='objective_cbt', # flexible mixed type
                configuration={'randomize': True}
            )
            db.session.add(comp)

        # 2. Second Semester Assessment (7 sections)
        second_sem = Assessment(name='Second Semester Examination', tenant_id=tenant.id)
        db.session.add(second_sem)
        db.session.flush()

        # Section 1: Compulsory Essay
        db.session.add(AssessmentComponent(
            assessment_id=second_sem.id,
            name='Section 1: Compulsory Essay',
            component_type='theory',
            enforced_question_type='essay'
        ))
        
        # Sections 2-4: Objective
        for i in range(2, 5):
            db.session.add(AssessmentComponent(
                assessment_id=second_sem.id,
                name=f'Section {i}: Objective',
                component_type='objective_cbt',
                enforced_question_type='mcq'
            ))
            
        # Sections 5-7: Multiple Choice
        for i in range(5, 8):
            db.session.add(AssessmentComponent(
                assessment_id=second_sem.id,
                name=f'Section {i}: Multiple Choice',
                component_type='objective_cbt',
                enforced_question_type='mcq'
            ))

        db.session.commit()
        print("Semester assessments seeded successfully.")

if __name__ == '__main__':
    seed_semester_assessments()
