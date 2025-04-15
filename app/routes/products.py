from flask import Blueprint, request, jsonify
from app.models.product import Product, ProductImage
from app import db
import uuid
import os

bp = Blueprint('products', __name__, url_prefix='/api/products')

@bp.route('', methods=['GET'])
def get_products():
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category = request.args.get('category')
    eco_friendly = request.args.get('eco_friendly')
    
    # 构建查询
    query = Product.query
    
    if category:
        query = query.filter(Product.category == category)
    
    if eco_friendly and eco_friendly.lower() == 'true':
        query = query.filter(Product.eco_friendly == True)
    
    # 执行分页查询
    pagination = query.order_by(Product.created_at.desc()).paginate(page=page, per_page=per_page)
    
    # 处理产品数据，确保图片URL正确
    items = []
    for product in pagination.items:
        product_dict = product.to_dict()
        # 确保图片URL是完整的路径
        if product_dict['images']:
            product_dict['images'] = [f"http://localhost:8000{url}" if url.startswith('/') else url for url in product_dict['images']]
        items.append(product_dict)
    
    return jsonify({
        'items': items,
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page
    }), 200

# 添加与小程序匹配的/list路由
@bp.route('/list', methods=['GET'])
def get_products_list():
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 10, type=int)
    category_id = request.args.get('category_id')
    keyword = request.args.get('keyword')
    
    # 构建查询
    query = Product.query
    
    if category_id:
        query = query.filter(Product.category == category_id)
    
    if keyword:
        query = query.filter(Product.name.contains(keyword) | Product.description.contains(keyword))
    
    # 执行分页查询
    pagination = query.order_by(Product.created_at.desc()).paginate(page=page, per_page=size)
    
    # 处理产品数据
    products_list = []
    for item in pagination.items:
        # 处理图片URL
        images = [f"http://localhost:8000{img.url}" if img.url.startswith('/') else img.url for img in item.images]
        default_image = "http://localhost:8000/static/images/product/default.jpg"
        
        product_data = {
            'product_id': item.id,
            'name': item.name,
            'description': item.description,
            'price': item.price,
            'category_id': item.category,
            'category_name': item.category,  # 实际应该从分类表获取名称
            'image': images[0] if images else default_image,
            'images': images if images else [default_image],
            'create_time': item.created_at.strftime('%Y-%m-%d %H:%M:%S') if item.created_at else ''
        }
        products_list.append(product_data)
    
    # 返回符合API文档的响应格式
    return jsonify({
        'code': 200,
        'msg': '成功',
        'data': {
            'total': pagination.total,
            'list': products_list
        }
    })

# 添加分类接口
@bp.route('/categories', methods=['GET'])
def get_categories():
    # 从数据库获取产品分类
    categories_query = db.session.query(Product.category).distinct()
    categories_query = categories_query.filter(Product.category.isnot(None))
    
    # 获取分类列表
    raw_categories = [item[0] for item in categories_query.all() if item[0]]
    
    # 组装分类数据
    categories = []
    # 图片映射，确保使用服务器上真实存在的图片
    category_image_map = {
        'table': '/static/images/category/category_table.png',
        'chair': '/static/images/category/category_chair.png',
        'bed': '/static/images/category/category_bed.png'
    }
    
    for i, cat_name in enumerate(raw_categories, start=1):
        # 确定图片路径
        lower_cat = cat_name.lower()
        if lower_cat in category_image_map:
            image_path = category_image_map[lower_cat]
        else:
            image_path = '/static/images/category/category_default.png'
        
        category = {
            'category_id': cat_name,
            'category_name': cat_name,
            'image': f"http://localhost:8000{image_path}"
        }
        categories.append(category)
    
    return jsonify({
        'code': 200,
        'msg': '成功',
        'data': categories
    })

@bp.route('/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get(id)
    
    if not product:
        return jsonify({'message': '产品不存在'}), 404
    
    return jsonify(product.to_dict()), 200

# 添加与小程序匹配的/detail路由
@bp.route('/detail', methods=['GET'])
def get_product_detail():
    product_id = request.args.get('product_id')
    if not product_id:
        return jsonify({'code': 400, 'msg': '缺少商品ID参数'}), 400
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'code': 404, 'msg': '商品不存在'}), 404
    
    # 处理图片URL
    images = [f"http://localhost:8000{img.url}" if img.url.startswith('/') else img.url for img in product.images]
    default_image = "http://localhost:8000/static/images/product/default.jpg"
    
    # 返回符合API文档的响应格式
    return jsonify({
        'code': 200,
        'msg': '成功',
        'data': {
            'product_id': product.id,
            'name': product.name,
            'description': product.description,
            'content': product.description,
            'price': product.price,
            'category_id': product.category,
            'category_name': product.category,
            'material': product.material,
            'carbon_footprint': product.carbon_footprint,
            'eco_labels': product.eco_labels.split(',') if product.eco_labels else [],
            'image': images[0] if images else default_image,
            'images': images if images else [default_image],
            'create_time': product.created_at.strftime('%Y-%m-%d %H:%M:%S') if product.created_at else ''
        }
    })

@bp.route('', methods=['POST'])
def create_product():
    data = request.get_json()
    
    # 检查必要字段
    if not all(k in data for k in ('name', 'price')):
        return jsonify({'message': '缺少必要字段'}), 400
    
    # 创建新产品
    product = Product(
        name=data['name'],
        description=data.get('description'),
        price=data['price'],
        stock=data.get('stock', 0),
        category=data.get('category'),
        eco_friendly=data.get('eco_friendly', False),
        eco_labels=','.join(data.get('eco_labels', [])) if isinstance(data.get('eco_labels'), list) else data.get('eco_labels', ''),
        material=data.get('material'),
        carbon_footprint=data.get('carbon_footprint')
    )
    
    try:
        db.session.add(product)
        
        # 处理产品图片
        if 'images' in data and isinstance(data['images'], list):
            for i, img_url in enumerate(data['images']):
                image = ProductImage(
                    url=img_url,
                    product=product,
                    is_primary=(i == 0)  # 第一张图片设为主图
                )
                db.session.add(image)
        
        db.session.commit()
        return jsonify({
            'message': '产品创建成功',
            'product': product.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'产品创建失败: {str(e)}'}), 500

@bp.route('/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get(id)
    
    if not product:
        return jsonify({'message': '产品不存在'}), 404
    
    data = request.get_json()
    
    # 更新产品信息
    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'price' in data:
        product.price = data['price']
    if 'stock' in data:
        product.stock = data['stock']
    if 'category' in data:
        product.category = data['category']
    if 'eco_friendly' in data:
        product.eco_friendly = data['eco_friendly']
    if 'eco_labels' in data:
        product.eco_labels = ','.join(data['eco_labels']) if isinstance(data['eco_labels'], list) else data['eco_labels']
    if 'material' in data:
        product.material = data['material']
    if 'carbon_footprint' in data:
        product.carbon_footprint = data['carbon_footprint']
    
    try:
        # 处理产品图片
        if 'images' in data and isinstance(data['images'], list):
            # 删除现有图片
            for image in product.images:
                db.session.delete(image)
            
            # 添加新图片
            for i, img_url in enumerate(data['images']):
                image = ProductImage(
                    url=img_url,
                    product=product,
                    is_primary=(i == 0)  # 第一张图片设为主图
                )
                db.session.add(image)
        
        db.session.commit()
        return jsonify({
            'message': '产品更新成功',
            'product': product.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'产品更新失败: {str(e)}'}), 500

@bp.route('/<int:id>', methods=['DELETE'])
def delete_product(id):
    print(f"尝试删除产品ID: {id}")
    
    product = Product.query.get(id)
    
    if not product:
        print(f"产品ID {id} 不存在")
        return jsonify({'message': '产品不存在'}), 404
    
    try:
        # 检查是否有订单项引用此产品
        from app.models.order import OrderItem
        order_items = OrderItem.query.filter_by(product_id=id).all()
        
        if order_items:
            order_count = len(order_items)
            print(f"产品ID {id} ({product.name}) 被 {order_count} 个订单项引用，无法直接删除")
            return jsonify({
                'message': f'无法删除产品，该产品已被 {order_count} 个订单引用。请先删除相关订单或将订单中的产品替换为其他产品。',
                'referenced_by_orders': True
            }), 400
        
        # 删除产品的所有图片
        print(f"删除产品 {product.name} 的 {len(product.images)} 张图片")
        
        # 删除产品
        print(f"开始删除产品: {product.name}")
        db.session.delete(product)
        db.session.commit()
        print(f"产品 {product.name} 删除成功")
        
        return jsonify({'message': '产品删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        print(f"删除产品时出错: {error_msg}")
        
        # 检查是否是外键约束错误
        if "foreign key constraint fails" in error_msg.lower():
            return jsonify({
                'message': '该产品正被订单使用，无法删除。请先删除相关订单。',
                'detail': error_msg
            }), 400
        
        return jsonify({'message': f'产品删除失败: {error_msg}'}), 500 