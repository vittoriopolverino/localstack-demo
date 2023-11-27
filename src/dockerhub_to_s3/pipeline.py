import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import boto3
from botocore.client import BaseClient

from src.dockerhub_to_s3.docker_api_client import DockerAPIClient


@dataclass
class Pipeline:
    s3_endpoint_url: Optional[str] = field(default=os.environ.get('S3_ENDPOINT_URL', None))
    bucket_name: Optional[str] = field(default=os.environ.get('BUCKET_NAME', None))

    docker_api_client: DockerAPIClient = field(default_factory=lambda: DockerAPIClient())

    s3: BaseClient = field(init=False, repr=True)
    object_key: str = field(init=False, repr=True)
    data: dict = field(init=False, repr=True)

    def __post_init__(self):
        self.s3 = boto3.client('s3', endpoint_url=self.s3_endpoint_url)

    @staticmethod
    def convert_to_datetime(date_str: str) -> datetime:
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')

    @staticmethod
    def format_object_key(date: datetime) -> str:
        # The key follows a structured format: raw/year=YYYY/month=MM/day=DD/YYYY_MM_DD_HHMMSS.json
        return f'raw/' f'year={date.year}/' f'month={date.month:02d}/' f'day={date.day:02d}/' f"{date.strftime('%Y_%m_%d_%H%M%S')}.json"

    def upload_to_s3(self, data: str, bucket_name: str, object_key: str) -> dict:
        return self.s3.put_object(Body=data, Bucket=bucket_name, Key=object_key)

    def execute(self, event, context):
        try:
            self.data = self.docker_api_client.get_data_from_api()
            last_updated = self.convert_to_datetime(date_str=self.data.get('last_updated', None))
            self.object_key = self.format_object_key(date=last_updated)
            self.upload_to_s3(data=json.dumps(self.data), bucket_name=self.bucket_name, object_key=self.object_key)

            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Dockerhub to S3 - Request processed successfully'}),
            }
        except Exception as exception:
            return {
                'statusCode': 500,
                'body': json.dumps({'message': f'{type(exception)} - {str(exception)}', 'error': 'Internal Server Error'}),
            }
