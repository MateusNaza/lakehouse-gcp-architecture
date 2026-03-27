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


    def list_objects(
        self,
        bucket_name: str,
        prefix: str | None = None
    ) -> list:
        """
        Lista todos os objetos em um bucket, opcionalmente filtrando por um prefixo.
        
        Args:
            bucket_name (str): O nome do bucket.
            prefix (str): Opcional. Prefixo para filtrar os objetos listados.
            
        Returns:
            list: Lista de objetos Blob.
        """
        try:
            bucket = self.client.bucket(bucket_name)
            blobs = list(bucket.list_blobs(prefix=prefix))
            
            _LOGGER.info(f'[bucket name]: `{bucket_name}` | objetos encontrados: {len(blobs)}')
            return blobs
        
        except NotFound:
            _LOGGER.error(f'[bucket name]: `{bucket_name}` não encontrado ao tentar listar objetos.')
            return []
            
        except Exception as e:
            _LOGGER.error(f'Erro ao listar objetos no bucket `{bucket_name}`: {e}')
            return []


    def upload_object(
        self,
        bucket_name: str,
        source_file_name: str,
        destination_blob_name: str
    ) -> storage.Blob | None:
        """
        Faz o upload de um arquivo para o bucket do GCS.
        
        Args:
            bucket_name (str): O nome do bucket.
            source_file_name (str): Caminho local do arquivo a ser feito upload.
            destination_blob_name (str): Nome de destino do arquivo no bucket.
            
        Returns:
            storage.Blob: O objeto do Blob criado no GCS, ou None em caso de erro.
        """
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(destination_blob_name)
            
            blob.upload_from_filename(source_file_name)
            
            _LOGGER.info(f'[blob name]: `{destination_blob_name}` salvo com sucesso no bucket `{bucket_name}`')
            return blob
            
        except NotFound:
            _LOGGER.error(f'[bucket name]: `{bucket_name}` não encontrado.')
            return None
            
        except FileNotFoundError:
            _LOGGER.error(f'[source file]: `{source_file_name}` não encontrado no disco local.')
            return None
            
        except Exception as e:
            _LOGGER.error(f'Erro ao fazer upload do arquivo `{source_file_name}`: {e}')
            return None


    def delete_object(
        self,
        bucket_name: str,
        blob_name: str
    ) -> bool:
        """
        Exclui um objeto específico do bucket.
        
        Args:
            bucket_name (str): O nome do bucket.
            blob_name (str): O nome do arquivo/objeto no GCS a ser excluído.
            
        Returns:
            bool: True se o objeto foi excluído com sucesso, False caso contrário.
        """
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            blob.delete()
            
            _LOGGER.info(f'[blob name]: `{blob_name}` excluído com sucesso do bucket `{bucket_name}`.')
            return True
            
        except NotFound:
            _LOGGER.error(f'[blob name]: `{blob_name}` não encontrado no bucket `{bucket_name}`.')
            return False
            
        except Exception as e:
            _LOGGER.error(f'Erro ao excluir objeto `{blob_name}`: {e}')
            return False
