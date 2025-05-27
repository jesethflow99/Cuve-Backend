from flask import Blueprint, request, jsonify, redirect, url_for
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from schemas import UserSchema
from models import db, User,Roles
from logger import setup_logger
from marshmallow import ValidationError

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
    email = data.get('email')
    password = data.get('password')
    try:

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            logger.error("Invalid email or password")
            # logger.error(f"Invalid email or password for user: {email}")
            return jsonify({"msg": "Nombre o contraseña incorrectos"}), 401
        
        if not user.is_active:
            logger.error("User account is inactive")
            
            return jsonify({"msg": "User account is inactive, contact to admin for activate"}), 403

        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token)
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return jsonify({"msg": "Error during login"}), 500
    


@auth_bp.route('/update', methods=['PATCH'])
@jwt_required()
def update_user():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    user_id = data.get('id', current_user_id)  # Si no se pasa user_id, se usa el propio

    user = db.session.get(User, user_id)


    if not user:
        logger.error("User not found")
        return jsonify({"msg": "User not found"}), 404

    current_user = db.session.get(User, current_user_id)
    # Solo admin puede modificar a otros usuarios
    if str(user.id) != str(current_user_id) and current_user.role != Roles.ADMIN:
        logger.error("Permission denied")
        return jsonify({"msg": "Permission denied"}), 403
    
    #ningun usuario puede moficicar ni el id ni el rol
    if 'role' in data and current_user.role != Roles.ADMIN:
        logger.error("Permission denied to change role")
        return jsonify({"msg": "Permission denied to change role"}), 403
    if 'id' in data:
        logger.error("Permission denied to change id")
        return jsonify({"msg": "Permission denied to change id"}), 403
    
    #if is active is disabled, redirect to method logout
    if 'is_active' in data and not data['is_active']:
        user.is_active = False
        db.session.commit()
        logger.info(f"User {user.username} deactivated their account")
        
        # Invalidar el token actual (si usas un sistema de blacklist)
        jti = get_jwt_identity()  # Obtener el identificador del token actual
        
        
        # Aquí podrías agregar el jti a una blacklist si tienes un sistema implementado
        
        
        return jsonify({"msg": "Account deactivated. You have been logged out."}), 200

    

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



@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    print(current_user_id)
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


blueprint = auth_bp