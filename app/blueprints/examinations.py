from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
from app.extensions import db
from app.models.examination import Examination, ExamAttempt, IntegrityLog
from app.models.assessment import Assessment, AssessmentComponent
from app.models.question import Question
from app.models.response import Response
from app.core.tenancy import get_current_tenant_id
from flask_login import login_required, current_user

examinations_bp = Blueprint('examinations', __name__)

@examinations_bp.route('/<uuid:attempt_id>/integrity', methods=['POST'])
@login_required
def log_integrity(attempt_id):
    data = request.json
    attempt = ExamAttempt.query.get_or_404(attempt_id)
    
    if attempt.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
        
    log = IntegrityLog(
        attempt_id=attempt.id,
        event_type=data['event_type']
    )
    db.session.add(log)
    db.session.commit()
    return jsonify({"message": "Integrity event logged"}), 201

@examinations_bp.route('/<uuid:attempt_id>/take', methods=['GET'])
@login_required
def take_exam(attempt_id):
    # Verify attempt ownership in a real scenario
    return render_template('dashboard/take.html', attempt_id=str(attempt_id))

@examinations_bp.route('/', methods=['POST'])
@login_required
def create_examination():
    data = request.json
    tenant_id = get_current_tenant_id()
    
    # Simple validation
    new_exam = Examination(
        tenant_id=tenant_id,
        assessment_id=data['assessment_id'],
        name=data['name'],
        start_time=datetime.fromisoformat(data['start_time']),
        end_time=datetime.fromisoformat(data['end_time']),
        duration_minutes=data['duration_minutes']
    )
    db.session.add(new_exam)
    db.session.commit()
    
    return jsonify({"message": "Examination created", "id": str(new_exam.id)}), 201

@examinations_bp.route('/<uuid:attempt_id>/content', methods=['GET'])
@login_required
def get_exam_content(attempt_id):
    attempt = ExamAttempt.query.get_or_404(attempt_id)
    if attempt.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    
    exam = attempt.examination
    assessment = exam.assessment
    
    # Build a structured response
    content = {
        "exam_name": exam.name,
        "duration_minutes": exam.duration_minutes,
        "components": []
    }
    
    for comp in assessment.components:
        comp_data = {
            "id": str(comp.id),
            "name": comp.name,
            "type": comp.component_type,
            "questions": []
        }
        for q in comp.questions:
            comp_data["questions"].append({
                "id": str(q.id),
                "type": q.question_type,
                "content": q.content,
                "marks": q.marks,
                "options": [{"id": str(o.id), "content": o.content} for o in q.options]
            })
        content["components"].append(comp_data)
        
    return jsonify(content), 200

@examinations_bp.route('/<uuid:exam_id>/attempt', methods=['POST'])
@login_required
def start_attempt(exam_id):
    tenant_id = get_current_tenant_id()
    
    # Verify exam exists and belongs to tenant
    exam = Examination.query.filter_by(id=exam_id, tenant_id=tenant_id).first_or_404()
    
    # Server-side validation: Check if exam is active
    now = datetime.utcnow()
    if now < exam.start_time or now > exam.end_time:
        return jsonify({"error": "Examination is not active"}), 400
    
    # Check if attempt already exists
    attempt = ExamAttempt.query.filter_by(examination_id=exam.id, user_id=current_user.id).first()
    if attempt:
        return jsonify({"message": "Attempt already exists", "id": str(attempt.id)}), 200
        
    new_attempt = ExamAttempt(
        examination_id=exam.id,
        user_id=current_user.id,
        status='in_progress'
    )
    db.session.add(new_attempt)
    db.session.commit()
    
    return jsonify({"message": "Attempt started", "id": str(new_attempt.id)}), 201
