from app import create_app, db
from app.models.user import User
from app.models.order import Order

app = create_app()

with app.app_context():
    # 检查用户ID=3的订单
    user_id = 3
    user = User.query.get(user_id)
    
    if user:
        print(f"用户信息: ID={user.id}, 用户名={user.username}, 电话={user.phone}")
        
        # 检查订单
        orders = Order.query.filter_by(user_id=user_id).all()
        print(f"用户{user.username}有{len(orders)}个订单")
        
        for order in orders:
            print(f"订单ID: {order.id}, 订单号: {order.order_number}, 状态: {order.status}")
            
            # 获取订单项
            if hasattr(order, 'items') and order.items:
                print(f"  订单项数量: {len(order.items)}")
                for item in order.items:
                    print(f"  订单项ID: {item.id}, 产品ID: {item.product_id}, 数量: {item.quantity}")
    else:
        print(f"用户ID={user_id}不存在")
        
    # 列出所有用户
    print("\n所有用户列表:")
    users = User.query.all()
    for u in users:
        orders_count = Order.query.filter_by(user_id=u.id).count()
        print(f"ID: {u.id}, 用户名: {u.username}, 订单数: {orders_count}") 