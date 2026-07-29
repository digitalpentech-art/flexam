from celery import shared_task
from app.extensions import db
from app.models.notification import Notification
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
    
    # Send Notification
    send_notification.delay(result.user_id, result.tenant_id, "Your exam result is ready!")
    
    return f"Result {result_id} processed"

@shared_task
def send_notification(user_id, tenant_id, message):
    new_notif = Notification(
        user_id=user_id,
        tenant_id=tenant_id,
        message=message
    )
    db.session.add(new_notif)
    db.session.commit()
    return f"Notification sent to {user_id}"
