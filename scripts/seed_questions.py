from app import create_app, db
from app.models.core import Tenant
from app.models.question import Question, QuestionOption
from app.core.tenancy import set_current_tenant

def seed_questions():
    app = create_app('development')
    with app.app_context():
        tenant = Tenant.query.filter_by(slug='kiu').first()
        set_current_tenant(tenant.id)

        # Mappings of component IDs
        first_sem_comps = [
            'b9f8b844-7e9b-4e7e-b215-197a41363b81', 'fb62081a-a983-42c0-808e-b461ff3d3c4f',
            '8bfa2b81-31d6-481a-aa61-14e863f6bd85', '8901e14c-1806-4e47-aa55-60163efebb60',
            '5b6c1a4e-977e-4b58-a203-6e9d780025f1', 'ddafbcd5-f604-4fd5-a3d2-442d4fd36e3e',
            '8d9c8a5b-f628-4ecf-9bc9-20ba19d8d097'
        ]
        
        # Add MCQs for first semester
        for comp_id in first_sem_comps:
            for i in range(1, 4):
                q = Question(
                    tenant_id=tenant.id,
                    component_id=comp_id,
                    question_type='mcq',
                    content={'text': f'Compiler Construction 1 Question {i} for Section {comp_id[-4:]}'},
                    marks=2
                )
                db.session.add(q)
                db.session.flush()
                db.session.add_all([
                    QuestionOption(question_id=q.id, content='Option A', is_correct=True),
                    QuestionOption(question_id=q.id, content='Option B', is_correct=False)
                ])

        # Second semester
        comp_essay = 'a33cf5e3-462a-4399-bdfe-2e2796340b86'
        comp_obj_mca = ['e0b035eb-e39c-4d0c-83d8-c7f03c8f7f19', '4f6a1835-f5da-4a12-9002-89b34896f08c', '0621a81c-ea79-4997-9fa4-0ffb98c48d2f']
        comp_mca = ['4edc6803-bc80-443e-8591-c89e7d07c74a', 'bf9f27b6-ea2d-4dae-ac78-780aac104973', '25792493-ceed-4248-a322-c7bc9d079baf']

        # Essay
        q = Question(tenant_id=tenant.id, component_id=comp_essay, question_type='essay', content={'text': 'Explain the phases of a compiler.'}, marks=10)
        db.session.add(q)

        # Objective / MCQ
        for comp_id in comp_obj_mca + comp_mca:
            q = Question(
                tenant_id=tenant.id,
                component_id=comp_id,
                question_type='mcq',
                content={'text': f'Compiler Construction 2 Objective Question for {comp_id[-4:]}'},
                marks=1
            )
            db.session.add(q)
            db.session.flush()
            db.session.add_all([
                QuestionOption(question_id=q.id, content='True', is_correct=True),
                QuestionOption(question_id=q.id, content='False', is_correct=False)
            ])

        db.session.commit()
        print("Questions seeded successfully.")

if __name__ == '__main__':
    seed_questions()
