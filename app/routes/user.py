from flask import Blueprint, request, jsonify, current_app
from flask import Blueprint, request, jsonify
from app.models.user import User, Address
from app.models.order import Order
from app import db

bp = Blueprint('user', __name__, url_prefix='/api/user')

@bp.route('/profile', methods=['GET'])
def get_profile():
    # 从请求头获取Token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"code": 401, "msg": "未授权，请先登录"}), 401
    
    token = auth_header.split(' ')[1]
    
    # 简化实现：假设token就是user_id（实际项目中应该解析JWT）
    # 在实际项目中应该验证token并提取用户信息
    try:
        # 尝试从token中获取用户ID
        if ':' in token:
            user_id = token.split(':')[0]
        else:
            # 尝试检查token是否可以直接作为用户ID使用
            user_id = int(token)
    except:
        return jsonify({"code": 401, "msg": "无效的用户身份"}), 401
    
    # 从数据库获取用户信息
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"code": 404, "msg": "用户不存在"}), 404
    
    # 构建完整的头像URL
    avatar_url = "/static/images/users/user1.png"
    
    user_info = {
        "user_id": user.id,
        "nickname": user.username,
        "avatar": avatar_url,
        "phone": user.phone,
        "email": user.email,
        "balance": user.balance,
        "create_time": user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else "2023-01-01 00:00:00"
    }
    
    return jsonify({"code": 200, "msg": "成功", "data": user_info}), 200

@bp.route('/profile', methods=['PUT'])
def update_profile():
    # 从请求头获取Token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"code": 401, "msg": "未授权，请先登录"}), 401
    
    token = auth_header.split(' ')[1]
    
    # 简化实现：从token中提取用户ID
    try:
        # 假设token格式为 "user_id:时间戳"或直接就是用户ID
        if ':' in token:
            user_id = token.split(':')[0]
        else:
            # 尝试检查token是否可以直接作为用户ID使用
            user_id = int(token)
    except:
        return jsonify({"code": 401, "msg": "无效的用户身份，请重新登录"}), 401
    
    # 从数据库获取用户
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 404, "msg": "用户不存在"}), 404
    
    # 获取更新数据
    data = request.get_json()
    
    # 更新用户信息
    if 'username' in data and data['username']:
        user.username = data['username']
    if 'email' in data and data['email']:
        user.email = data['email']
    if 'phone' in data and data['phone']:
        user.phone = data['phone']
    
    # 保存更新到数据库
    try:
        db.session.commit()
        
        # 返回更新后的用户信息
        updated_user = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone
        }
        
        return jsonify({
            "code": 200,
            "msg": '用户信息更新成功',
            "data": updated_user
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": f"更新失败: {str(e)}"}), 500

@bp.route('/addresses', methods=['GET'])
def get_addresses():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"code": 401, "msg": "未授权，请先登录"}), 401

    token = auth_header.split(' ')[1]
    try:
        if ':' in token:
            user_id = int(token.split(':')[0])
        else:
            user_id = int(token)
    except:
        return jsonify({"code": 401, "msg": "无效的用户身份"}), 401

    addresses = Address.query.filter_by(user_id=user_id).all()
    return jsonify([address.to_dict() for address in addresses]), 200


@bp.route('/addresses', methods=['POST'])
def create_address():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"code": 401, "msg": "未授权"}), 401
    
    token = auth_header.split(' ')[1]
    try:
        if ':' in token:
            user_id = int(token.split(':')[0])
        else:
            user_id = int(token)
    except:
        return jsonify({"code": 401, "msg": "用户身份无效"}), 401

    data = request.get_json()
    required_fields = ['province', 'city', 'district', 'detail', 'name', 'phone']
    if not all(k in data for k in required_fields):
        return jsonify({"code": 400, "msg": '缺少必要字段'}), 400

    # 如果当前添加的是默认地址，则清除旧的默认地址
    if data.get("is_default"):
        Address.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})

    new_address = Address(
        user_id=user_id,
        province=data['province'],
        city=data['city'],
        district=data['district'],
        detail=data['detail'],
        name=data['name'],
        phone=data['phone'],
        is_default=data.get('is_default', False)
    )

    try:
        db.session.add(new_address)
        db.session.commit()
        return jsonify({
            "code": 200,
            "msg": '地址添加成功',
            "data": new_address.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": f"添加失败: {str(e)}"}), 500


@bp.route('/addresses/<int:id>', methods=['PUT'])
def update_address(id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"code": 401, "msg": "未授权"}), 401

    token = auth_header.split(' ')[1]
    try:
        if ':' in token:
            user_id = int(token.split(':')[0])
        else:
            user_id = int(token)
    except:
        return jsonify({"code": 401, "msg": "用户身份无效"}), 401

    address = Address.query.filter_by(id=id, user_id=user_id).first()
    
    if not address:
        return jsonify({"code": 404, "msg": "地址不存在或无权访问"}), 404
    
    data = request.get_json()

    if 'province' in data:
        address.province = data['province']
    if 'city' in data:
        address.city = data['city']
    if 'district' in data:
        address.district = data['district']
    if 'detail' in data:
        address.detail = data['detail']
    if 'name' in data:
        address.name = data['name']
    if 'phone' in data:
        address.phone = data['phone']

    if 'is_default' in data and data['is_default'] and not address.is_default:
        Address.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})
        address.is_default = True

    try:
        db.session.commit()
        return jsonify({
            "code": 200,
            "msg": "地址更新成功",
            "data": address.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": f"地址更新失败: {str(e)}"}), 500



@bp.route('/addresses/<int:id>', methods=['DELETE'])
def delete_address(id):
    import traceback  # 放在函数开头即可

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"code": 401, "msg": "未授权"}), 401

    token = auth_header.split(' ')[1]
    try:
        if ':' in token:
            user_id = int(token.split(':')[0])
        else:
            user_id = int(token)
    except:
        return jsonify({"code": 401, "msg": "用户身份无效"}), 401

    # ✅ 先查询 address
    address = Address.query.filter_by(id=id, user_id=user_id).first()
    if not address:
        return jsonify({"code": 404, "msg": "地址不存在或无权访问"}), 404

    # ✅ 新增：检查是否有订单使用该地址
    linked_order = Order.query.filter_by(address_id=id).first()
    if linked_order:
        return jsonify({"code": 400, "msg": "该地址已关联订单，无法删除"}), 400

    # 原始删除逻辑继续执行
    was_default = address.is_default
    try:
        db.session.delete(address)

        if was_default:
            new_default = Address.query.filter_by(user_id=user_id).first()
            if new_default:
                new_default.is_default = True

        db.session.commit()
        return jsonify({"code": 200, "msg": "地址删除成功"}), 200

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"code": 500, "msg": f"地址删除失败: {str(e)}"}), 500



@bp.route('/charge', methods=['POST'])
def charge():
    """用户充值"""
    # 从请求头获取Token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"code": 401, "msg": "未授权，请先登录"}), 401
    
    token = auth_header.split(' ')[1]
    
    # 简化实现：固定用户ID
    try:
        if ':' in token:
            user_id = int(token.split(':')[0])
        else:
            user_id = int(token)
    except:
        return jsonify({"code": 401, "msg": "无效的用户身份"}), 401
    
    # 获取请求数据
    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "msg": "请求数据无效"}), 400
    
    amount = data.get('amount')
    if not amount or not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({"code": 400, "msg": "充值金额必须大于0"}), 400
    
    # 从数据库获取用户信息
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 404, "msg": "用户不存在"}), 404
    
    # 更新余额
    try:
        user.balance += float(amount)
        db.session.commit()
        
        return jsonify({
            "code": 200,
            "msg": "充值成功",
            "data": {
                "balance": user.balance
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": f"充值失败: {str(e)}"}), 500

@bp.route('/update', methods=['POST'])
def update_user():
    """用户信息更新接口"""
    # 从请求头获取Token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"code": 401, "msg": "未授权，请先登录"}), 401
    
    token = auth_header.split(' ')[1]
    
    # 简化实现：从token中提取用户ID
    try:
        # 假设token格式为 "user_id:时间戳"或直接就是用户ID
        if ':' in token:
            user_id = token.split(':')[0]
        else:
            # 尝试检查token是否可以直接作为用户ID使用
            user_id = int(token)
    except:
        return jsonify({"code": 401, "msg": "无效的用户身份，请重新登录"}), 401
    
    # 从数据库获取用户
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 404, "msg": "用户不存在"}), 404
    
    # 获取更新数据
    data = request.get_json()
    
    # 更新用户信息
    if 'username' in data and data['username']:
        user.username = data['username']
    if 'email' in data and data['email']:
        user.email = data['email']
    if 'phone' in data and data['phone']:
        user.phone = data['phone']
    if 'nickname' in data and data['nickname']:
        user.username = data['nickname']  # 用nickname更新username字段
    
    # 保存更新到数据库
    try:
        db.session.commit()
        
        # 构建完整的头像URL
        avatar_url = "/static/images/users/user1.png"
        
        # 返回更新后的用户信息
        updated_user = {
            "user_id": user.id,
            "nickname": user.username,
            "email": user.email,
            "phone": user.phone,
            "avatar": avatar_url
        }
        
        return jsonify({
            "code": 200,
            "msg": '用户信息更新成功',
            "data": updated_user
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": f"更新失败: {str(e)}"}), 500 