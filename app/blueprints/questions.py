from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.question import Question, QuestionOption
from app.core.tenancy import get_current_tenant_id

question_bp = Blueprint('questions', __name__)

@question_bp.route('/', methods=['POST'])
def create_question():
    data = request.json
    tenant_id = get_current_tenant_id()
    
    new_question = Question(
        tenant_id=tenant_id,
        question_type=data['question_type'],
        content=data['content'],
        marks=data.get('marks', 1)
    )
    db.session.add(new_question)
    
    # Add options if provided
    for opt in data.get('options', []):
        new_option = QuestionOption(
            question=new_question,
            content=opt['content'],
            is_correct=opt.get('is_correct', False)
        )
        db.session.add(new_option)
        
    db.session.commit()
    
    return jsonify({"message": "Question created", "id": str(new_question.id)}), 201
