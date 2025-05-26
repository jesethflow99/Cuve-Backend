import pytest
from flask_jwt_extended import create_access_token
from models import db, User, Roles
from werkzeug.security import generate_password_hash, check_password_hash
from app import create_app
from config import get_config
import os

os.environ['APP_ENV'] = 'testing'

@pytest.fixture
def app():
    """Crea una instancia de la aplicación para pruebas."""
    app = create_app()
    
    app.config.from_object(get_config())
    with app.app_context():
        db.create_all()
        # Crear un usuario de prueba
        
        user = User(
            username="testuser",
            email="testuser@example.com",
            password=generate_password_hash("Hashedpassword123"),
            phone="+556231254876",
            address="av.state 532"
        )
        db.session.add(user)
        db.session.commit()
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Crea un cliente de pruebas."""
    return app.test_client()

@pytest.fixture
def access_token(app):
    """Genera un token de acceso para el usuario de prueba."""
    with app.app_context():
        user = User.query.filter_by(email="testuser@example.com").first()
        return create_access_token(identity=str(user.id))

def test_register(client):
    response = client.post('/auth/register', json={
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "Password123",
        "phone": "+2123456789",
        "address":"av.state 532"
    })

    assert response.status_code == 201
    assert "email" in response.get_json()

def test_login(client):
    response = client.post('/auth/login', json={
        "email": "testuser@example.com",
        "password": "Hashedpassword123"
    })
    assert response.status_code == 200
    assert "access_token" in response.get_json()

def test_login_inactive_user(client, app):
    with app.app_context():
        user = User.query.filter_by(email="testuser@example.com").first()
        user.is_active = False
        db.session.commit()

    response = client.post('/auth/login', json={
        "email": "testuser@example.com",
        "password": "Hashedpassword123"
    })
    assert response.status_code == 403
    assert response.get_json()["msg"] == "User account is inactive, contact to admin for activate"

def test_update_user(client, access_token):
    response = client.patch('/auth/update', json={
        "username": "updateduser"
    }, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.get_json()["username"] == "updateduser"

def test_update_user_deactivate_account(client, access_token):
    response = client.patch('/auth/update', json={
        "is_active": False
    }, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.get_json()["msg"] == "Account deactivated. You have been logged out."

def test_get_current_user(client, access_token):
    response = client.get('/auth/me', headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.get_json()["email"] == "testuser@example.com"

def test_logout(client, access_token):
    response = client.post('/auth/logout', headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.get_json()["msg"] == "Successfully logged out"