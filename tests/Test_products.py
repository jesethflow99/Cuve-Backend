import pytest
from flask_jwt_extended import create_access_token
from models import db, User, Product, Order, OrderItem, Category, Comment, Roles
from werkzeug.security import generate_password_hash
from app import create_app
import os
from datetime import datetime
from config import get_config

os.environ['APP_ENV'] = 'testing'
@pytest.fixture
def app():
    """Crea una instancia de la aplicación para pruebas."""
    app = create_app()
    app.config.from_object(get_config())
    with app.app_context():
        db.create_all()
        # Crear un usuario de prueba
        category = Category(name="Electronics", description="Electronic devices")
        db.session.add(category)
        
        user = User(
            username="testuser",
            email="testuser@example.com",
            password=generate_password_hash("Hashedpassword123"),
            phone="12343453",
            address="av.state 532"
        )
        admin_user = User(
            username="adminuser",
            email="admin@example.com",
            password=generate_password_hash("Adminpassword123"),
            phone="987654321",
            address="admin address",
            role=Roles.ADMIN
        )
        
        seller_user = User(
            username="selleruser",
            email="seller@example.com",
            password=generate_password_hash("Sellerpassword123"),
            phone="555555555",
            address="seller address",
            role=Roles.SELLER
        )
        
        # Crear productos de prueba
        product1 = Product(
            name="Test Product 1",
            description="Description 1",
            price=10.99,
            stock=100,
            category_id=1,
            image_url="http://example.com/image1.jpg"
        )
        
        product2 = Product(
            name="Test Product 2",
            description="Description 2",
            price=20.50,
            stock=50,
            category_id=1,
            image_url="http://example.com/image2.jpg"
        )
        
        # Crear comentario de prueba
        comment = Comment(
            product_id=1,
            user_id=1,
            content="Great product!",
            stars=5
        )
        
        db.session.add_all([user, admin_user, seller_user, product1, product2, comment])
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
def user_access_token(app):
  with app.app_context():
        user = User.query.filter_by(email="testuser@example.com").first()
        return create_access_token(identity=str(user.id))

@pytest.fixture
def admin_access_token(app):
    with app.app_context():
        user = User.query.filter_by(email="admin@example.com").first()
        return create_access_token(identity=str(user.id))

@pytest.fixture
def seller_access_token(app):
    with app.app_context():
        user = User.query.filter_by(email="seller@example.com").first()      
        return create_access_token(identity=str(user.id))
      
      
def test_test(client):
  response = client.get("/products/test")
  assert response.status_code == 200
  assert response.get_json()

def test_get_products(client, user_access_token):
    headers = {'Authorization': f'Bearer {user_access_token}'}
    response = client.get('/products/products', headers=headers)
    assert response.status_code == 200
    assert all('description' in product for product in response.json)
    assert all('image_url' in product for product in response.json)
    assert all('category_id' in product for product in response.json)