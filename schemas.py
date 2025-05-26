from flask_marshmallow import Marshmallow
from marshmallow import fields, validates, ValidationError
from models import User, Product, Order, OrderItem, Comment, Category
from validators import validate_password, validate_phone, validate_email


ma = Marshmallow()

class UserSchema(ma.SQLAlchemyAutoSchema):
    password = fields.String(load_only=True, validate=validate_password)
    email = fields.Email(validate=validate_email)
    class Meta:
        model = User
        load_instance = True
        include_fk = True
        

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True

    @validates('price')
    def validate_price(self, value):
        if value < 0:
            raise ValidationError("Price must be a positive number.")

    @validates('stock')
    def validate_stock(self, value):
        if value < 0:
            raise ValidationError("Stock must be a positive number.")

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