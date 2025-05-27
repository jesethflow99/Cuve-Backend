from marshmallow import ValidationError
import re
from models import User, Product, Order, OrderItem, Comment, Category


def validate_password(password):
    if len(password) < 8:
        raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
    if not re.search(r"[A-Z]", password):
        raise ValidationError("La contraseña debe contener al menos una letra mayúscula.")
    if not re.search(r"[a-z]", password):
        raise ValidationError("La contraseña debe contener al menos una letra minúscula.")
    if not re.search(r"[0-9]", password):
        raise ValidationError("La contraseña debe contener al menos un número.")

def validate_phone(phone):
    if not re.match(r"^\+?\d{10,15}$", phone):
        raise ValidationError("El número de teléfono no es válido.")
    # Check if the phone number is already in use
    existing_user = User.query.filter_by(phone=phone).first()
    if existing_user:
        raise ValidationError("El número de teléfono ya está en uso.")
    
def validate_email(email):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValidationError("El correo electrónico no es válido.")
    # Check if the email is already in use
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        raise ValidationError("El correo electrónico ya está en uso.")
    
def validate_price(price):
    if price <= 0:
        raise ValidationError("El precio debe ser un número positivo.")
    
def validate_stock(stock):
    if stock < 0:
        raise ValidationError("El stock no puede ser negativo.")