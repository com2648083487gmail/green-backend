from flask import Blueprint, jsonify
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app import db
from datetime import datetime, timedelta
import random  # 用于生成模拟数据

bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@bp.route('/stats', methods=['GET'])
def get_stats():
    """获取仪表盘统计数据"""
    try:
        # 查询待处理订单数量
        try:
            pending_orders = Order.query.filter_by(status='pending').count()
        except Exception as e:
            print(f"查询待处理订单数量失败: {str(e)}")
            pending_orders = 0
        
        # 查询今日收入
        try:
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_orders = Order.query.filter(
                Order.created_at >= today,
                Order.status != 'canceled'  # 排除已取消的订单
            ).all()
            
            today_income = sum(order.total_amount for order in today_orders if order.total_amount is not None)
        except Exception as e:
            print(f"查询今日收入失败: {str(e)}")
            today_income = 0
        
        # 查询产品总数
        try:
            total_products = Product.query.count()
        except Exception as e:
            print(f"查询产品总数失败: {str(e)}")
            total_products = 0
        
        # 查询用户总数
        try:
            total_users = User.query.count()
        except Exception as e:
            print(f"查询用户总数失败: {str(e)}")
            total_users = 0
        
        return jsonify({
            'code': 200,
            'msg': '成功',
            'data': {
                'pendingOrders': pending_orders,
                'todayIncome': float(today_income),
                'totalProducts': total_products,
                'totalUsers': total_users
            }
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"获取统计数据失败: {str(e)}")
        print(f"错误详情: {error_details}")
        return jsonify({
            'code': 500,
            'msg': f'获取统计数据失败: {str(e)}'
        }), 500

@bp.route('/recent-orders', methods=['GET'])
def get_recent_orders():
    """获取最近订单"""
    try:
        # 查询最近5个订单
        recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
        
        # 格式化订单数据
        orders_data = []
        for order in recent_orders:
            # 获取用户信息
            username = f"用户 #{order.user_id}"
            try:
                user = User.query.get(order.user_id)
                if user and user.username:
                    username = user.username
            except Exception as e:
                print(f"获取用户信息失败: {str(e)}")
            
            # 获取订单信息
            order_data = {
                'id': order.id,
                'order_number': order.order_number,
                'user_name': username,
                'total_amount': float(order.total_amount) if order.total_amount is not None else 0,
                'status': order.status,
                'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S') if order.created_at else ""
            }
            orders_data.append(order_data)
        
        return jsonify({
            'code': 200,
            'msg': '成功',
            'data': orders_data
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"获取最近订单失败: {str(e)}")
        print(f"错误详情: {error_details}")
        return jsonify({
            'code': 500,
            'msg': f'获取最近订单失败: {str(e)}'
        }), 500

@bp.route('/eco-stats', methods=['GET'])
def get_eco_stats():
    """获取环保统计数据"""
    try:
        # 查询环保产品信息
        eco_products = Product.query.filter_by(eco_friendly=True).all()
        eco_product_count = len(eco_products)
        
        # 根据环保产品的实际碳足迹计算碳减排量
        carbon_reduction = 0
        for product in eco_products:
            if product.carbon_footprint is not None:
                try:
                    carbon_reduction += float(product.carbon_footprint)
                except (ValueError, TypeError):
                    pass
        
        # 如果没有碳足迹数据，使用基于环保产品数量的估算
        if carbon_reduction == 0:
            carbon_reduction = eco_product_count * 100  # 每个环保产品估算减少100kg碳排放
            
        # 计算树木数量（基于碳减排量，平均一棵树每年吸收25kg CO2）
        trees = int(carbon_reduction / 25)
        if trees == 0 and eco_product_count > 0:
            trees = eco_product_count * 2  # 至少有一些树
            
        # 计算回收材料使用量（基于环保产品数量）
        recycled_materials = eco_product_count * 50  # 每产品估算50kg回收材料
        
        return jsonify({
            'code': 200,
            'msg': '成功',
            'data': {
                'trees': trees,
                'recycledMaterials': int(recycled_materials),
                'carbonReduction': int(carbon_reduction)
            }
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"获取环保统计数据失败: {str(e)}")
        print(f"错误详情: {error_details}")
        return jsonify({
            'code': 500,
            'msg': f'获取环保统计数据失败: {str(e)}'
        }), 500 