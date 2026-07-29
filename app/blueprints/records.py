from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.metadata import EntityDefinition, Record, SequenceState
from app.core.tenancy import get_current_tenant_id

records_bp = Blueprint('records', __name__)

@records_bp.route('/<uuid:entity_id>/', methods=['POST'])
def create_record(entity_id):
    data = request.json
    tenant_id = get_current_tenant_id()
    
    # Verify entity exists and belongs to tenant
    entity = EntityDefinition.query.filter_by(id=entity_id, tenant_id=tenant_id).first_or_404()
    
    # Process fields for autoincrement
    for field in entity.fields:
        if field.field_type == 'autoincrement' and field.name not in data:
            # Get or create sequence state
            seq = SequenceState.query.filter_by(
                tenant_id=tenant_id, 
                entity_definition_id=entity.id
            ).with_for_update().first()
            
            if not seq:
                seq = SequenceState(
                    tenant_id=tenant_id, 
                    entity_definition_id=entity.id, 
                    next_value=1
                )
                db.session.add(seq)
            
            # Assign value and increment
            data[field.name] = seq.next_value
            seq.next_value += 1
    
    new_record = Record(
        tenant_id=tenant_id,
        entity_definition_id=entity.id,
        data=data
    )
    db.session.add(new_record)
    db.session.commit()
    
    return jsonify({"message": "Record created", "id": str(new_record.id)}), 201

@records_bp.route('/<uuid:entity_id>/', methods=['GET'])
def list_records(entity_id):
    tenant_id = get_current_tenant_id()
    records = Record.query.filter_by(entity_definition_id=entity_id, tenant_id=tenant_id).all()
    return jsonify([{"id": str(r.id), "data": r.data} for r in records]), 200

@records_bp.route('/<uuid:entity_id>/<uuid:record_id>/', methods=['GET'])
def get_record(entity_id, record_id):
    tenant_id = get_current_tenant_id()
    record = Record.query.filter_by(id=record_id, entity_definition_id=entity_id, tenant_id=tenant_id).first_or_404()
    return jsonify({"id": str(record.id), "data": record.data}), 200

@records_bp.route('/<uuid:entity_id>/<uuid:record_id>/', methods=['PUT'])
def update_record(entity_id, record_id):
    data = request.json
    tenant_id = get_current_tenant_id()
    record = Record.query.filter_by(id=record_id, entity_definition_id=entity_id, tenant_id=tenant_id).first_or_404()
    
    # Update data
    record.data.update(data)
    # We need to flag JSONB as modified for SQLAlchemy to detect it
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(record, 'data')
    
    db.session.commit()
    return jsonify({"message": "Record updated", "id": str(record.id)}), 200

@records_bp.route('/<uuid:entity_id>/<uuid:record_id>/', methods=['DELETE'])
def delete_record(entity_id, record_id):
    tenant_id = get_current_tenant_id()
    record = Record.query.filter_by(id=record_id, entity_definition_id=entity_id, tenant_id=tenant_id).first_or_404()
    
    db.session.delete(record)
    db.session.commit()
    return jsonify({"message": "Record deleted"}), 200

