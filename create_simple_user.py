from app import create_app, db
from app.models.user import User
import sqlite3

app = create_app()

with app.app_context():
    # 查询现有用户
    existing_users = User.query.all()
    print(f'现有用户: {[(u.id, u.username, u.phone) for u in existing_users]}')
    
    # 直接使用SQL更新admin用户的密码，绕过werkzeug的哈希函数
    conn = sqlite3.connect('instance/green.sqlite')
    cursor = conn.cursor()
    
    # 更新admin用户密码为123456
    cursor.execute("UPDATE users SET password_hash = 'pbkdf2:sha256:1000$vJIZRCNl$5beded01a5e73b421b6ad760fa6a289d8b22d7cd621b33b175a0826f58fe52c8' WHERE username = 'admin'")
    conn.commit()
    
    # 创建一个简单的测试用户
    cursor.execute("""
    INSERT OR IGNORE INTO users (username, email, phone, password_hash, balance)
    VALUES ('simple_user', 'simple@example.com', '13900139000', 'pbkdf2:sha256:1000$vJIZRCNl$5beded01a5e73b421b6ad760fa6a289d8b22d7cd621b33b175a0826f58fe52c8', 10000.0)
    """)
    conn.commit()
    
    # 关闭连接
    conn.close()
    
    print("用户密码已重置/创建完成")
    print("admin 用户密码: 123456")
    print("simple_user 用户密码: 123456")
    print("手机号: 13900139000")
    
    # 验证用户
    admin = User.query.filter_by(username='admin').first()
    simple_user = User.query.filter_by(phone='13900139000').first()
    
    print(f"admin密码验证: {admin.check_password('123456')}")
    print(f"simple_user密码验证: {simple_user.check_password('123456') if simple_user else '用户不存在'}") 