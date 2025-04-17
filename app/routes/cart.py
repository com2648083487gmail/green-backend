from flask import Blueprint, request, jsonify
from app import db
from app.models.cart import CartItem
from app.models.product import Product
from app.models.user import User
from datetime import datetime

bp = Blueprint('cart', __name__, url_prefix='/api/cart')

# 获取购物车列表
@bp.route('/list', methods=['GET'])
def get_cart_items():
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({'code': 401, 'msg': '未授权'}), 401

    user_id = int(token.split(' ')[1].split(':')[0])
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404

    cart_items = CartItem.query.filter_by(user_id=user_id).all()

    enriched_items = []
    for item in cart_items:
        product = Product.query.get(item.product_id)
        image = product.images[0].url if product.images else ''
        # 防止重复拼接 localhost
        if image and not image.startswith('http'):
            image = f"https://web-production-85aa.up.railway.app{image}"

        enriched_items.append({
            'id': item.id,
            'product_id': item.product_id,
            'quantity': item.quantity,
            'name': product.name,
            'price': product.price,
            'image': image
        })

    return jsonify({'code': 200, 'msg': '成功', 'data': enriched_items})

# 添加商品到购物车
@bp.route('/add', methods=['POST'])
def add_to_cart():
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({'code': 401, 'msg': '未授权'}), 401

    user_id = int(token.split(' ')[1].split(':')[0])
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    if not product_id:
        return jsonify({'code': 400, 'msg': '缺少商品ID'}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'code': 404, 'msg': '商品不存在'}), 404

    item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if item:
        item.quantity += quantity
    else:
        item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(item)

    db.session.commit()
    return jsonify({'code': 200, 'msg': '添加成功'})

# 更新购物车商品数量
@bp.route('/update', methods=['PUT', 'POST'])
def update_cart():
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({'code': 401, 'msg': '未授权'}), 401

    user_id = int(token.split(' ')[1].split(':')[0])
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    if not product_id or quantity is None:
        return jsonify({'code': 400, 'msg': '参数不完整'}), 400

    item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if not item:
        return jsonify({'code': 404, 'msg': '购物车项不存在'}), 404

    item.quantity = quantity
    db.session.commit()
    return jsonify({'code': 200, 'msg': '更新成功'})

# 删除购物车项
@bp.route('/delete/<int:product_id>', methods=['DELETE'])
def delete_cart(product_id):
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({'code': 401, 'msg': '未授权'}), 401

    user_id = int(token.split(' ')[1].split(':')[0])

    item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if not item:
        return jsonify({'code': 404, 'msg': '购物车项不存在'}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '删除成功'})

