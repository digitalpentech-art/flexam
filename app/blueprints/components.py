from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.extensions import db
from app.models.metadata import ComponentDefinition
from app.utils.auth import roles_required

components_bp = Blueprint('components', __name__)

@components_bp.route('/api/entities/<uuid:entity_id>/fields', methods=['GET'])
@login_required
@roles_required(['Admin'])
def get_entity_fields(entity_id):
    from app.models.metadata import FieldDefinition
    fields = FieldDefinition.query.filter_by(entity_id=entity_id).all()
    return jsonify([{"id": str(f.id), "label": f.label} for f in fields]), 200

@components_bp.route('/registry', methods=['GET'])
@login_required
@roles_required(['Admin'])
def get_component_registry():
    from app.models.registry import ComponentRegistry
    components = ComponentRegistry.query.all()
    return jsonify([{
        "id": str(c.id),
        "component_type": c.component_type,
        "property_schema": c.property_schema,
        "ui_metadata": c.ui_metadata
    } for c in components]), 200

@components_bp.route('/<uuid:component_id>/config', methods=['PUT'])
@login_required
@roles_required(['Admin'])
def update_component_config(component_id):
    component = ComponentDefinition.query.get_or_404(component_id)
    data = request.json
    
    if not data:
        return jsonify({"error": "No configuration data provided"}), 400
        
    # Update the configuration dictionary
    if 'configuration' in data:
        component.configuration = data['configuration']
        
    # Update entity-aware fields
    if 'entity_id' in data:
        component.entity_id = data['entity_id']
        
    if 'field_ids' in data:
        component.field_ids = data['field_ids']
        
    db.session.commit()
    
    return jsonify({"message": "Configuration updated successfully"}), 200

@components_bp.route('/api/layouts/<uuid:layout_id>/position', methods=['PUT'])
@login_required
@roles_required(['Admin'])
def update_layout_position(layout_id):
    from app.models.metadata import LayoutDefinition
    layout = LayoutDefinition.query.get_or_404(layout_id)
    data = request.json
    
    if not data or not all(k in data for k in ['x', 'y', 'w', 'h']):
        return jsonify({"error": "Missing positioning data (x, y, w, h)"}), 400
        
    layout.position = {'x': data['x'], 'y': data['y'], 'w': data['w'], 'h': data['h']}
    db.session.commit()
    
    return jsonify({"message": "Position updated successfully"}), 200
