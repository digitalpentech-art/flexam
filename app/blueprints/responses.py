from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.response import Response
from app.models.examination import ExamAttempt
from flask_login import login_required, current_user

responses_bp = Blueprint('responses', __name__)

@responses_bp.route('/', methods=['POST'])
@login_required
def submit_response():
    # Detect if request is JSON or multipart (for file uploads)
    if request.is_json:
        data = request.json
    else:
        # Handle file upload response
        data = request.form.to_dict()
        data['content'] = {'file_path': request.form.get('file_path')}

    attempt = ExamAttempt.query.get_or_404(data['attempt_id'])
    
    # Security: Verify attempt belongs to current user
    if attempt.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
        
    new_response = Response(
        attempt_id=attempt.id,
        component_id=data['component_id'],
        question_id=data.get('question_id'),
        response_mode=data['response_mode'],
        content=data['content']
    )
    db.session.add(new_response)
    db.session.commit()
    
    return jsonify({"message": "Response saved", "id": str(new_response.id)}), 201
