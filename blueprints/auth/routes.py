from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from schemas import UserSchema
from models import db, User,Roles
from logger import setup_logger

auth_bp = Blueprint('auth', __name__)

logger = setup_logger(__name__)
#endpoint test
@auth_bp.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "Test endpoint auth"}), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    user_schema = UserSchema()
    data = request.get_json()

    errors = user_schema.validate(data)
    if errors:
        logger.error(f"Validation errors: {errors}")
        return jsonify(errors), 400

    # Hashear la contraseña antes de cargar el modelo
    data['password'] = generate_password_hash(data['password'])

    user = user_schema.load(data)

    db.session.add(user)
    db.session.commit()

    return jsonify(user_schema.dump(user)), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        logger.error("Invalid username or password")
        # logger.error(f"Invalid username or password for user: {username}")
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify(access_token=access_token)

@auth_bp.route('/update', methods=['PATCH'])
@jwt_required()
def update_user():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    user_id = data.get('id', current_user_id)  # Si no se pasa user_id, se usa el propio

    user = User.query.get(user_id)
    if not user:
        logger.error("User not found")
        return jsonify({"msg": "User not found"}), 404

    current_user = User.query.get(current_user_id)
    # Solo admin puede modificar a otros usuarios
    if str(user.id) != str(current_user_id) and current_user.role != Roles.ADMIN:
        logger.error("Permission denied")
        return jsonify({"msg": "Permission denied"}), 403
    #no se puede modificar el rol de admin con id 1
    if user.role == Roles.ADMIN and str(user.id) == '1':
        logger.error("Cannot modify admin user")
        return jsonify({"msg": "Cannot modify admin user"}), 403

    user_schema = UserSchema(partial=True)
    errors = user_schema.validate(data)
    if errors:
        logger.error(f"Validation errors: {errors}")
        return jsonify(errors), 400

    for key, value in data.items():
        if hasattr(user, key):
            if key == 'id':
                continue  # Nunca permitir actualizar el id
            if key == 'password':
                value = generate_password_hash(value)
            setattr(user, key, value)

    db.session.commit()
    logger.info(f"User {user.username} updated successfully")
    return jsonify(user_schema.dump(user)), 200

@auth_bp.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    # Solo admin puede eliminar a otros usuarios
    if str(user.id) != str(user_id) and user.role != Roles.ADMIN:
        logger.error("Permission denied")
        return jsonify({"msg": "Permission denied"}), 403
    
    user = User.query.get(id)
    if not user:
        logger.error("User not found")
        return jsonify({"msg": "User not found"}), 404 
    if user.role == Roles.ADMIN:
        logger.error("Cannot delete admin user")
        return jsonify({"msg": "Cannot delete admin user"}), 403 

    # Eliminar el usuario
    db.session.delete(user)
    db.session.commit()
    logger.info(f"User {user.username} deleted successfully")
    return jsonify({"msg": "User deleted"}), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        logger.error("User not found")
        return jsonify({"msg": "User not found"}), 404

    user_schema = UserSchema()
    return jsonify(user_schema.dump(user)), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # Invalidate the token (this is a placeholder, actual implementation may vary)
    jti = get_jwt_identity()
    # Here you would typically add the jti to a blacklist
    return jsonify({"msg": "Successfully logged out"}), 200

@auth_bp.route('/get_user/<int:id>', methods=['GET'])
@jwt_required()
def get_user(id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    # Solo admin puede ver a otros usuarios
    if str(user.id) != str(current_user_id) and user.role != Roles.ADMIN:
        logger.error("Permission denied")
        return jsonify({"msg": "Permission denied"}), 403

    user = User.query.get(id)
    if not user:
        logger.error("User not found")
        return jsonify({"msg": "User not found"}), 404

    user_schema = UserSchema()
    return jsonify(user_schema.dump(user)), 200

@auth_bp.route('/get_all_users', methods=['GET'])
@jwt_required()
def get_all_users():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    # Solo admin puede ver a otros usuarios
    if str(user.id) != str(current_user_id) and user.role != Roles.ADMIN:
        logger.error("Permission denied")
        return jsonify({"msg": "Permission denied"}), 403

    users = User.query.all()
    user_schema = UserSchema(many=True)
    return jsonify(user_schema.dump(users)), 200

blueprint = auth_bp
