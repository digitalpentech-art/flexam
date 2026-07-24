from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.metadata import EntityDefinition, FieldDefinition
from app.core.tenancy import get_current_tenant_id
from app.utils.audit import log_action

metadata_bp = Blueprint('metadata', __name__)

@metadata_bp.route('/entities', methods=['POST'])
def create_entity():
    data = request.json
    tenant_id = get_current_tenant_id()
    
    if not tenant_id:
        return jsonify({"error": "Tenant not identified"}), 400
    
    new_entity = EntityDefinition(
        tenant_id=tenant_id,
        name=data['name'],
        plural_name=data.get('plural_name'),
        description=data.get('description')
    )
    db.session.add(new_entity)
    db.session.commit()
    
    # Log the action
    log_action('create', 'EntityDefinition', new_entity.id, changes={'name': new_entity.name})
    
    return jsonify({"message": "Entity created", "id": str(new_entity.id)}), 201

@metadata_bp.route('/entities/<uuid:entity_id>/fields', methods=['POST'])
def add_field(entity_id):
    data = request.json
    tenant_id = get_current_tenant_id()
    
    # Verify entity belongs to tenant
    entity = EntityDefinition.query.filter_by(id=entity_id, tenant_id=tenant_id).first_or_404()
    
    new_field = FieldDefinition(
        entity_id=entity.id,
        name=data['name'],
        label=data['label'],
        field_type=data['field_type'],
        is_required=data.get('is_required', False)
    )
    db.session.add(new_field)
    db.session.commit()
    
    log_action('create', 'FieldDefinition', new_field.id, changes={'name': new_field.name, 'entity_id': str(entity_id)})
    
    return jsonify({"message": "Field added", "id": str(new_field.id)}), 201

@metadata_bp.route('/schema/save', methods=['POST'])
def save_full_schema():
    data = request.json
    tenant_id = get_current_tenant_id()
    
    new_entity = EntityDefinition(
        tenant_id=tenant_id,
        name=data['name'],
        description=data.get('description')
    )
    db.session.add(new_entity)
    db.session.flush() # Get ID
    
    for field in data.get('fields', []):
        new_field = FieldDefinition(
            entity_id=new_entity.id,
            name=field['name'],
            label=field.get('label', field['name']),
            field_type=field['field_type']
        )
        db.session.add(new_field)
    
    db.session.commit()
    log_action('create_schema', 'EntityDefinition', new_entity.id, changes={'name': new_entity.name})
    
    return jsonify({"message": "Schema saved", "id": str(new_entity.id)}), 201
