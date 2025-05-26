from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from models import Product, db,Order,OrderItem
from schemas import ProductSchema
from flask_jwt_extended import get_jwt_identity

product_bp = Blueprint('products', __name__)


def has_role(required_roles):
    user_roles = get_jwt_identity().get('roles', [])
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

# Create a new product
@product_bp.route('/products', methods=['POST'])
@jwt_required()
def create_product():
  # if is admin or seller
  if not has_role(['admin', 'seller']):
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
  
# Update an existing product
@product_bp.route('/products/<int:product_id>', methods=['PATCH'])
@jwt_required()
def update_product(product_id):
  
  if not has_role(['admin', 'seller']):
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
@product_bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
  
  if not any(role in ['admin', 'seller'] for role in get_jwt_identity().get('roles', [])):
    return jsonify({"msg": "Access forbidden"}), 403
  
  product = Product.query.get_or_404(product_id)
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
    
    
blueprint = product_bp  