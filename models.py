from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

class Roles():
    USER = os.getenv('USER_ROLE')
    ADMIN = os.getenv('ADMIN_ROLE')
    SELLER = os.getenv('SELLER_ROLE')

class ModelBase(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
class User(ModelBase):
    __tablename__ = 'users'
    
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String, default=Roles.USER)
    
class Product(ModelBase):
    __tablename__ = 'products'
    
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    category = db.relationship('Category', backref=db.backref('products', lazy=True))

class OrderItem(ModelBase):
    __tablename__ = 'order_items'
    
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    
    order = db.relationship('Order', backref=db.backref('order_items', lazy='joined'))
    product = db.relationship('Product', backref=db.backref('order_items', lazy='joined'))
    
class Order(ModelBase):
    __tablename__ = 'orders'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')
    
    user = db.relationship('User', backref=db.backref('orders', lazy=True))
    
class Comment(ModelBase):
    __tablename__ = 'comments'
    
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    stars = db.Column(db.Integer, nullable=False)  # no "starts"
    
    product = db.relationship('Product', backref=db.backref('comments', lazy=True))
    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    
class Category(ModelBase):
    __tablename__ = 'categories'

    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
