import os
from werkzeug.utils import secure_filename
from flask import current_app

# STORAGE_TYPE: 'local' or 's3'
def get_storage_engine():
    return os.environ.get('STORAGE_TYPE', 'local')

def save_file(file, tenant_id, subfolder=''):
    engine = get_storage_engine()
    
    if engine == 's3':
        # Placeholder for S3 integration using boto3
        # return upload_to_s3(file, tenant_id, subfolder)
        raise NotImplementedError("S3 storage not yet implemented")
    
    # Local Storage Implementation
    base_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    tenant_dir = os.path.join(base_dir, str(tenant_id), subfolder)
    
    if not os.path.exists(tenant_dir):
        os.makedirs(tenant_dir)
        
    filename = secure_filename(file.filename)
    save_path = os.path.join(tenant_dir, filename)
    file.save(save_path)
    
    return save_path
