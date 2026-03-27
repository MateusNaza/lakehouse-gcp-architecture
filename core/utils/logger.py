import logging
import os

from pyfiglet import Figlet

_LOG_LEVEL = os.getenv('LOG_LEVEL', logging.INFO)
_LOG_FORMAT = '[%(asctime)s] | %(levelname)s | %(name)s:%(lineno)s >> %(message)s'

# só pra tirar uma onda com o nome no log
f = Figlet(font='cricket')
print(f.renderText('Mateus Naza'))

def get_logger(module):
    logger = logging.getLogger(module)
    logger.setLevel(_LOG_LEVEL)

    log_formatter = logging.Formatter(_LOG_FORMAT)
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(log_formatter)

    logger.propagate = False
    logger.addHandler(log_handler)

    return logger