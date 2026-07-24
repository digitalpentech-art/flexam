from app.models.results import Result
from app.models.examination import ExamAttempt
from sqlalchemy import func
from app.extensions import db

def get_performance_metrics(tenant_id):
    # Example: Average score for the tenant
    avg_score = db.session.query(func.avg(Result.total_score)).filter(Result.tenant_id == tenant_id).scalar()
    
    # Count of assessments
    total_attempts = ExamAttempt.query.join(Result).filter(Result.tenant_id == tenant_id).count()
    
    return {
        "average_score": round(avg_score or 0, 2),
        "total_attempts": total_attempts
    }
