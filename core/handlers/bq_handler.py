from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from google.cloud.bigquery.table import RowIterator


from core.utils import logger

_LOGGER = logger.get_logger(__name__)


class BQHandler:
    """
    Handler para operações no Google Cloud BigQuery.
    """

    def __init__(
        self, 
        project_id: str | None = None
    ):
        """
        Inicializa o client do BigQuery.
        Se project_id não for fornecido, a biblioteca tentará inferir
        do ambiente (ex: variável GOOGLE_CLOUD_PROJECT ou credenciais).
        """
        self.client = bigquery.Client(project=project_id)
        self.project_id = self.client.project


    def get_table_ref(
        self,
        dataset_id: str,
        table_id: str
    ) -> bigquery.TableReference:
        """
        Retorna a referência de uma tabela no BigQuery.
        
        Args:
            dataset_id (str): O ID do dataset.
            table_id (str): O ID da tabela.
            
        Returns:
            bigquery.TableReference: Objeto de referência da tabela.
        """
        _LOGGER.debug(f'[START] [get_table_ref] dataset: `{dataset_id}` | table: `{table_id}`')
        
        dataset_ref = bigquery.DatasetReference(
            project=self.project_id,
            dataset_id=dataset_id
        )
        table_ref = bigquery.TableReference(
            dataset_ref=dataset_ref,
            table_id=table_id
        )
        
        _LOGGER.debug('[END] [get_table_ref]')
        
        return table_ref


    def table_exists(
        self, 
        table_ref: str
    ) -> bool:
        """
        Verifica se uma tabela do BigQuery existe.
        
        Args:
            table_ref (str): A referência completa da tabela no formato `projeto.dataset.tabela`.
            
        Returns:
            bool: True se a tabela existe, False caso contrário.
        """
        try:
            self.client.get_table(table_ref)
            return True
        
        except NotFound:
            return False
            
        except Exception as e:
            _LOGGER.error(f'Erro ao verificar a existência da tabela `{table_ref}`: {e}')
            return False


    def execute_query(
        self,
        query: str
    ) -> RowIterator | None:
        """
        Executa uma query no BigQuery de forma nativa.
        
        Args:
            query (str): A string contendo a query SQL a ser executada.
            
        Returns:
            RowIterator: O resultado iterável da query, ou None em caso de erro.
        """
        _LOGGER.debug('[START] [execute_query]')

        try:
            query_job = self.client.query(query)
            result = query_job.result()  # Aguarda a conclusão da query
            
            _LOGGER.info('[query]: executada com sucesso!')
            _LOGGER.debug('[END] [execute_query]')
            
            return result
            
        except Exception as e:
            _LOGGER.error(f'Erro ao executar a query: {e}')
            return None


    def load_file_to_table(
        self,
        source_file_path: str,
        table_id: str,
        source_format: str = bigquery.SourceFormat.CSV,
        write_disposition: str = bigquery.WriteDisposition.WRITE_TRUNCATE,
        schema_file_path: str | None = None,
        partition_field: str | None = None,
        partition_type: str = 'DAY'
    ) -> bool:
        """
        Faz a carga de um arquivo local (CSV, JSONL, PARQUET, etc) para uma tabela do BigQuery, 
        utilizando apenas a API nativa.
        
        Args:
            source_file_path (str): Caminho local do arquivo fonte a ser carregado.
            table_id (str): Identificador completo da tabela (ex: 'projeto.dataset.tabela').
            source_format (str): Formato do arquivo (ex: bigquery.SourceFormat.PARQUET). Padrão: CSV.
            write_disposition (str): Regra de escrita para garantir idempotência. 
                                     Padrões: WRITE_TRUNCATE (sobrescreve, idempotente) ou WRITE_APPEND (adiciona).
            schema_file_path (str | None): Caminho para o JSON contendo a estrutura do schema BQ.
            partition_field (str | None): Nome da coluna de DATE/TIMESTAMP para particionar a tabela.
            partition_type (str): Granularidade do particionamento ('HOUR', 'DAY', 'MONTH', 'YEAR'). Padrão: 'DAY'.
            
        Returns:
            bool: True se os dados foram carregados com sucesso, False caso contrário.
        """
        _LOGGER.info(f'Iniciando o carregamento para a tabela `{table_id}`...')
        
        try:
            job_config = bigquery.LoadJobConfig(
                source_format=source_format,
                write_disposition=write_disposition
            )
            
            if schema_file_path:
                _LOGGER.info(f'[schema]: via arquivo .json')
                job_config.schema = self.client.schema_from_json(schema_file_path)
                job_config.autodetect = False
            else:
                job_config.autodetect = True
                
            if partition_field:
                _LOGGER.info(f'[partition field]: `{partition_field}` (Granularidade: {partition_type})')
                
                type_mapping = {
                    'HOUR': bigquery.TimePartitioningType.HOUR,
                    'DAY': bigquery.TimePartitioningType.DAY,
                    'MONTH': bigquery.TimePartitioningType.MONTH,
                    'YEAR': bigquery.TimePartitioningType.YEAR,
                }
                
                job_config.time_partitioning = bigquery.TimePartitioning(
                    type_=type_mapping.get(partition_type.upper(), bigquery.TimePartitioningType.DAY),
                    field=partition_field
                )
            
            with open(source_file_path, 'rb') as source_file:
                load_job = self.client.load_table_from_file(
                    source_file,
                    table_id,
                    job_config=job_config
                )
                
            load_job.result()  
            
            _LOGGER.info(f'[linhas carregadas]: `{load_job.output_rows}` na tabela `{table_id}`')
            
            return True
            
        except FileNotFoundError:
            _LOGGER.error(f'[source file]: `{source_file_path}` não encontrado no disco local.')
            return False
            
        except Exception as e:
            _LOGGER.error(f'Falha ao carregar os dados na tabela `{table_id}`: {e}')
            return False
