from app import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 环保属性
    eco_friendly = db.Column(db.Boolean, default=False)
    eco_labels = db.Column(db.String(200), nullable=True)
    material = db.Column(db.String(100), nullable=True)
    carbon_footprint = db.Column(db.Float, nullable=True)

    # 关联
    images = db.relationship('ProductImage', back_populates='product', lazy=True, cascade="all, delete-orphan")
    order_items = db.relationship('OrderItem', back_populates='product', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'stock': self.stock,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'eco_friendly': self.eco_friendly,
            'eco_labels': self.eco_labels.split(',') if self.eco_labels else [],
            'material': self.material,
            'carbon_footprint': self.carbon_footprint,
            'images': [img.url for img in self.images]
        }

class ProductImage(db.Model):
    __tablename__ = 'product_images'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)

    product = db.relationship('Product', back_populates='images')  # ✅ 添加此行保持一致

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'url': self.url,
            'is_primary': self.is_primary
        }
