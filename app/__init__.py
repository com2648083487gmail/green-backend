from flask import Flask, send_from_directory, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

# 初始化数据库
db = SQLAlchemy()

def create_app(test_config=None):
    # 创建并配置app
    app = Flask(__name__, instance_relative_config=True)

    # 添加CORS支持
    CORS(app, resources={r"/*": {"origins": "*"}})

    # 默认配置
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'green.sqlite'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 最大上传文件大小为16MB
        JWT_TOKEN_LOCATION=["headers"],  # 添加JWT配置
        JWT_HEADER_NAME="Authorization",  # JWT头部名称
        JWT_HEADER_TYPE="Bearer",  # JWT头部类型
        SEND_FILE_MAX_AGE_DEFAULT=0,  # 禁用静态文件缓存
        SEND_FILE_DEFAULT_MIMETYPE='image/jpeg'  # 设置默认MIME类型
    )

    if test_config is None:
        # 加载实例配置（如果存在）
        app.config.from_pyfile('config.py', silent=True)
    else:
        # 加载测试配置
        app.config.from_mapping(test_config)

    # 确保实例文件夹存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 确保静态资源和上传目录存在
    uploads_dir = os.path.join(app.static_folder, 'uploads')
    images_dir = os.path.join(app.static_folder, 'images')
    product_images_dir = os.path.join(images_dir, 'product')
    category_images_dir = os.path.join(images_dir, 'category')

    for directory in [uploads_dir, images_dir, product_images_dir, category_images_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)

    # 初始化扩展
    db.init_app(app)

    # 配置CORS - 允许前端跨域请求
    CORS(app, 
         resources={r"/*": {
             "origins": ["http://localhost:8080", "http://localhost:5100"],
             "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "expose_headers": "*",
             "supports_credentials": True,
             "max_age": 600
         }}, 
         automatic_options=True)

    # 添加预检请求处理
    @app.after_request
    def after_request(response):
        # 处理预检请求
        if request.method == 'OPTIONS':
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
            response.status_code = 200
        return response

    # 注册蓝图（改为从 app.routes.__init__ 中引入）
    from app.routes import all_blueprints
    for bp in all_blueprints:
        app.register_blueprint(bp)

    # 添加静态资源路由
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        response = send_from_directory(uploads_dir, filename)
        response.headers['Content-Type'] = 'image/jpeg'  # 设置正确的内容类型
        return response

    @app.route('/static/images/product/<path:filename>')
    def product_images(filename):
        response = send_from_directory(product_images_dir, filename)
        response.headers['Content-Type'] = 'image/jpeg'
        return response

    @app.route('/static/images/category/<path:filename>')
    def category_images(filename):
        response = send_from_directory(category_images_dir, filename)
        response.headers['Content-Type'] = 'image/jpeg'
        return response

    @app.route('/static/images/<path:filename>')
    def static_images(filename):
        response = send_from_directory(images_dir, filename)
        response.headers['Content-Type'] = 'image/jpeg'
        return response

    @app.route('/static/images/icons/<path:filename>')
    def icon_files(filename):
        icons_dir = os.path.join(images_dir, 'icons')
        if not os.path.exists(icons_dir):
            os.makedirs(icons_dir)
        response = send_from_directory(icons_dir, filename)
        if filename.endswith('.png'):
            response.headers['Content-Type'] = 'image/png'
        elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
            response.headers['Content-Type'] = 'image/jpeg'
        elif filename.endswith('.svg'):
            response.headers['Content-Type'] = 'image/svg+xml'
        return response

    @app.route('/instance/<path:filename>')
    def instance_file(filename):
        response = send_from_directory(app.instance_path, filename)
        return response
    
    @app.route('/user/<path:path>')
    def serve_user_app(path):
        dist_dir = os.path.join(app.static_folder, 'user', 'dist')
        return send_from_directory(dist_dir, path)

    @app.route('/user/')
    @app.route('/user')
    def serve_user_index():
        dist_dir = os.path.join(app.static_folder, 'user', 'dist')
        return send_from_directory(dist_dir, 'index.html')
    
    @app.route('/admin/<path:path>')
    def serve_admin_app(path):
        dist_dir = os.path.join(app.static_folder, 'admin', 'dist')
        return send_from_directory(dist_dir, path)

    @app.route('/admin/')
    @app.route('/admin')
    def serve_admin_index():
        dist_dir = os.path.join(app.static_folder, 'admin', 'dist')
        return send_from_directory(dist_dir, 'index.html')

    return app

