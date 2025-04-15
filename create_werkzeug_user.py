from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash

app = create_app()

with app.app_context():
    # 简单的测试密码，与前端测试数据一致
    test_password = '123456'
    
    # 查询现有用户
    existing_users = User.query.all()
    for user in existing_users:
        print(f"ID: {user.id}, 用户名: {user.username}, 手机: {user.phone}")
    
    # 查询是否已存在werkzeug_user2
    existing_user = User.query.filter_by(phone='13911111112').first()
    if existing_user:
        print(f"用户已存在: {existing_user.username}, ID: {existing_user.id}")
        # 更新密码
        existing_user.set_password(test_password)
        db.session.commit()
        print(f"已更新用户密码")
    else:
        # 创建新用户
        new_user = User(
            username='werkzeug_user2',
            email='werkzeug2@example.com',
            phone='13911111112',
            balance=10000.0
        )
        new_user.set_password(test_password)
        db.session.add(new_user)
        db.session.commit()
        print(f"新用户已创建，ID: {new_user.id}, 用户名: {new_user.username}")
    
    # 验证密码
    user = User.query.filter_by(phone='13911111112').first()
    password_valid = user.check_password(test_password)
    print(f"密码验证结果: {password_valid}")
    
    # 列出所有用户
    print("\n所有用户列表:")
    all_users = User.query.all()
    for user in all_users:
        print(f"ID: {user.id}, 用户名: {user.username}, 手机: {user.phone}")
        
    # 检查是否有手机号为空的用户
    empty_phone_users = User.query.filter(User.phone.is_(None)).all()
    if empty_phone_users:
        print("\n警告: 发现手机号为空的用户:")
        for user in empty_phone_users:
            print(f"ID: {user.id}, 用户名: {user.username}")
            
    print("\n使用以下凭据登录:")
    print(f"手机号: 13911111112")
    print(f"密码: {test_password}")