from flask_marshmallow import Marshmallow
from models import User, Product, Order, OrderItem, Comment, Category
from validators import validate_password, validate_phone

ma = Marshmallow()

class UserSchema(ma.SQLAlchemyAutoSchema):
    password = ma.String(load_only=True)

    class Meta:
        model = User
        load_instance = True
        include_fk = True
        

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True
        include_fk = True

class OrderItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = OrderItem
        load_instance = True
        include_fk = True

class OrderSchema(ma.SQLAlchemyAutoSchema):
    order_items = ma.Nested(OrderItemSchema, many=True)
    class Meta:
        model = Order
        load_instance = True
        include_fk = True

class CommentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Comment
        load_instance = True
        include_fk = True

class CategorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Category
        load_instance = True
        include_fk = True