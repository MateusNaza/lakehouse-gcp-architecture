import os
from dotenv import load_dotenv

from core.utils import logger
from core.handlers.gcs_handler import GCSHandler

_LOGGER = logger.get_logger(__name__)

# Carrega as variáveis de ambiente (ex: GOOGLE_APPLICATION_CREDENTIALS)
load_dotenv()
PROJECT_ID = os.getenv('PROJECT_ID', '')


def main():
    
    pass
    

if __name__ == '__main__':

    main()
