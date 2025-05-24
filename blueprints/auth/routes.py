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

    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token)

@auth_bp.route('/update', methods=['PATCH'])
@jwt_required()
def update_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        logger.error("User not found")
        return jsonify({"msg": "User not found"}), 404
    
    if user.role != Roles.ADMIN:
        logger.error("Permission denied")
        return jsonify({"msg": "Permission denied"}), 403

    user_schema = UserSchema(partial=True)
    data = request.get_json()

    errors = user_schema.validate(data)
    if errors:
        logger.error(f"Validation errors: {errors}")
        return jsonify(errors), 400

    for key, value in data.items():
        if hasattr(user, key):
            if key == 'password':
                value = generate_password_hash(value)
        setattr(user, key, value)

    db.session.commit()
    logger.info(f"User {user.username} updated successfully")
    return jsonify(user_schema.dump(user)), 200

@auth_bp.route('/delete', methods=['DELETE'])
@jwt_required()
def delete_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        logger.error("User not found")
        return jsonify({"msg": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    logger.info(f"User {user.username} deleted successfully")
    return jsonify({"msg": "User deleted"}), 200

blueprint = auth_bp
