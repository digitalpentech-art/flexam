from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required
from app.extensions import db
from app.models.assessment import Assessment, AssessmentComponent
from app.core.tenancy import get_current_tenant_id

assessment_bp = Blueprint('assessments', __name__)

@assessment_bp.route('/<uuid:assessment_id>', methods=['GET'])
@login_required
def get_assessment(assessment_id):
    assessment = Assessment.query.filter_by(id=assessment_id, tenant_id=get_current_tenant_id()).first_or_404()
    return render_template('dashboard/assessment_details.html', assessment=assessment)

@assessment_bp.route('/<uuid:assessment_id>/components', methods=['POST'])
@login_required
def add_component(assessment_id):
    assessment = Assessment.query.filter_by(id=assessment_id, tenant_id=get_current_tenant_id()).first_or_404()
    data = request.json
    new_component = AssessmentComponent(
        assessment_id=assessment.id,
        name=data['name'],
        component_type=data['component_type'],
        enforced_question_type=data.get('enforced_question_type'),
        weight=data.get('weight', 1.0)
    )
    db.session.add(new_component)
    db.session.commit()
    return jsonify({"message": "Component added", "id": str(new_component.id)}), 201

@assessment_bp.route('/components/<uuid:component_id>', methods=['PUT', 'DELETE'])
@login_required
def component_operations(component_id):
    component = AssessmentComponent.query.get_or_404(component_id)
    # Verify ownership via assessment
    if component.assessment.tenant_id != get_current_tenant_id():
        return jsonify({"error": "Unauthorized"}), 403
        
    if request.method == 'DELETE':
        db.session.delete(component)
        db.session.commit()
        return jsonify({"message": "Component deleted"}), 200

    # Handle PUT (Update)
    data = request.json
    component.name = data.get('name', component.name)
    component.component_type = data.get('component_type', component.component_type)
    component.weight = data.get('weight', component.weight)
    db.session.commit()
    return jsonify({"message": "Component updated"}), 200

@assessment_bp.route('/', methods=['POST'])
@login_required
def create_assessment():
    data = request.json
    if not data or 'name' not in data:
        return jsonify({"error": "Name is required"}), 400

    tenant_id = get_current_tenant_id()

    try:
        new_assessment = Assessment(
            tenant_id=tenant_id,
            name=data['name']
        )
        db.session.add(new_assessment)

        # Add components
        for comp in data.get('components', []):
            if 'name' not in comp or 'component_type' not in comp:
                db.session.rollback()
                return jsonify({"error": "Component name and type are required"}), 400
                
            new_component = AssessmentComponent(
                assessment=new_assessment,
                name=comp['name'],
                component_type=comp['component_type'],
                enforced_question_type=comp.get('enforced_question_type'),
                weight=comp.get('weight', 1.0),
                configuration=comp.get('configuration', {})
            )
            db.session.add(new_component)

        db.session.commit()
        return jsonify({"message": "Assessment created", "id": str(new_assessment.id)}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
