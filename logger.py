import logging

def setup_logger(name=None):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)  # Ajusta nivel según ambiente

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # Formato de logs
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        ch.setFormatter(formatter)

        logger.addHandler(ch)
        logger.propagate = False

    return logger