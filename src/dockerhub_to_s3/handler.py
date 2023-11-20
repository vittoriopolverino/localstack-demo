import os
from datetime import datetime

import urllib3
import json
import boto3

BUCKET_NAME = os.environ.get('BUCKET_NAME', None)
s3 = boto3.client('s3', endpoint_url=os.environ.get('S3_ENDPOINT_URL', None))


def get_data_from_docker_api() -> dict:
    http = urllib3.PoolManager()
    response = http.request('GET', os.environ.get('DOCKER_API_URL', None))
    return json.loads(response.data.decode('utf-8'))


def convert_to_datetime(date_str: str) -> datetime:
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')


def handler(event, context):
    try:
        data = get_data_from_docker_api()
        last_updated = data.get('last_updated', None)
        last_updated_date = convert_to_datetime(date_str=last_updated)

        # The key follows a structured format: raw/year=YYYY/month=MM/day=DD/YYYY_MM_DD_HHMMSS.json
        object_key = (
            f'raw/'
            f'year={last_updated_date.year}/'
            f'month={last_updated_date.month:02d}/'
            f'day={last_updated_date.day:02d}/'
            f"{last_updated_date.strftime('%Y_%m_%d_%H%M%S')}.json"
        )
        s3.put_object(Body=json.dumps(data), Bucket=BUCKET_NAME, Key=object_key)

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Dockerhub to S3 - Request processed successfully'}),
        }
    except Exception as exception:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'{type(exception)} - {str(exception)}', 'error': 'Internal Server Error'}),
        }
