import logging

def setup_logger(name=None):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)  # Ajusta nivel según ambiente

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        
        #file handler
        fh = logging.FileHandler('logs/app.log', encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        # Formato de logs
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)
        logger.propagate = False

    return logger