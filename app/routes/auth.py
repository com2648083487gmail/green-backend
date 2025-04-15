from flask import Blueprint, request, jsonify
from app.models.user import User
from app import db
from datetime import datetime, timedelta, timezone

bp = Blueprint('auth', __name__, url_prefix='/api')

@bp.route('/user/login', methods=['POST', 'OPTIONS'])
def login():
    """用户登录"""
    try:
        # 处理OPTIONS请求
        if request.method == 'OPTIONS':
            return '', 200
            
        if not request.is_json:
            print("请求不是JSON格式")
            return jsonify({"code": 400, "msg": "请求必须是JSON格式"}), 400
        
        # 获取请求数据
        data = request.get_json()
        print(f"原始登录请求数据: {data}")  # 打印原始请求数据
        
        # 获取登录凭据，支持手机号或邮箱
        phone = data.get('phone', '')
        email = data.get('email', '')
        password = data.get('password', '')
        
        print(f"处理后的凭据 - 手机号: '{phone}', 邮箱: '{email}', 密码: '{password}'")
        
        # 检查必要参数
        if not password:
            print("密码为空")
            return jsonify({"code": 400, "msg": "密码不能为空"}), 400
        
        if not phone and not email:
            print("手机号和邮箱都为空")
            return jsonify({"code": 400, "msg": "请提供手机号或邮箱"}), 400
        
        # 根据提供的凭据查询用户
        user = None
        if phone:
            print(f"通过手机号查询用户: {phone}")
            user = User.query.filter_by(phone=phone).first()
            if user:
                print(f"查找到用户: ID={user.id}, 用户名={user.username}")
            else:
                print(f"未找到手机号为 {phone} 的用户")
        elif email:
            print(f"通过邮箱查询用户: {email}")
            user = User.query.filter_by(email=email).first()
            if user:
                print(f"查找到用户: ID={user.id}, 用户名={user.username}")
            else:
                print(f"未找到邮箱为 {email} 的用户")
        
        # 如果找不到用户，立即返回错误
        if not user:
            print("未找到匹配的用户")
            return jsonify({"code": 401, "msg": "用户不存在"}), 401
        
        # 验证密码
        try:
            password_hash = user.password_hash
            print(f"数据库中的密码哈希: {password_hash}")
            password_valid = user.check_password(password)
            print(f"密码验证结果: {password_valid}")
        except Exception as e:
            print(f"密码验证出错: {str(e)}")
            return jsonify({"code": 500, "msg": f"密码验证错误: {str(e)}"}), 500
        
        # 验证用户存在并且密码正确
        if password_valid:
            # 返回用户信息
            user_info = {
                "user_id": user.id,
                "nickname": user.username,
                "avatar": "/static/images/users/user2.png",
                "phone": user.phone,
                "balance": user.balance  # 使用数据库中的余额
            }
            
            # 创建包含用户ID的token
            token = f"{user.id}:{datetime.now().timestamp()}"
            
            print(f"登录成功 - 用户: {user.username}, UserID: {user.id}")
            
            return jsonify({
                "code": 200,
                "msg": "登录成功",
                "data": {
                    "user_id": user.id,
                    "user_info": user_info,
                    "token": token  # 使用包含用户ID的token
                }
            })
        else:
            print(f"密码验证失败 - 用户: {user.username}")
            return jsonify({"code": 401, "msg": "密码错误"}), 401
    except Exception as e:
        print(f"登录过程中发生错误: {str(e)}")
        return jsonify({"code": 500, "msg": f"服务器内部错误: {str(e)}"}), 500

@bp.route('/user/register', methods=['POST', 'OPTIONS'])
def register():
    """用户注册"""
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        return '', 200
        
    if not request.is_json:
        return jsonify({"code": 400, "msg": "请求必须是JSON格式"}), 400
    
    data = request.get_json()
    phone = data.get('phone', '')
    password = data.get('password', '')
    # 优先使用用户提供的用户名，如果没有提供则使用默认格式
    username = data.get('username', '')
    nickname = data.get('nickname', '')
    
    # 如果用户提供了nickname或username，优先使用这些值
    if nickname:
        # 如果提供了nickname，优先使用nickname
        user_display_name = nickname
    elif username:
        # 如果没有nickname但有username，使用username
        user_display_name = username
    else:
        # 如果都没有提供，则使用默认格式
        user_display_name = f'用户{phone[-4:]}'
    
    email = data.get('email', f'user_{phone}@example.com')  # 简化处理，实际应要求提供邮箱
    
    # 检查必要字段
    if not phone or not password:
        return jsonify({"code": 400, "msg": "手机号和密码不能为空"}), 400
    
    # 检查手机号是否已被注册
    if User.query.filter_by(phone=phone).first():
        return jsonify({"code": 400, "msg": "该手机号已被注册"}), 400
    
    # 检查用户名是否已被注册
    if User.query.filter_by(username=user_display_name).first():
        user_display_name = f'{user_display_name}_{datetime.now().strftime("%H%M%S")}'
    
    # 创建新用户
    try:
        new_user = User(username=user_display_name, phone=phone, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            "code": 200,
            "msg": "注册成功",
            "data": {
                "user_id": new_user.id
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": f"注册失败: {str(e)}"}), 500

@bp.route('/user/info', methods=['GET', 'OPTIONS'])
def get_user_info():
    """获取当前登录用户信息"""
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        return '', 200
        
    # 从请求头获取Token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"code": 401, "msg": "未授权，请先登录"}), 401
    
    token = auth_header.split(' ')[1]
    
    # 从token中获取用户ID
    # 在实际系统中应该解析JWT token，这里为了简化，可以从请求参数中获取
    user_id = request.args.get('user_id')
    
    # 如果参数中没有user_id，则尝试从token中提取
    if not user_id:
        try:
            # 假设token格式为 "user_id:时间戳"
            if ':' in token:
                user_id = token.split(':')[0]
            else:
                # 尝试检查token是否可以直接作为用户ID使用
                potential_user_id = int(token)
                # 查询用户是否存在
                if User.query.get(potential_user_id):
                    user_id = potential_user_id
                else:
                    return jsonify({"code": 401, "msg": "无效的用户身份，请重新登录"}), 401
        except:
            # 如果解析失败，返回错误，不再使用默认ID
            return jsonify({"code": 401, "msg": "无法识别用户身份，请重新登录"}), 401
    
    # 从数据库获取用户信息
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"code": 404, "msg": "用户不存在"}), 404
    
    user_info = {
        "user_id": user.id,
        "nickname": user.username,
        "avatar": "/static/images/users/user1.png",
        "phone": user.phone,
        "email": user.email,
        "balance": user.balance,  # 使用数据库中的余额
        "create_time": user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else "2023-01-01 00:00:00"
    }
    
    return jsonify({"code": 200, "msg": "成功", "data": user_info})

@bp.route('/admin/login', methods=['POST', 'OPTIONS'])
def admin_login():
    """管理员登录"""
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        return '', 200
        
    if not request.is_json:
        return jsonify({"code": 400, "msg": "请求必须是JSON格式"}), 400
    
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    
    print(f"管理员登录请求: username={username}, password={password}")
    
    # 采用最简单的硬编码方式：只要用户名是admin且密码是123456即可登录
    if username == 'admin' and password == '123456':
        print(f"管理员登录成功: {username}")
        # 返回管理员信息
        user_info = {
            "id": 1,
            "username": "admin",
            "name": "系统管理员",
            "avatar": "/static/images/users/user3.png",
            "role": "admin"
        }
        
        # 创建包含用户ID的token
        token = f"1:{datetime.now().timestamp()}"
        
        return jsonify({
            "code": 200,
            "msg": "登录成功",
            "data": {
                "user": user_info,
                "token": token
            }
        })
    
    print(f"管理员登录失败: username={username}, 用户名或密码不正确")
    return jsonify({"code": 401, "msg": "用户名或密码错误"}), 401

@bp.route('/users', methods=['GET'])
def get_users():
    """获取用户列表 - 管理员功能"""
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 获取筛选参数
    username = request.args.get('username')
    email = request.args.get('email')
    
    # 构建查询
    query = User.query
    
    # 应用筛选条件
    if username:
        query = query.filter(User.username.like(f'%{username}%'))
    if email:
        query = query.filter(User.email.like(f'%{email}%'))
    
    # 执行分页查询
    pagination = query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page)
    users = pagination.items
    
    # 转换为字典列表
    user_list = []
    for user in users:
        user_dict = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'created_at': user.created_at.strftime('%Y-%m-%dT%H:%M:%S') if user.created_at else None
        }
        user_list.append(user_dict)
    
    return jsonify({
        "items": user_list,
        "total": pagination.total
    })

@bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """管理员删除用户 - 管理员功能"""
    try:
        print(f"尝试删除用户ID: {user_id}")
        
        # 验证请求头中的token，验证管理员权限
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            print("未提供Authorization头或格式不正确")
            return jsonify({"code": 401, "msg": "未授权，请先登录"}), 401
        
        # 简化实现：假设管理员的用户名是"admin"
        # 在实际应用中，应该通过token验证并检查用户角色
        
        if user_id == 1:
            print("尝试删除管理员账户")
            return jsonify({"code": 403, "msg": "不能删除管理员账户"}), 403
        
        # 获取要删除的用户
        user = User.query.get(user_id)
        if not user:
            print(f"用户ID {user_id} 不存在")
            return jsonify({"code": 404, "msg": "用户不存在"}), 404
        
        print(f"找到用户: {user.username}, 尝试删除")
        
        try:
            # 级联删除用户的所有关联数据
            from app.models.order import Order, OrderItem
            
            # 1. 删除用户的订单项和订单
            orders = Order.query.filter_by(user_id=user_id).all()
            if orders:
                print(f"删除用户 {user.username} 的 {len(orders)} 个订单")
                for order in orders:
                    # 删除订单项
                    order_items = OrderItem.query.filter_by(order_id=order.id).all()
                    if order_items:
                        print(f"删除订单 {order.id} 的 {len(order_items)} 个订单项")
                        for item in order_items:
                            db.session.delete(item)
                    
                    # 删除订单
                    db.session.delete(order)
            
            # 2. 删除用户的地址
            if hasattr(user, 'addresses') and user.addresses:
                print(f"删除用户 {user.username} 的 {len(user.addresses)} 个地址记录")
                for address in user.addresses:
                    db.session.delete(address)
            
            # 3. 最后删除用户
            print(f"正在删除用户 {user.username}")
            db.session.delete(user)
            db.session.commit()
            print(f"成功删除用户 {user.username} 及其所有关联数据")
            return jsonify({"code": 200, "msg": "用户及其所有关联数据删除成功"})
        except Exception as e:
            db.session.rollback()
            error_msg = str(e)
            print(f"删除用户时出现数据库错误: {error_msg}")
            return jsonify({"code": 500, "msg": f"删除失败: {error_msg}"}), 500
    except Exception as e:
        error_msg = str(e)
        print(f"删除用户过程中出现未处理的异常: {error_msg}")
        return jsonify({"code": 500, "msg": f"服务器内部错误: {error_msg}"}), 500 