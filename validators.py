from marshmallow import ValidationError
import re

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