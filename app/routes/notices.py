from flask import Blueprint, request, jsonify
import datetime

bp = Blueprint('notices', __name__, url_prefix='/api/notices')

# 模拟数据：公告列表
mock_notices = [
    {
        'notice_id': 1,
        'title': '关于绿野鲜踪平台上线发布会的通知',
        'content': '我们将于下月10日举办绿野鲜踪电商平台上线发布会，正式推出以原生态农产品为核心的电商交易服务。发布会将通过线上直播方式进行，欢迎广大用户观看参与。',
        'content_summary': '我们将于下月10日举办绿野鲜踪电商平台上线发布会...',
        'create_time': '2025-03-15 10:30:00'
    },
    {
        'notice_id': 2,
        'title': '平台系统升级维护公告',
        'content': '为了提供更流畅的购物体验，绿野鲜踪平台将于本周末进行系统升级维护，预计维护时长约6小时。期间部分功能可能受限，敬请谅解与支持。',
        'content_summary': '为了提供更流畅的购物体验，绿野鲜踪平台将于本周末进行系统升级维护...',
        'create_time': '2025-03-12 14:15:00'
    },
    {
        'notice_id': 3,
        'title': '关于农产品溯源认证的重要说明',
        'content': '绿野鲜踪平台上架的主要农产品已通过产地认证与无公害检测，平台支持产品溯源功能，用户可查看产地信息与农户档案，保障每一份食材来源真实可查。',
        'content_summary': '绿野鲜踪平台上架的主要农产品已通过产地认证与无公害检测...',
        'create_time': '2025-03-08 09:45:00'
    },
    {
        'notice_id': 4,
        'title': '绿野鲜踪夏季促销活动开启',
        'content': '绿野鲜踪夏季促销活动正式开启，全场应季蔬果限时折扣，精选高原土豆、爆甜沃柑等产品参与秒杀抢购。活动时间：8月1日至8月15日，先到先得！',
        'content_summary': '绿野鲜踪夏季促销活动正式开启，全场应季蔬果限时折扣...',
        'create_time': '2025-03-01 08:00:00'
    },
    {
        'notice_id': 5,
        'title': '新增社区菜篮子配送服务',
        'content': '为更好服务社区用户，绿野鲜踪平台新增“菜篮子”定制配送服务。用户可在线选择每日新鲜蔬果套餐，我们将由农户直发至社区，保障食材新鲜、安全、实惠。',
        'content_summary': '绿野鲜踪平台新增“菜篮子”定制配送服务，支持每日送达...',
        'create_time': '2025-03-25 16:20:00'
    }
]

@bp.route('/list', methods=['GET'])
def get_notices_list():
    """获取公告列表"""
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))
    
    # 计算分页
    start = (page - 1) * size
    end = start + size
    
    notices = mock_notices[start:end]
    total = len(mock_notices)
    
    # 转换为响应格式
    result = []
    for notice in notices:
        result.append({
            'notice_id': notice['notice_id'],
            'title': notice['title'],
            'content': notice['content_summary'],
            'create_time': notice['create_time']
        })
    
    return jsonify({
        'code': 200,
        'msg': '成功',
        'data': {
            'list': result,
            'total': total
        }
    })

@bp.route('/detail', methods=['GET'])
def get_notice_detail():
    """获取公告详情"""
    notice_id = int(request.args.get('notice_id', 0))
    
    # 查找对应ID的公告
    notice = None
    for n in mock_notices:
        if n['notice_id'] == notice_id:
            notice = n
            break
    
    if not notice:
        return jsonify({
            'code': 404,
            'msg': '公告不存在'
        }), 404
    
    return jsonify({
        'code': 200,
        'msg': '成功',
        'data': {
            'notice_id': notice['notice_id'],
            'title': notice['title'],
            'content': notice['content'],
            'create_time': notice['create_time']
        }
    })

# 管理接口
@bp.route('', methods=['POST'])
def create_notice():
    # 实际应用中，这里应该将公告保存到数据库
    # 这里只是一个示例
    data = request.get_json()
    
    if not all(k in data for k in ('title', 'content')):
        return jsonify({'code': 400, 'msg': '缺少必要字段'}), 400
    
    new_notice = {
        'notice_id': len(mock_notices) + 1,
        'title': data['title'],
        'content': data['content'],
        'content_summary': data['content'][:50] + '...',
        'create_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # 在实际应用中，应该将新公告保存到数据库
    # 这里我们只是将它添加到模拟数据中
    mock_notices.append(new_notice)
    
    return jsonify({
        'code': 200,
        'msg': '公告创建成功',
        'data': {
            'notice_id': new_notice['notice_id']
        }
    }), 201 