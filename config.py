from datetime import timedelta
import os


class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET = os.getenv('JWT_SECRET')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)  # 7 days
    
class Development(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI_DEVELOPMENT', 'sqlite:///dev.db')
    
class Testing(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # Use an in-memory database for testing
    
class Production(Config):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI_PRODUCTION', 'sqlite:///prod.db')
    
def get_config():
    env = os.getenv('APP_ENV', 'development').lower()
    config_class = {
        'development': Development,
        'testing': Testing,
        'production': Production
    }.get(env, Config)

    # Validaciones críticas
    if env == 'production':
        if not config_class.JWT_SECRET:
            raise RuntimeError("JWT_SECRET no está configurado para producción")
        if not config_class.DATABASE_URI or 'sqlite' in config_class.DATABASE_URI:
            raise RuntimeError("DATABASE_URI de producción no está configurada correctamente")
    
    return config_class
