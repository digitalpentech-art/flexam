from flask import Blueprint, request, jsonify
from app.utils.storage import save_file
from app.core.tenancy import get_current_tenant_id
from flask_login import login_required

uploads_bp = Blueprint('uploads', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@uploads_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400
        
    tenant_id = get_current_tenant_id()
    file_path = save_file(file, tenant_id, subfolder='scripts')
    
    return jsonify({"message": "File uploaded", "path": file_path}), 201
