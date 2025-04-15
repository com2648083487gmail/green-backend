# 环保家具电商平台 - 后端

这是环保家具电商平台的后端项目，使用Flask框架和SQLite数据库构建。

## 项目结构

```
Backend/
├── app/                    # 应用主目录
│   ├── models/             # 数据库模型
│   ├── routes/             # API路由
│   ├── static/             # 静态文件
│   ├── templates/          # 模板文件（如有）
│   ├── utils/              # 工具函数
│   └── __init__.py         # 应用初始化
├── instance/               # 实例文件夹（包含数据库）
├── venv/                   # 虚拟环境
├── run.py                  # 应用入口
└── README.md               # 项目说明
```

## 依赖项

- Flask
- Flask-CORS
- Flask-SQLAlchemy
- Flask-JWT-Extended

## 安装与运行

1. 创建并激活虚拟环境:

```bash
python3 -m venv venv
source venv/bin/activate  # 在Windows上使用: venv\Scripts\activate
```

2. 安装依赖:

```bash
pip install flask flask-cors flask-sqlalchemy flask-jwt-extended
```

3. 初始化数据库:

```bash
python -m app.utils.init_db
```

4. 运行应用:

```bash
python run.py
```

## API端点

### 认证

- POST `/api/auth/register` - 用户注册
- POST `/api/auth/login` - 用户登录
- GET `/api/auth/me` - 获取当前用户信息

### 用户

- GET `/api/user/profile` - 获取用户资料
- PUT `/api/user/profile` - 更新用户资料
- GET `/api/user/addresses` - 获取用户地址列表
- POST `/api/user/addresses` - 添加新地址
- PUT `/api/user/addresses/<id>` - 更新地址
- DELETE `/api/user/addresses/<id>` - 删除地址

### 产品

- GET `/api/products` - 获取产品列表
- GET `/api/products/<id>` - 获取单个产品详情
- POST `/api/products` - 添加新产品
- PUT `/api/products/<id>` - 更新产品
- DELETE `/api/products/<id>` - 删除产品

### 订单

- GET `/api/orders` - 获取订单列表
- GET `/api/orders/<id>` - 获取单个订单详情
- POST `/api/orders` - 创建新订单
- PUT `/api/orders/<id>/status` - 更新订单状态

## 测试数据

系统已预置以下测试账户：

- 管理员: 用户名 `admin`，密码 `admin123`
- 用户1: 用户名 `user1`，密码 `user123`
- 用户2: 用户名 `user2`，密码 `user123`

同时包含5种环保家具产品和示例订单数据。 