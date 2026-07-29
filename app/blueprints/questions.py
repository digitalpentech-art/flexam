from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.question import Question, QuestionOption
from app.core.tenancy import get_current_tenant_id

question_bp = Blueprint('questions', __name__)

from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.question import Question, QuestionOption
from app.core.tenancy import get_current_tenant_id
from flask_login import login_required

question_bp = Blueprint('questions', __name__)

@question_bp.route('/', methods=['POST'])
@login_required
def create_question():
    data = request.json
    tenant_id = get_current_tenant_id()
    
    new_question = Question(
        tenant_id=tenant_id,
        component_id=data.get('component_id'),
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

@question_bp.route('/<uuid:question_id>', methods=['PUT', 'DELETE'])
@login_required
def question_operations(question_id):
    question = Question.query.get_or_404(question_id)
    if question.tenant_id != get_current_tenant_id():
        return jsonify({"error": "Unauthorized"}), 403

    if request.method == 'DELETE':
        db.session.delete(question)
        db.session.commit()
        return jsonify({"message": "Question deleted"}), 200

    # Handle PUT (Update)
    data = request.json
    question.content = data.get('content', question.content)
    question.marks = data.get('marks', question.marks)
    
    # Simple option update: replace all
    if 'options' in data:
        QuestionOption.query.filter_by(question_id=question.id).delete()
        for opt in data['options']:
            db.session.add(QuestionOption(
                question_id=question.id,
                content=opt['content'],
                is_correct=opt.get('is_correct', False)
            ))
            
    db.session.commit()
    return jsonify({"message": "Question updated"}), 200
