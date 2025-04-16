from .auth import bp as auth_bp
from .products import bp as products_bp
from .orders import bp as orders_bp
from .user import bp as user_bp
from .notices import bp as notices_bp
from .brand import bp as brand_bp
from .dashboard import bp as dashboard_bp
from .upload import bp as upload_bp
from .cart import bp as cart_bp
from .frontend import frontend_bp
from .admin import admin_bp

# 集中导出所有蓝图
all_blueprints = [
    auth_bp,
    products_bp,
    orders_bp,
    user_bp,
    notices_bp,
    brand_bp,
    dashboard_bp,
    upload_bp,
    cart_bp,
    frontend_bp,
    admin_bp
]
