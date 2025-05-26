import logging
import os

def setup_logger(name=None):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)  # Ajusta nivel según ambiente

        # Verificar y crear directorio de logs
        if not os.path.exists('logs'):
            os.makedirs('logs')

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        
        # File handler
        fh = logging.FileHandler('logs/app.log', encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        
        # Formato de logs
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)
        logger.propagate = False

    return logger

# Prueba
if __name__ == "__main__":
    logger = setup_logger('test_logger')
    logger.debug('Este es un mensaje de prueba')