from flask import Blueprint, request, jsonify, current_app
import os
import uuid
from werkzeug.utils import secure_filename
import time

bp = Blueprint('upload', __name__, url_prefix='/api/upload')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/image', methods=['POST'])
def upload_image():
    # 检查是否有文件
    if 'file' not in request.files:
        return jsonify({'code': 400, 'msg': '没有文件被上传'}), 400
    
    file = request.files['file']
    
    # 检查文件名是否为空
    if file.filename == '':
        return jsonify({'code': 400, 'msg': '未选择文件'}), 400
    
    if file and allowed_file(file.filename):
        # 安全处理文件名
        filename = secure_filename(file.filename)
        # 添加时间戳和UUID避免文件名冲突
        filename = f"{int(time.time())}_{uuid.uuid4().hex}_{filename}"
        
        # 获取上传目录
        uploads_dir = os.path.join(current_app.static_folder, 'uploads')
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
        
        # 保存文件
        file_path = os.path.join(uploads_dir, filename)
        file.save(file_path)
        
        # 构建URL路径
        url = f"/uploads/{filename}"
        
        return jsonify({
            'code': 200,
            'msg': '上传成功',
            'url': url,
            'data': {
                'url': url
            }
        })
    
    return jsonify({'code': 400, 'msg': '不支持的文件类型'}), 400 