from flask import Blueprint, request, jsonify
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User, Address
from app import db
import datetime
import random
import string

bp = Blueprint('orders', __name__, url_prefix='/api/orders')

def generate_order_number():
    """生成订单号: 当前日期 + 6位随机字符"""
    date_str = datetime.datetime.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{date_str}{random_str}"

@bp.route('', methods=['GET'])
def get_orders():
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 获取筛选参数
    order_number = request.args.get('order_number')
    status = request.args.get('status')
    
    # 构建查询条件
    query = Order.query.join(Order.user)
    
    if order_number:
        query = query.filter(Order.order_number.like(f'%{order_number}%'))
    if status:
        query = query.filter(Order.status == status)
    
    # 执行分页查询，确保加载用户信息
    pagination = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    orders = pagination.items
    
    # 格式化订单数据
    order_list = [order.to_dict() for order in orders]
    
    return jsonify({
        "items": order_list,
        "total": pagination.total
    })

@bp.route('/<int:id>', methods=['GET'])
def get_order(id):
    # 查询订单，同时加载用户信息
    order = Order.query.join(Order.user).filter(Order.id == id).first_or_404()
    
    # 返回订单详情
    return jsonify(order.to_dict())

@bp.route('', methods=['POST'])
def create_order():
    data = request.get_json()
    
    # 检查必要字段
    if not all(k in data for k in ('user_id', 'address_id', 'items')):
        return jsonify({"message": '缺少必要字段'}), 400
    
    # 获取数据
    user_id = data['user_id']
    address_id = data['address_id']
    items_data = data['items']
    
    # 创建订单
    new_order = Order(
        user_id=user_id,
        address_id=address_id,
        order_number=generate_order_number(),
        status='pending',
        total_amount=0
    )
    
    # 添加订单项
    total_amount = 0
    order_items = []
    
    for item_data in items_data:
        product_id = item_data.get('product_id')
        quantity = item_data.get('quantity', 1)
        
        # 查询产品
        product = Product.query.get(product_id)
        if not product:
            continue
        
        # 检查库存
        if product.stock < quantity:
            return jsonify({"message": f"产品 {product.name} 库存不足"}), 400
        
        # 减少库存
        product.stock -= quantity
        
        # 创建订单项
        order_item = OrderItem(
            product_id=product_id,
            quantity=quantity,
            price=product.price
        )
        
        # 计算小计
        item_total = product.price * quantity
        total_amount += item_total
        
        order_items.append(order_item)
    
    # 更新订单总额
    new_order.total_amount = round(total_amount, 2)
    
    # 保存订单
    db.session.add(new_order)
    db.session.flush()  # 获取订单ID
    
    # 关联订单项
    for item in order_items:
        item.order_id = new_order.id
        db.session.add(item)
    
    try:
        db.session.commit()
        return jsonify({
            "message": "订单创建成功",
            "order_id": new_order.id,
            "order_number": new_order.order_number
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"创建订单失败: {str(e)}"}), 500

@bp.route('/<int:id>/status', methods=['PUT', 'POST'])
def update_order_status(id):
    # 查找订单，不再限制用户ID
    order = Order.query.get_or_404(id)
    
    data = request.get_json()
    
    if 'status' not in data:
        return jsonify({'message': '缺少状态字段'}), 400
    
    # 验证状态值是否合法
    valid_statuses = ['pending', 'paid', 'shipped', 'delivered', 'canceled']
    if data['status'] not in valid_statuses:
        return jsonify({'message': '无效的状态值'}), 400
    
    # 验证状态变更的合法性（例如已发货的订单不能取消）
    if order.status == 'shipped' and data['status'] == 'canceled':
        return jsonify({'message': '已发货的订单不能取消'}), 400
    
    # 如果取消订单，恢复库存
    if data['status'] == 'canceled' and order.status != 'canceled':
        for item in order.items:
            product = Product.query.get(item.product_id)
            if product:
                product.stock += item.quantity
    
    # 更新状态
    order.status = data['status']
    
    try:
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '订单状态更新成功',
            'order': order.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'订单状态更新失败: {str(e)}'}), 500

@bp.route('/list', methods=['GET'])
def get_orders_list():
    """获取当前用户的订单列表 - 小程序专用接口"""
    # 从请求头获取Token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"code": 401, "msg": "未授权，请先登录"}), 401
    
    token = auth_header.split(' ')[1]
    
    # 从token中提取用户ID
    try:
        # 尝试从token中获取用户ID
        if ':' in token:
            user_id = int(token.split(':')[0])
        else:
            # 尝试将token直接作为用户ID使用
            user_id = int(token)
    except:
        return jsonify({"code": 401, "msg": "无效的用户身份，请重新登录"}), 401
    
    # 检查用户是否存在
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 404, "msg": "用户不存在"}), 404
    
    # 获取请求参数
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 10, type=int)
    status = request.args.get('status')  # 订单状态筛选
    
    # 构建查询
    query = Order.query.filter_by(user_id=user_id)
    
    if status and status != 'all':
        query = query.filter(Order.status == status)
    
    # 执行分页查询
    pagination = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=size)
    
    # 处理订单数据
    orders_list = []
    for order in pagination.items:
        items = []
        for item in order.items:
            try:
                product = Product.query.get(item.product_id)
                product_name = product.name if product else "未知商品"
                product_image = ""
                if product and product.images and product.images[0]:
                    image_url = product.images[0].url
                    product_image = f"http://localhost:8000{image_url}" if image_url.startswith('/') else image_url
            except Exception as e:
                print(f"获取商品信息失败: {str(e)}")
                product_name = "商品信息获取失败"
                product_image = ""
            
            item_data = {
                "id": item.id,
                "product_id": item.product_id,
                "name": product_name,
                "image": product_image,
                "price": float(item.price) if item.price else 0,
                "quantity": item.quantity
            }
            items.append(item_data)
        
        order_data = {
            "order_id": order.id,
            "order_number": order.order_number,
            "status": order.status,
            "status_text": {
                "pending": "待付款",
                "paid": "已支付",
                "shipped": "已发货",
                "delivered": "已送达",
                "canceled": "已取消"
            }.get(order.status, "未知状态"),
            "total_amount": round(float(order.total_amount), 2) if order.total_amount else 0,
            "create_time": order.created_at.strftime("%Y-%m-%d %H:%M:%S") if order.created_at else "",
            "items": items
        }
        orders_list.append(order_data)
    
    return jsonify({
        "code": 200,
        "msg": "成功",
        "data": {
            "total": pagination.total,
            "list": orders_list
        }
    })

@bp.route('/create', methods=['POST'])
def create_order_api():
    """创建订单 - 小程序专用接口"""
    # 从请求头获取Token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"code": 401, "msg": "未授权，请先登录"}), 401
    
    token = auth_header.split(' ')[1]
    
    # 从token中提取用户ID
    try:
        # 尝试从token中获取用户ID
        if ':' in token:
            user_id = int(token.split(':')[0])
        else:
            # 尝试将token直接作为用户ID使用
            user_id = int(token)
    except:
        return jsonify({"code": 401, "msg": "无效的用户身份，请重新登录"}), 401
    
    # 检查用户是否存在
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 404, "msg": "用户不存在"}), 404
    
    # 获取请求数据
    data = request.get_json()
    print("🟢 接收到的订单数据：", data) 
    if not data:
        return jsonify({"code": 400, "msg": "请求数据无效"}), 400
    
    # 检查必要字段
    if 'address_id' not in data or 'items' not in data or not data['items']:
        return jsonify({"code": 400, "msg": "缺少必要参数"}), 400
    
    address_id = data['address_id']
    items_data = data['items']
    
    # 创建订单
    new_order = Order(
        user_id=user_id,
        address_id=address_id,
        order_number=generate_order_number(),
        status='pending',
        total_amount=0
    )
    
    # 添加订单项
    total_amount = 0
    order_items = []
    
    for item_data in items_data:
        product_id = item_data.get('product_id')
        quantity = item_data.get('quantity', 1)
        
        if not product_id or not quantity:
            continue
        
        # 查询产品
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"code": 400, "msg": f"商品ID {product_id} 不存在"}), 400
        
        # 检查库存
        if product.stock < quantity:
            return jsonify({"code": 400, "msg": f"商品 {product.name} 库存不足"}), 400
        
        # 减少库存
        product.stock -= quantity
        
        # 创建订单项
        order_item = OrderItem(
            product_id=product_id,
            quantity=quantity,
            price=product.price
        )
        
        # 计算小计
        item_total = product.price * quantity
        total_amount += item_total
        
        order_items.append(order_item)
    
    # 更新订单总额
    new_order.total_amount = total_amount
    
    # 保存订单
    try:
        db.session.add(new_order)
        db.session.flush()  # 获取订单ID
        
        # 关联订单项
        for item in order_items:
            item.order_id = new_order.id
            db.session.add(item)
        
        db.session.commit()
        
        return jsonify({
            "code": 200,
            "msg": "订单创建成功",
            "data": {
                "order_id": new_order.id,
                "order_number": new_order.order_number,
                "total_amount": round(float(new_order.total_amount), 2)
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": f"创建订单失败: {str(e)}"}), 500 

@bp.route('/detail', methods=['GET'])
def get_order_detail_api():
    """获取订单详情 - 小程序专用接口"""
    # 从请求头获取Token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"code": 401, "msg": "未授权，请先登录"}), 401
    
    token = auth_header.split(' ')[1]
    
    # 从token中提取用户ID
    try:
        # 尝试从token中获取用户ID
        if ':' in token:
            user_id = int(token.split(':')[0])
        else:
            # 尝试将token直接作为用户ID使用
            user_id = int(token)
    except:
        return jsonify({"code": 401, "msg": "无效的用户身份，请重新登录"}), 401
    
    # 检查用户是否存在
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 404, "msg": "用户不存在"}), 404
    
    # 获取订单ID参数
    order_id = request.args.get('order_id', type=int)
    if not order_id:
        return jsonify({"code": 400, "msg": "缺少订单ID参数"}), 400
    
    # 查询订单
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return jsonify({"code": 404, "msg": "订单不存在或无权查看"}), 404
    
    # 获取收货地址
    address_info = None
    if order.address_id:
        address = Address.query.get(order.address_id)
        if address:
            address_info = {
                "id": address.id,
                "name": address.name,
                "phone": address.phone,
                "province": address.province,
                "city": address.city,
                "district": address.district,
                "detail": address.detail,
                "is_default": address.is_default
            }
    
    # 获取订单项
    items = []
    for item in order.items:
        try:
            product = Product.query.get(item.product_id)
            product_name = product.name if product else "未知商品"
            product_image = ""
            if product and product.images and product.images[0]:
                image_url = product.images[0].url
                product_image = f"http://localhost:8000{image_url}" if image_url.startswith('/') else image_url
        except Exception as e:
            print(f"获取商品信息失败: {str(e)}")
            product_name = "商品信息获取失败"
            product_image = ""
        
        item_data = {
            "id": item.id,
            "product_id": item.product_id,
            "name": product_name,
            "image": product_image,
            "price": float(item.price) if item.price else 0,
            "quantity": item.quantity,
            "total": float(item.price * item.quantity) if item.price else 0
        }
        items.append(item_data)
    
    # 构建订单详情
    order_data = {
        "order_id": order.id,
        "order_number": order.order_number,
        "status": order.status,
        "status_text": {
            "pending": "待付款",
            "paid": "已支付",
            "shipped": "已发货",
            "delivered": "已送达",
            "canceled": "已取消"
        }.get(order.status, "未知状态"),
        "total_amount": round(float(order.total_amount), 2) if order.total_amount else 0,
        "create_time": order.created_at.strftime("%Y-%m-%d %H:%M:%S") if order.created_at else "",
        "update_time": order.updated_at.strftime("%Y-%m-%d %H:%M:%S") if order.updated_at else "",
        "address": address_info,
        "items": items
    }
    
    return jsonify({
        "code": 200,
        "msg": "成功",
        "data": order_data
    })

@bp.route('/pay', methods=['POST'])
def pay_order_api():
    """订单支付 - 小程序专用接口"""
    # 从请求头获取Token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"code": 401, "msg": "未授权，请先登录"}), 401
    
    token = auth_header.split(' ')[1]
    
    # 从token中提取用户ID
    try:
        # 尝试从token中获取用户ID
        if ':' in token:
            user_id = int(token.split(':')[0])
        else:
            # 尝试将token直接作为用户ID使用
            user_id = int(token)
    except:
        return jsonify({"code": 401, "msg": "无效的用户身份，请重新登录"}), 401
    
    # 检查用户是否存在
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 404, "msg": "用户不存在"}), 404
    
    # 获取请求数据
    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "msg": "请求数据无效"}), 400
    
    # 检查必要字段
    if 'order_id' not in data:
        return jsonify({"code": 400, "msg": "缺少订单ID参数"}), 400
    
    order_id = data['order_id']
    
    # 查询订单
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return jsonify({"code": 404, "msg": "订单不存在或无权操作"}), 404
    
    # 检查订单状态
    if order.status != 'pending':
        return jsonify({"code": 400, "msg": f"订单状态为{order.status}，不能支付"}), 400
    
    # 获取用户信息，检查余额
    if user.balance < order.total_amount:
        return jsonify({"code": 400, "msg": "余额不足，请先充值"}), 400
    
    try:
        # 扣减用户余额
        user.balance -= order.total_amount
        
        # 更改订单状态
        order.status = 'paid'
        order.updated_at = datetime.datetime.now()
        
        db.session.commit()
        
        return jsonify({
            "code": 200,
            "msg": "支付成功",
            "data": {
                "order_id": order.id,
                "status": order.status,
                "balance": float(user.balance)
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": f"支付失败: {str(e)}"}), 500

@bp.route('/confirm', methods=['POST'])
def confirm_order_api():
    """确认收货 - 小程序专用接口"""
    # 从请求头获取Token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"code": 401, "msg": "未授权，请先登录"}), 401
    
    token = auth_header.split(' ')[1]
    
    # 从token中提取用户ID
    try:
        # 尝试从token中获取用户ID
        if ':' in token:
            user_id = int(token.split(':')[0])
        else:
            # 尝试将token直接作为用户ID使用
            user_id = int(token)
    except:
        return jsonify({"code": 401, "msg": "无效的用户身份，请重新登录"}), 401
    
    # 检查用户是否存在
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 404, "msg": "用户不存在"}), 404
    
    # 获取请求数据
    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "msg": "请求数据无效"}), 400
    
    # 检查必要字段
    if 'order_id' not in data:
        return jsonify({"code": 400, "msg": "缺少订单ID参数"}), 400
    
    order_id = data['order_id']
    
    # 查询订单
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return jsonify({"code": 404, "msg": "订单不存在或无权操作"}), 404
    
    # 检查订单状态
    if order.status != 'shipped':
        return jsonify({"code": 400, "msg": f"订单状态为{order.status}，不能确认收货"}), 400
    
    try:
        # 更改订单状态
        order.status = 'delivered'
        order.updated_at = datetime.datetime.now()
        
        db.session.commit()
        
        return jsonify({
            "code": 200,
            "msg": "确认收货成功",
            "data": {
                "order_id": order.id,
                "status": order.status
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": f"确认收货失败: {str(e)}"}), 500

@bp.route('/<int:id>/action', methods=['POST'])
def order_action(id):
    """处理订单操作 - 例如删除订单"""
    # 查找订单
    order = Order.query.get_or_404(id)
    
    data = request.get_json()
    
    if 'action' not in data:
        return jsonify({'message': '缺少action字段'}), 400
    
    action = data['action']
    
    if action == 'delete':
        try:
            # 移除状态限制，允许删除任何状态的订单
            # 获取订单项
            order_items = OrderItem.query.filter_by(order_id=id).all()
            
            # 删除订单项
            for item in order_items:
                db.session.delete(item)
            
            # 删除订单
            db.session.delete(order)
            db.session.commit()
            
            return jsonify({
                'message': '订单删除成功'
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'订单删除失败: {str(e)}'}), 500
    else:
        return jsonify({'message': f'不支持的操作: {action}'}), 400