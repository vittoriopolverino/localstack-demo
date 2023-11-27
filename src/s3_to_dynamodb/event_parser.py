import logging

from urllib.parse import unquote


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EventParser:
    @staticmethod
    def get_bucket_name(event: dict) -> str:
        try:
            records = event.get('Records', [])
            bucket_name = records[0]['s3']['bucket']['name']
            return bucket_name
        except Exception as exception:
            logger.error(exception)
            raise

    @staticmethod
    def get_object_key(event: dict) -> str:
        try:
            records = event.get('Records', [])
            object_key = records[0]['s3']['object']['key']
            # Decode the S3 key to obtain the original form
            # Example: 'raw/year%3D2023/month%3D11/day%3D16/2023_11_16_095024.json' becomes
            # 'raw/year=2023/month=11/day=16/2023_11_16_095024.json'
            decoded_object_key = unquote(object_key)
            return decoded_object_key
        except Exception as exception:
            logger.error(exception)
            raise
