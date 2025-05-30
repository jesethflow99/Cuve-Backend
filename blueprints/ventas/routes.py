from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db,Order,OrderItem,Product
from schemas import OrderSchema,OrderItemSchema

ventas_bp = Blueprint("ventas", __name__)

#1. Crear una nueva orden

@ventas_bp.route('/orders', methods=['POST'])
@jwt_required()
def create_order():
    try:
        # Obtener el usuario actual
        user_id = get_jwt_identity()

        # Crear la nueva orden
        order = Order(user_id=user_id, status='pending')
        db.session.add(order)
        db.session.commit()

        order_schema = OrderSchema()
        return jsonify({"msg": "Order created successfully", "order": order_schema.dump(order)}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error creating order", "error": str(e)}), 500


#2. Obtener todas las órdenes

@ventas_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    orders = Order.query.all()
    order_schema = OrderSchema(many=True)
    return jsonify(order_schema.dump(orders)), 200

#3. Obtener una orden específica  
 
@ventas_bp.route('/orders/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"msg": "Order not found"}), 404

    order_schema = OrderSchema()
    return jsonify(order_schema.dump(order)), 200
  
  
#4. Actualizar el estado de una orden

@ventas_bp.route('/orders/<int:order_id>', methods=['PATCH'])
@jwt_required()
def update_order(order_id):
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({"msg": "Order not found"}), 404

        # Obtener los datos del cuerpo de la solicitud
        data = request.get_json()
        status = data.get('status')

        # Validar el estado
        if status:
            order.status = status

        db.session.commit()

        order_schema = OrderSchema()
        return jsonify({"msg": "Order updated successfully", "order": order_schema.dump(order)}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error updating order", "error": str(e)}), 500

#5. Eliminar una orden

 
@ventas_bp.route('/orders/<int:order_id>', methods=['DELETE'])
@jwt_required()
def delete_order(order_id):
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({"msg": "Order not found"}), 404

        db.session.delete(order)
        db.session.commit()
        return jsonify({"msg": "Order deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error deleting order", "error": str(e)}), 500
      
#6. Agregar un ítem a una orden


@ventas_bp.route('/orders/<int:order_id>/items', methods=['POST'])
@jwt_required()
def add_order_item(order_id):
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({"msg": "Order not found"}), 404

        # Obtener los datos del cuerpo de la solicitud
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity')

        # Validar los datos
        if not product_id or not quantity or quantity <= 0:
            return jsonify({"msg": "Invalid product or quantity"}), 400

        # Verificar si el producto existe
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"msg": "Product not found"}), 404

        # Crear el ítem de la orden
        order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=quantity)
        db.session.add(order_item)
        db.session.commit()

        order_item_schema = OrderItemSchema()
        return jsonify({"msg": "Order item added successfully", "order_item": order_item_schema.dump(order_item)}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error adding order item", "error": str(e)}), 500

#7. Eliminar un ítem de una orden

      
@ventas_bp.route('/orders/<int:order_id>/items/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_order_item(order_id, item_id):
    try:
        order_item = OrderItem.query.filter_by(order_id=order_id, id=item_id).first()
        if not order_item:
            return jsonify({"msg": "Order item not found"}), 404

        db.session.delete(order_item)
        db.session.commit()
        return jsonify({"msg": "Order item deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error deleting order item", "error": str(e)}), 500
      
blueprint = ventas_bp