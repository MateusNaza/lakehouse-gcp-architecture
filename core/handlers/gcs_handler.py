from google.cloud import storage
from google.cloud.exceptions import (
    Conflict,
    NotFound
)

from core.utils import logger

_LOGGER = logger.get_logger(__name__)


class GCSHandler:
    """
    Handler para operações no Google Cloud Storage (GCS).
    """

    def __init__(
        self, 
        project_id: str 
    ):
        """
        Inicializa o client do GCS.
        Se project_id não for fornecido, a biblioteca tentará inferir
        do ambiente (ex: variável GOOGLE_CLOUD_PROJECT ou credenciais).
        """
        
        self.client = storage.Client(project=project_id)


    def list_buckets(self) -> list:
        """
        Lista todos os buckets no projeto configurado.
        
        Returns:
            list: Lista de objetos Bucket.
        """
        return list(self.client.list_buckets())


    def create_bucket(
        self, 
        bucket_name: str, 
        location: str = 'US'
    ) -> storage.Bucket | None:
        """
        Cria um novo bucket no GCS.
        
        Args:
            bucket_name (str): O nome do bucket a ser criado (deve ser globalmente único).
            location (str): A localização do bucket (ex: 'US', 'us-east1').
            
        Returns:
            storage.Bucket: O objeto do bucket criado, ou None se houver erro.
        """
        try:
            bucket = self.client.bucket(bucket_name)
            
            bucket.location = location
            created_bucket = self.client.create_bucket(bucket)
            
            _LOGGER.info(f'[bucket name]: `{bucket_name}` criado com sucesso!')
            _LOGGER.info(f'[location]: `{location}`')
            
            return created_bucket
        
        except Conflict:
            _LOGGER.error(f'[bucket name]: `{bucket_name}` já existe e é de propriedade de outro usuário ou projeto.')
            return None
        
        except Exception as e:
            _LOGGER.error(f'Erro ao criar o bucket `{bucket_name}`: {e}')
            return None


    def delete_bucket(
        self,
        bucket_name: str,
        force: bool = False
    ) -> bool:
        """
        Exclui um bucket do GCS.
        
        Args:
            bucket_name (str): O nome do bucket a ser excluído.
            force (bool): Se True, exclui o bucket mesmo se ele contiver objetos.
                          Se False, a exclusão falhará se o bucket não estiver vazio.
                          
        Returns:
            bool: True se o bucket foi excluído com sucesso, False caso contrário.
        """
        try:
            bucket = self.client.bucket(bucket_name)
            bucket.delete(force=force)
            _LOGGER.info(f'[bucket name]: `{bucket_name}` excluído com sucesso.')
            return True
        
        except NotFound:
            _LOGGER.error(f'[bucket name]: `{bucket_name}` não encontrado.')
            return False
        
        except Exception as e:
            _LOGGER.error(f'[bucket name]: `{bucket_name}` erro ao excluir.. Erro: {e}')
            return False
