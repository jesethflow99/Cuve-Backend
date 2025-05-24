from werkzeug.security import generate_password_hash
from app import db 
from models import User
import os
from logger import setup_logger

logger = setup_logger(__name__)

def create_superuser():


    email = os.getenv("SUPERUSER_EMAIL")
    username = os.getenv("SUPERUSER_USERNAME")
    password = os.getenv("SUPERUSER_PASSWORD")
    role = os.getenv("ADMIN_ROLE")

    if not all([email, username, password]):
        logger.error("Faltan variables de entorno para crear el superusuario.")
        print("Faltan variables de entorno para crear el superusuario.")
        return

    existing = User.query.filter_by(email=email).first()
    if existing:
        return

    new_superuser = User(
        username=username,
        email=email,
        password=generate_password_hash(password),
        role=role
    )
    db.session.add(new_superuser)
    db.session.commit()
    logger.info(f"Superusuario '{email}' creado exitosamente.")
    print(f"[+] Superusuario '{email}' creado exitosamente.")
