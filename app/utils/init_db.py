from app import create_app, db
from app.models.user import User, Address
from app.models.product import Product, ProductImage
from app.models.order import Order, OrderItem
import random
import datetime

def init_db():
    """初始化数据库并添加测试数据"""
    app = create_app()
    with app.app_context():
        # 创建数据库表
        db.drop_all()
        db.create_all()
        
        # 创建测试用户
        create_test_users()
        
        # 创建测试产品
        create_test_products()
        
        # 创建测试订单
        create_test_orders()
        
        print("数据库初始化完成，测试数据已创建")

def create_test_users():
    """创建测试用户数据"""
    # 创建管理员用户
    admin = User(username='admin', email='admin@example.com', phone='13800000000')
    admin.set_password('admin123')
    
    # 创建普通用户
    user1 = User(username='user1', email='user1@example.com', phone='13800000001')
    user1.set_password('user123')
    
    user2 = User(username='user2', email='user2@example.com', phone='13800000002')
    user2.set_password('user123')
    
    db.session.add_all([admin, user1, user2])
    db.session.commit()
    
    # 为用户添加地址
    address1 = Address(
        user_id=user1.id,
        province='广东省',
        city='深圳市',
        district='南山区',
        detail='科技园88号',
        name='张三',
        phone='13800000001',
        is_default=True
    )
    
    address2 = Address(
        user_id=user1.id,
        province='广东省',
        city='广州市',
        district='天河区',
        detail='天河路101号',
        name='张三',
        phone='13800000001',
        is_default=False
    )
    
    address3 = Address(
        user_id=user2.id,
        province='北京市',
        city='北京市',
        district='海淀区',
        detail='中关村大街20号',
        name='李四',
        phone='13800000002',
        is_default=True
    )
    
    db.session.add_all([address1, address2, address3])
    db.session.commit()

def create_test_products():
    """创建测试产品数据"""
    products = [
        {
            'name': '环保实木书桌',
            'description': '采用FSC认证的可持续森林木材制成，无甲醛释放，低碳环保家具的优选。',
            'price': 999.00,
            'stock': 50,
            'category': '书桌',
            'eco_friendly': True,
            'eco_labels': 'FSC认证,低碳,可回收',
            'material': '实木',
            'carbon_footprint': 25.5,
            'images': [
                '/static/images/product/eco_table_1.jpg',
            ]
        },
        {
            'name': '竹制收纳柜',
            'description': '100%竹制材料，天然可再生资源，比木材生长速度快10倍，减少森林砍伐。',
            'price': 699.00,
            'stock': 30,
            'category': '收纳',
            'eco_friendly': True,
            'eco_labels': '竹材,可再生,零甲醛',
            'material': '竹子',
            'carbon_footprint': 18.2,
            'images': [
                '/static/images/product/eco_cabinet_1.jpg',
            ]
        },
        {
            'name': '再生纸浆环保餐桌',
            'description': '使用回收纸浆压制而成，强度高，防水耐用，100%可回收材料。',
            'price': 1299.00,
            'stock': 20,
            'category': '餐桌',
            'eco_friendly': True,
            'eco_labels': '再生材料,可回收,低碳',
            'material': '再生纸浆',
            'carbon_footprint': 12.8,
            'images': [
                '/static/images/product/eco_table_1.jpg',
            ]
        },
        {
            'name': '简约风格沙发',
            'description': '采用环保面料和填充物，无化学添加剂，布套可拆洗，方便清洁。',
            'price': 2999.00,
            'stock': 15,
            'category': '沙发',
            'eco_friendly': True,
            'eco_labels': '零污染,低过敏,节能生产',
            'material': '环保面料',
            'carbon_footprint': 35.6,
            'images': [
                '/static/images/product/default.jpg',
            ]
        },
        {
            'name': '环保实木床',
            'description': '采用天然木材制成，环保漆涂装，零甲醛释放，给您健康的睡眠环境。',
            'price': 3499.00,
            'stock': 10,
            'category': '床',
            'eco_friendly': True,
            'eco_labels': '天然木材,零甲醛,环保漆',
            'material': '橡木',
            'carbon_footprint': 30.2,
            'images': [
                '/static/images/product/eco_bed_1.jpg',
            ]
        }
    ]
    
    for product_data in products:
        product = Product(
            name=product_data['name'],
            description=product_data['description'],
            price=product_data['price'],
            stock=product_data['stock'],
            category=product_data['category'],
            eco_friendly=product_data['eco_friendly'],
            eco_labels=product_data['eco_labels'],
            material=product_data['material'],
            carbon_footprint=product_data['carbon_footprint']
        )
        db.session.add(product)
        db.session.flush()  # 获取产品ID
        
        # 添加产品图片
        for i, img_url in enumerate(product_data['images']):
            image = ProductImage(
                product_id=product.id,
                url=img_url,
                is_primary=(i == 0)
            )
            db.session.add(image)
    
    db.session.commit()

def create_test_orders():
    """创建测试订单数据"""
    # 获取用户和地址
    user1 = User.query.filter_by(username='user1').first()
    user2 = User.query.filter_by(username='user2').first()
    
    address1 = Address.query.filter_by(user_id=user1.id, is_default=True).first()
    address2 = Address.query.filter_by(user_id=user2.id, is_default=True).first()
    
    # 获取所有产品
    products = Product.query.all()
    
    # 为用户1创建订单
    order1 = Order(
        user_id=user1.id,
        order_number=f"ORDER{datetime.datetime.now().strftime('%Y%m%d')}001",
        status='delivered',
        total_amount=products[0].price * 1 + products[2].price * 2,
        address_id=address1.id,
        created_at=datetime.datetime.now() - datetime.timedelta(days=15)
    )
    
    order1_item1 = OrderItem(
        order=order1,
        product_id=products[0].id,
        quantity=1,
        price=products[0].price
    )
    
    order1_item2 = OrderItem(
        order=order1,
        product_id=products[2].id,
        quantity=2,
        price=products[2].price
    )
    
    db.session.add_all([order1, order1_item1, order1_item2])
    
    # 为用户1创建另一个订单
    order2 = Order(
        user_id=user1.id,
        order_number=f"ORDER{datetime.datetime.now().strftime('%Y%m%d')}002",
        status='shipped',
        total_amount=products[3].price * 1,
        address_id=address1.id,
        created_at=datetime.datetime.now() - datetime.timedelta(days=5)
    )
    
    order2_item1 = OrderItem(
        order=order2,
        product_id=products[3].id,
        quantity=1,
        price=products[3].price
    )
    
    db.session.add_all([order2, order2_item1])
    
    # 为用户2创建订单
    order3 = Order(
        user_id=user2.id,
        order_number=f"ORDER{datetime.datetime.now().strftime('%Y%m%d')}003",
        status='pending',
        total_amount=products[1].price * 2 + products[4].price * 3,
        address_id=address2.id,
        created_at=datetime.datetime.now() - datetime.timedelta(days=2)
    )
    
    order3_item1 = OrderItem(
        order=order3,
        product_id=products[1].id,
        quantity=2,
        price=products[1].price
    )
    
    order3_item2 = OrderItem(
        order=order3,
        product_id=products[4].id,
        quantity=3,
        price=products[4].price
    )
    
    db.session.add_all([order3, order3_item1, order3_item2])
    db.session.commit()

if __name__ == '__main__':
    init_db() 