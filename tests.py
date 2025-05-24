import pytest
from app import create_app,db
from flask import jsonify, Response

@pytest.fixture
def app():
    app = create_app()
    app.config.from_object('Config.Testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
        

        
