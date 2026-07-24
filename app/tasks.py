from celery import shared_task
from app.extensions import db
from app.models.results import Result
from app.utils.grading import compute_grade

@shared_task
def process_marking_task(result_id):
    result = Result.query.get(result_id)
    if not result:
        return
    
    # Simulate complex logic...
    result.final_grade = compute_grade(result.tenant_id, result.total_score)
    db.session.commit()
    return f"Result {result_id} processed"
