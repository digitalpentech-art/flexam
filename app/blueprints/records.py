from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.metadata import EntityDefinition, Record
from app.core.tenancy import get_current_tenant_id

records_bp = Blueprint('records', __name__)

@records_bp.route('/<uuid:entity_id>/', methods=['POST'])
def create_record(entity_id):
    data = request.json
    tenant_id = get_current_tenant_id()
    
    # Verify entity exists and belongs to tenant
    entity = EntityDefinition.query.filter_by(id=entity_id, tenant_id=tenant_id).first_or_404()
    
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
    
    # Verify entity exists and belongs to tenant
    entity = EntityDefinition.query.filter_by(id=entity_id, tenant_id=tenant_id).first_or_404()
    
    records = Record.query.filter_by(entity_definition_id=entity.id, tenant_id=tenant_id).all()
    
    return jsonify([{"id": str(r.id), "data": r.data} for r in records]), 200
