from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from models import Product, db,Order,OrderItem,User,Roles, Category
from schemas import ProductSchema,OrderItemSchema
from flask_jwt_extended import get_jwt_identity


product_bp = Blueprint('products', __name__)


def has_role(required_roles):
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    if not user:
        return False
    user_roles = user.role if isinstance(user.role, list) else [user.role]
    
    return any(role in required_roles for role in user_roles)

# Endpoint test
@product_bp.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "Test endpoint products"}), 200
  
#get products
@product_bp.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    products = Product.query.all()
    product_schema = ProductSchema(many=True)
    return jsonify(product_schema.dump(products)), 200
  
@product_bp.route('/products/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    product_schema = ProductSchema()
    return jsonify(product_schema.dump(product)), 200

#get products by category
@product_bp.route('/categories/<int:category>', methods=['GET'])
@jwt_required()
def get_products_by_category(category):
    products = Product.query.filter_by(category_id=category).all()
    product_schema = ProductSchema(many=True)
    
    if not products:
        return []
    
    return jsonify(product_schema.dump(products)), 200
  
# get orders by user as cart
@product_bp.route('/orders/<int:id_user>', methods=['GET'])
@jwt_required()
def get_orders_by_user(id_user):
    order = Order.query.filter_by(user_id=id_user).first()
    if not order:
        return []
    order_items = OrderItem.query.filter_by(order_id=order.id).all()
    order_item_schema = OrderItemSchema(many=True)
    return jsonify({
        "order_id": order.id,
        "user_id": order.user_id,
        "items": order_item_schema.dump(order_items)
    }), 200
    

# Create a new product
@product_bp.route('/products', methods=['POST'])
@jwt_required()
def create_product():
  # if is admin or seller
  try:
    if not has_role([Roles.ADMIN, Roles.SELLER]):
      return jsonify({"msg": "Access forbidden"}), 403
    
    product_schema = ProductSchema()
    data = request.get_json()

    errors = product_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    product = product_schema.load(data)
    db.session.add(product)
    db.session.commit()

    return jsonify(product_schema.dump(product)), 201
  except Exception as e:
    db.session.rollback()
    
    return jsonify({"msg": "Error creating product", "error": str(e)}), 500
  
# Update an existing product
@product_bp.route('/<int:product_id>', methods=['PATCH'])
@jwt_required()
def update_product(product_id):
  
  if not has_role([Roles.ADMIN, Roles.SELLER]):
    return jsonify({"msg": "Access forbidden"}), 403
  
  product = Product.query.get_or_404(product_id)
  product_schema = ProductSchema(partial=True)
  data = request.get_json()

  errors = product_schema.validate(data, partial=True)
  if errors:
      return jsonify(errors), 400

  product = product_schema.load(data, instance=product, partial=True)
  db.session.commit()

  return jsonify(product_schema.dump(product)), 200

# Delete a product
@product_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
  
  if not has_role([Roles.ADMIN, Roles.SELLER]):
    return jsonify({"msg": "Access forbidden"}), 403
  
  product = db.session.get(Product,product_id)
  db.session.delete(product)
  db.session.commit()

  return jsonify({"msg": "Product deleted successfully"}), 200


#create order

@product_bp.route("/add_item",methods=["DELETE"])
@jwt_required()
def  add_order():
  
    #get data
    data = request.get_json()

    product_id = data.get("product_id")
    quantity = data.get("quantity")

    #validators
    if not product_id or not quantity:
      return jsonify({"msg": "Product ID and quantity are required"}), 400

    product = Product.query.get(product_id)
    if not product:
      return jsonify({"msg": "Product not found"}), 404

    if product.stock < quantity:
      return jsonify({"msg": "Insufficient stock"}), 400
    
    if not isinstance(quantity, int) or quantity <= 0:
      return jsonify({"msg": "Quantity must be a positive integer"}), 400

    #execute
    order = Order(user_id=get_jwt_identity().get("id"))
    db.session.add(order)
    db.session.flush()  # Flush to get the order ID

    order_item = OrderItem(order_id=order.id, product_id=product_id, quantity=quantity)
    db.session.add(order_item)

    product.stock -= quantity
    db.session.commit()

    return jsonify({"msg": "Order created successfully", "order_id": order.id}), 201
  
@product_bp.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    # Verificar si el usuario tiene el rol adecuado
    if not has_role([Roles.ADMIN]):
        return jsonify({"msg": "Access forbidden"}), 403

    # Obtener los datos del cuerpo de la solicitud
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    # Validar los datos
    if not name:
        return jsonify({"msg": "Category name is required"}), 400

    # Verificar si ya existe una categoría con el mismo nombre
    if Category.query.filter_by(name=name).first():
        return jsonify({"msg": "Category with this name already exists"}), 400

    # Crear la nueva categoría
    category = Category(name=name, description=description)
    db.session.add(category)
    db.session.commit()

    return jsonify({"msg": "Category created successfully", "category": {"id": category.id, "name": category.name, "description": category.description}}), 201
    
@product_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    categories = Category.query.all()
    return jsonify([{"id": category.id, "name": category.name, "description": category.description} for category in categories]), 200


@product_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    # Verificar si el usuario tiene el rol adecuado
    if not has_role([Roles.ADMIN]):
        return jsonify({"msg": "Access forbidden"}), 403

    # Buscar la categoría
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"msg": "Category not found"}), 404

    try:
        # Eliminar la categoría
        db.session.delete(category)
        db.session.commit()
        return jsonify({"msg": "Category deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error deleting category", "error": str(e)}), 500


blueprint = product_bp  