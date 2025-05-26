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
            phone="+556321547868",
            address="av.state 532",
            role=Roles.ADMIN
        )
        db.session.add(user)
        db.session.commit()
        print(User.query.all())
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


def test_get_user(client,access_token):
  response = client.get("/admin/get_user/1",headers={"Authorization":f"Bearer {access_token}"})
  assert response.status_code == 200
  assert response.get_json()
  
def test_get_all_users(client,access_token):
  response = client.get("/admin/get_all_users",headers={"Authorization":f"Bearer {access_token}"})
  assert response.status_code == 200
  assert response.get_json()
  

def test_delete(client,access_token):
  client.post('/auth/register', json={
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "Password123",
        "phone": "+352123456789",
        "address":"av.state 532"
    })
  response = client.delete("/admin/delete/2",headers={"Authorization":f"Bearer {access_token}"})
  assert response.status_code == 200
  assert response.get_json()
  

