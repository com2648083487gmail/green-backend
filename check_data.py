from app import create_app, db
from app.models.user import User, Address
from app.models.product import Product
from app.models.order import Order

def check_data():
    app = create_app()
    with app.app_context():
        users = User.query.all()
        addresses = Address.query.all()
        products = Product.query.all()
        orders = Order.query.all()
        
        print(f"数据库中已有:")
        print(f"- 用户数: {len(users)}")
        print(f"- 地址数: {len(addresses)}")
        print(f"- 产品数: {len(products)}")
        print(f"- 订单数: {len(orders)}")
        
        if users:
            print("\n用户信息:")
            for user in users[:3]:  # 只显示前3个用户
                print(f"  ID: {user.id}, 用户名: {user.username}, 邮箱: {user.email}")
                
        if addresses:
            print("\n地址信息:")
            for addr in addresses[:3]:  # 只显示前3个地址
                print(f"  ID: {addr.id}, 用户ID: {addr.user_id}, 收件人: {addr.name}, 地址: {addr.province}{addr.city}{addr.district}{addr.detail}")
        
        if products:
            print("\n产品信息:")
            for product in products[:3]:  # 只显示前3个产品
                print(f"  ID: {product.id}, 名称: {product.name}, 价格: {product.price}, 库存: {product.stock}")
        
        if orders:
            print("\n订单信息:")
            for order in orders[:3]:  # 只显示前3个订单
                print(f"  ID: {order.id}, 用户ID: {order.user_id}, 订单号: {order.order_number}, 状态: {order.status}, 金额: {order.total_amount}")

if __name__ == "__main__":
    check_data() 