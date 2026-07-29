from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.extensions import db
from app.models.metadata import EntityDefinition, FieldDefinition
from app.core.tenancy import get_current_tenant_id
from app.utils.audit import log_action
from app.core.schema_manager import SchemaManager
from app.core.types import FieldType

metadata_bp = Blueprint('metadata', __name__)
# ...
@metadata_bp.route('/entities/<uuid:entity_id>/layout', methods=['POST'])
@login_required
def save_layout(entity_id):
    data = request.json
    tenant_id = get_current_tenant_id()
    
    # Verify entity belongs to tenant
    entity = EntityDefinition.query.filter_by(id=entity_id, tenant_id=tenant_id).first_or_404()
    
    # Sync full schema based on the UI payload (layout_config + fields)
    SchemaManager.sync_schema(entity.id, data)
    
    return jsonify({"message": "Schema synchronized"}), 200

@metadata_bp.route('/fields/<uuid:field_id>', methods=['PUT', 'DELETE'])
def field_operations(field_id):
    field = FieldDefinition.query.get_or_404(field_id)
    
    if request.method == 'DELETE':
        db.session.delete(field)
        db.session.commit()
        log_action('delete', 'FieldDefinition', field.id, changes={'name': field.name})
        return jsonify({"message": "Field deleted"}), 200

    # Handle PUT (Update)
    data = request.json
    
    # Store old type for migration check
    old_type = field.field_type
    
    # Update field
    field.label = data.get('label', field.label)
    new_type = data.get('field_type', field.field_type)
    if new_type not in FieldType.list():
        return jsonify({"error": f"Invalid field type. Must be one of: {', '.join(FieldType.list())}"}), 400
    field.field_type = new_type
    field.ui_config = data.get('ui_config', field.ui_config)
    field.position = data.get('position', field.position)
    field.is_required = data.get('is_required', field.is_required)
    field.is_unique = data.get('is_unique', field.is_unique)
    field.default_value = data.get('default_value', field.default_value)
    
    # Migrate data if type changed
    if old_type != field.field_type:
        SchemaManager.migrate_field_type(field.entity_id, field.name, old_type, field.field_type)
        
    db.session.commit()
    log_action('update', 'FieldDefinition', field.id, changes={'name': field.name})
    return jsonify({"message": "Field updated"}), 200

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
    
    if data['field_type'] not in FieldType.list():
        return jsonify({"error": f"Invalid field type. Must be one of: {', '.join(FieldType.list())}"}), 400
    
    new_field = FieldDefinition(
        entity_id=entity.id,
        name=data['name'],
        label=data['label'],
        field_type=data['field_type'],
        is_required=data.get('is_required', False),
        is_unique=data.get('is_unique', False),
        default_value=data.get('default_value'),
        validation_rules=data.get('validation_rules'),
        choices=data.get('choices'),
        related_entity_id=data.get('related_entity_id'),
        ui_config=data.get('ui_config', {}),
        position=data.get('position', 0)
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
