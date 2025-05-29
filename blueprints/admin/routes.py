from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User
from schemas import UserSchema
from models import Roles
from logger import setup_logger
from flask_jwt_extended import get_jwt_identity
from flask import abort
from functools import wraps



admin_bp = Blueprint('admin', __name__)

logger = setup_logger(__name__)
def has_role(required_roles):
    identity = get_jwt_identity()
    user = db.session.get(User,identity)
    return user and user.role in required_roles
  
#asign roles to user
def role_required(required_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not has_role(required_roles):
                logger.error(f"Access forbidden for roles: {required_roles}")
                return jsonify({"msg": "Access forbidden"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
  
@admin_bp.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "Test endpoint users"}), 200
  
@admin_bp.route('/get_user/<int:id>', methods=['GET'])
@jwt_required()
@role_required(Roles.ADMIN)
def get_user(id):
    current_user_id = get_jwt_identity()
    user = db.session.get(User,current_user_id)
    user = db.session.get(User,id)
    if not user:
        logger.error("User not found")
        return jsonify({"msg": "User not found"}), 404

    user_schema = UserSchema()
    return jsonify(user_schema.dump(user)), 200

@admin_bp.route('/get_all_users', methods=['GET'])
@jwt_required()
@role_required(Roles.ADMIN)
def get_all_users():
    current_user_id = get_jwt_identity()
    user = db.session.get(User,current_user_id)


    users = User.query.all()
    user_schema = UserSchema(many=True)
    return jsonify(user_schema.dump(users)), 200
  
@admin_bp.route('/change_role/<int:id>', methods=['PATCH'])
@jwt_required()
@role_required(Roles.ADMIN)
def change_user_role(id):
    current_user_id = get_jwt_identity()
    user = db.session.get(User, id)

    if not user:
        logger.error("User not found")
        return jsonify({"msg": "User not found"}), 404

    # Proteger al superadministrador
    if user.id == 1:
        logger.error("Cannot change the role of the superadmin user")
        return jsonify({"msg": "Cannot change the role of the superadmin user"}), 403

    data = request.get_json()
    new_role = data.get('role')
    if new_role == "admin":
        new_role = Roles.ADMIN
    elif new_role == "seller":
        new_role = Roles.SELLER
    else:
        new_role = Roles.USER
    # Validar que el nuevo rol sea válido
    valid_roles = [Roles.USER, Roles.ADMIN, Roles.SELLER]
    if new_role not in valid_roles:
        logger.error(f"Invalid role: {new_role}")
        return jsonify({"msg": f"Invalid role. Valid roles are: {valid_roles}"}), 400

    # Cambiar el rol del usuario
    user.role = new_role
    db.session.commit()
    logger.info(f"User {user.username} role changed to {new_role} by admin {current_user_id}")
    return jsonify({"msg": f"User role updated to {new_role}"}), 200


@admin_bp.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
@role_required(Roles.ADMIN)
def delete_user(id):
    user_id = get_jwt_identity()
    user = db.session.get(User,user_id)
    
    user = db.session.get(User,id)
    if not user:
        logger.error("User not found")
        return jsonify({"msg": "User not found"}), 404 
      
    if user.id == 1:
      logger.error("Cannot delete the superadmin user")
      return jsonify({"msg": "Cannot delete the superadmin user"}), 403

    # Eliminar el usuario
    db.session.delete(user)
    db.session.commit()
    logger.info(f"User {user.username} deleted successfully")
    return jsonify({"msg": "User deleted"}), 200
  
blueprint = admin_bp