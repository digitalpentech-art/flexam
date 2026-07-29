import os
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.attachment import Attachment
from app.core.tenancy import get_current_tenant_id

uploads_bp = Blueprint('uploads', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'docx'}

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
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Store in a secure uploads directory defined in config
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, str(uuid.uuid4()) + '_' + filename)
        file.save(filepath)
        
        new_attachment = Attachment(
            tenant_id=get_current_tenant_id(),
            filename=filename,
            filepath=filepath,
            mime_type=file.mimetype,
            owner_id=request.form['owner_id'],
            owner_type=request.form['owner_type']
        )
        db.session.add(new_attachment)
        db.session.commit()
        
        return jsonify({"message": "File uploaded", "id": str(new_attachment.id)}), 201
        
    return jsonify({"error": "File type not allowed"}), 400
