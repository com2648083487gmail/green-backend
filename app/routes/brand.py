from flask import Blueprint, request, jsonify
from app import db
from flask_jwt_extended import jwt_required

bp = Blueprint('brand', __name__, url_prefix='/api/brand')

@bp.route('/info', methods=['GET'])
def get_brand_info():
    """获取品牌介绍信息"""
    # 模拟品牌数据，实际应该从数据库获取
    brand_info = {
        'title': '绿野鲜踪电商交易平台',
        'banner': 'http://localhost:8000/static/images/brand/brand_workshop.jpg',
        'content': """
        <p>绿野鲜踪电商平台的核心价值主张是"为消费者提供新鲜、安全、可溯源的绿色农产品，推动健康生活方式，助力乡村振兴"。</p>
        
        <h3>我们的价值主张</h3>
        <p><strong>健康与安全：</strong>提供无农残、绿色认证、产地直供的农产品，确保消费者“吃得放心，吃得安心”。</p>
        <p><strong>便捷的购物体验：</strong>平台为消费者提供轻松易用的线上农产品购物服务，支持多种支付方式与社区配送，覆盖用户日常所需。</p>
        <p><strong>个性化定制：</strong>提供个性化的“家庭菜篮子”搭配方案，按需组合每日所需食材，满足不同家庭的饮食习惯和口味偏好。</p>
        <p><strong>科普与认知提升：</strong>通过农产品百科、食材知识小卡片、食谱推荐等模块，帮助用户了解食材来源与营养，提升健康认知。</p>

        <h3>我们的服务</h3>
        <p><strong>绿色农产品的供应与采购：</strong>平台与各地农户、合作社建立长期合作关系，保障农产品品质、认证合规，推动可持续农业发展。</p>
        <p><strong>产品推荐与搭配：</strong>为用户推荐多样化搭配套餐，如应季果蔬组合、家庭食材包、健康营养搭配方案等，提升购物效率与科学性。</p>
        <p><strong>售后服务：</strong>提供从下单到送达的全流程服务支持，包含物流查询、售后反馈、新鲜保障等，确保用户体验无忧。</p>
        <p><strong>产地溯源与品质保障：</strong>为消费者展示每一件农产品的产地信息、种植过程、合作农户档案等，增强透明度与信任感。</p>
        """,
        'images': [
            'http://localhost:8000/static/images/brand/brand_logo.jpg',
            'http://localhost:8000/static/images/brand/brand_workshop.jpg',
            'http://localhost:8000/static/images/brand/brand_facility.jpg'
        ],
        'advantages': [
            {
                'title': '绿色健康食材',
                'icon': 'http://localhost:8000/static/images/icons/icon_leaf.png',
                'desc': '提供无农残、可追溯的农产品，确保消费者吃得健康、用得安心'
            },
            {
                'title': '便捷购物体验',
                'icon': 'http://localhost:8000/static/images/icons/icon_natural.png',
                'desc': '支持在线下单与配送到家，轻松获取每日所需新鲜农产品'
            },
            {
                'title': '个性化菜篮搭配',
                'icon': 'http://localhost:8000/static/images/icons/icon_recycle.png',
                'desc': '根据家庭成员结构与饮食偏好，提供智能化推荐搭配'
            },
            {
                'title': '科普内容赋能',
                'icon': 'http://localhost:8000/static/images/icons/icon_global.png',
                'desc': '通过食材小知识与农业科普内容，引导健康消费习惯'
            }
        ],
        'target_users': [
            {
                'title': '家庭用户',
                'desc': '关注食材安全与营养，追求高品质健康饮食，为家人选购安心农产品'
            },
            {
                'title': '社区用户',
                'desc': '希望通过平台实现一站式生鲜购物，享受高效配送服务'
            },
            {
                'title': '宝妈群体',
                'desc': '注重食材品质，为孩子提供营养均衡、无添加的新鲜食物'
            },
            {
                'title': '绿色消费倡导者',
                'desc': '倾向于选择产地明确、认证齐全的健康农产品，践行可持续生活方式'
            },
            {
                'title': '农产品供给方',
                'desc': '如农户、合作社等，关注品牌合作、公平交易和销售渠道拓展'
            }
        ]
    }

    
    return jsonify({
        'code': 200,
        'msg': '成功',
        'data': brand_info
    }) 