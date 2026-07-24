from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.assessment import Assessment, AssessmentComponent
from app.core.tenancy import get_current_tenant_id

assessment_bp = Blueprint('assessments', __name__)

@assessment_bp.route('/', methods=['POST'])
def create_assessment():
    data = request.json
    tenant_id = get_current_tenant_id()
    
    new_assessment = Assessment(
        tenant_id=tenant_id,
        name=data['name']
    )
    db.session.add(new_assessment)
    
    # Add components
    for comp in data.get('components', []):
        new_component = AssessmentComponent(
            assessment=new_assessment,
            name=comp['name'],
            component_type=comp['component_type'],
            weight=comp.get('weight', 1.0),
            configuration=comp.get('configuration', {})
        )
        db.session.add(new_component)
        
    db.session.commit()
    
    return jsonify({"message": "Assessment created", "id": str(new_assessment.id)}), 201
