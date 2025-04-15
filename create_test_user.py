from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # 创建一个测试用户
    test_user = User(
        username='test_user', 
        phone='13800138000', 
        email='test@example.com',
        password_hash=generate_password_hash('123456')
    )
    
    # 查询现有用户
    existing_users = User.query.all()
    print(f'现有用户: {[(u.id, u.username, u.phone) for u in existing_users]}')
    
    # 检查用户是否已存在
    if not User.query.filter_by(phone='13800138000').first():
        db.session.add(test_user)
        db.session.commit()
        print('测试用户创建成功')
    else:
        print('测试用户已存在')
    
    # 验证用户密码
    user = User.query.filter_by(phone='13800138000').first()
    if user:
        print(f'用户ID: {user.id}, 用户名: {user.username}')
        print(f'密码验证结果: {user.check_password("123456")}') 