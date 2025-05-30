from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
from models import User, Product, Order, OrderItem, Comment, Category,Roles
from validators import validate_password, validate_phone, validate_email,validate_price, validate_stock


ma = Marshmallow()

class UserSchema(ma.SQLAlchemyAutoSchema):
    password = fields.String(load_only=True, validate=validate_password)
    email = fields.Email(validate=validate_email)
    phone = fields.String(validate=validate_phone)
    role = fields.Method("get_role_name")  # Campo personalizado para transformar el rol

    class Meta:
        model = User
        load_instance = True
        include_fk = True

    def get_role_name(self, obj):
        # Diccionario de mapeo de claves a nombres legibles
        role_mapping = {
            Roles.USER: "user",
            Roles.ADMIN: "admin",
            Roles.SELLER: "seller"
        }
        # Devuelve el nombre legible o la clave si no está en el mapeo
        return role_mapping.get(obj.role, obj.role)
        

class ProductSchema(ma.SQLAlchemyAutoSchema):
    price = fields.Float(required=True, validate=validate_price) 
    stock = fields.Integer(required=True, validate=validate_stock)
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