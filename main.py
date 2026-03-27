import os
from dotenv import load_dotenv

from core.utils import logger
from core.handlers.gcs_handler import GCSHandler

_LOGGER = logger.get_logger(__name__)

# Carrega as variáveis de ambiente (ex: GOOGLE_APPLICATION_CREDENTIALS)
load_dotenv()
PROJECT_ID = os.getenv('PROJECT_ID', '')


def main():
    
    _BUCKET_NAME = 'teste123jkfrewhgnjbuofbjo'

    gcs = GCSHandler(project_id=PROJECT_ID)


    buckets = gcs.list_buckets()
    
    if _BUCKET_NAME not in buckets:
        _LOGGER.info(f'PRIMEIRO IF [bucket name]: {_BUCKET_NAME} não encontrado')
        
    gcs.create_bucket(
        bucket_name=_BUCKET_NAME,
        location='US'
    )
    
    buckets = gcs.list_buckets()
    
    if _BUCKET_NAME not in buckets:
        _LOGGER.info(f'SEGUNDO IF [bucket name]: {_BUCKET_NAME} encontrado')
    
    gcs.delete_bucket(
        bucket_name=_BUCKET_NAME,
        force=True
    )
    

if __name__ == '__main__':

    main()
