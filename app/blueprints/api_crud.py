from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.core.crud_service import CrudService

api_crud_bp = Blueprint('api_crud', __name__)

@api_crud_bp.route('/api/crud/<entity_slug>/<action>', methods=['GET', 'POST'])
@login_required
def handle_crud(entity_slug, action):
    entity = CrudService.get_entity_by_slug(entity_slug)
    
    if action == 'create' and request.method == 'POST':
        data = request.json
        record = CrudService.create_record(entity.id, data)
        return jsonify({"message": "Record created", "id": record.id}), 201
    
    elif action == 'read':
        # Extract filters from query parameters or request body if provided
        filters = request.json.get('filters') if request.is_json else None
        records = CrudService.read_records(entity.id, filters=filters)
        return jsonify([{"id": r.id, "data": r.data} for r in records])
    
    elif action == 'update' and request.method == 'POST':
        record_id = request.json.get('id')
        data = request.json.get('data')
        CrudService.update_record(record_id, data)
        return jsonify({"message": "Record updated"})
        
    elif action == 'delete' and request.method == 'POST':
        record_id = request.json.get('id')
        CrudService.delete_record(record_id)
        return jsonify({"message": "Record deleted"})
    
    return jsonify({"error": "Invalid action or method"}), 400
