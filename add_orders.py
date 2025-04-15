from app import create_app, db
from app.models.user import User, Address
from app.models.product import Product
from app.models.order import Order, OrderItem
from datetime import datetime, timedelta
import random
import uuid

# 示例订单状态
ORDER_STATUSES = ['pending', 'paid', 'shipped', 'delivered', 'canceled']

def generate_order_number():
    """生成订单号，格式为：年月日+8位随机数字"""
    now = datetime.now()
    date_prefix = now.strftime('%Y%m%d')
    random_suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
    return f"{date_prefix}{random_suffix}"

def add_sample_orders():
    """添加示例订单数据"""
    app = create_app()
    with app.app_context():
        # 获取用户、地址和产品数据
        users = User.query.all()
        addresses = Address.query.all()
        products = Product.query.all()
        
        if not users:
            print("没有用户数据，请先添加用户")
            return
        
        if not addresses:
            print("没有地址数据，请先添加地址")
            return
        
        if not products:
            print("没有产品数据，请先添加产品")
            return
        
        print(f"发现 {len(users)} 个用户, {len(addresses)} 个地址, {len(products)} 个产品")
        
        # 创建10个示例订单
        for i in range(10):
            # 随机选择用户和地址
            user = random.choice(users)
            # 尝试获取该用户的地址，如果没有则随机选择一个
            user_addresses = [addr for addr in addresses if addr.user_id == user.id]
            address = random.choice(user_addresses) if user_addresses else random.choice(addresses)
            
            # 创建订单
            order = Order(
                user_id=user.id,
                order_number=generate_order_number(),
                status=random.choice(ORDER_STATUSES),
                total_amount=0,  # 初始化为0，稍后计算
                address_id=address.id,
                created_at=datetime.now() - timedelta(days=random.randint(0, 30)),
            )
            
            # 添加1-5个订单项
            order_items = []
            for _ in range(random.randint(1, 5)):
                product = random.choice(products)
                quantity = random.randint(1, 5)
                
                # 创建订单项
                order_item = OrderItem(
                    product_id=product.id,
                    quantity=quantity,
                    price=product.price  # 使用产品当前价格
                )
                order_items.append(order_item)
            
            # 计算订单总金额
            total_amount = sum(item.price * item.quantity for item in order_items)
            order.total_amount = total_amount
            
            # 保存订单
            db.session.add(order)
            db.session.flush()  # 获取订单ID
            
            # 关联订单项到订单
            for item in order_items:
                item.order_id = order.id
                db.session.add(item)
            
            print(f"创建订单 #{i+1}: 用户={user.username}, 订单号={order.order_number}, 状态={order.status}, 总金额={order.total_amount:.2f}")
        
        # 提交事务
        db.session.commit()
        print("成功添加示例订单数据")

if __name__ == "__main__":
    add_sample_orders() 