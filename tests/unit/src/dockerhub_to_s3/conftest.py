import datetime
import json
import os
from typing import Generator

import boto3
import pytest

from src.dockerhub_to_s3.docker_api_client import DockerAPIClient
from src.dockerhub_to_s3.pipeline import Pipeline


@pytest.fixture(scope='session', autouse=True)
def setup_environment():
    os.environ['DOCKER_API_URL'] = 'https://hub.docker.com/v2/repositories/localstack/localstack/'
    os.environ['S3_ENDPOINT_URL'] = 'http://s3.localhost.localstack.cloud:4566'
    os.environ['BUCKET_NAME'] = 'test-bucket'
    yield
    del os.environ['DOCKER_API_URL']
    del os.environ['S3_ENDPOINT_URL']
    del os.environ['BUCKET_NAME']


@pytest.fixture()
def pipeline() -> Generator[Pipeline, None, None]:
    bucket_name = os.environ['BUCKET_NAME']
    pipeline = Pipeline()
    session = boto3.Session(profile_name='localstack')
    pipeline.s3 = session.client('s3', endpoint_url=os.getenv('S3_ENDPOINT_URL'))
    pipeline.bucket_name = bucket_name
    pipeline.s3.create_bucket(Bucket=bucket_name)
    yield pipeline
    objects = pipeline.s3.list_objects(Bucket=bucket_name).get('Contents', [])
    for obj in objects:
        pipeline.s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
    pipeline.s3.delete_bucket(Bucket=bucket_name)


@pytest.fixture()
def docker_api_client() -> DockerAPIClient:
    docker_api_client = DockerAPIClient()
    docker_api_client.docker_api_url = os.getenv('DOCKER_API_URL')
    return docker_api_client


@pytest.fixture()
def date_str_params_1() -> str:
    return '2023-09-14T15:00:00.087021Z'


@pytest.fixture()
def datetime_params_1() -> datetime.datetime:
    return datetime.datetime(2023, 9, 14, 15, 0, 0, 87021)


@pytest.fixture()
def object_key_params_1() -> str:
    return 'raw/year=2023/month=09/day=14/2023_09_14_150000.json'


@pytest.fixture()
def data_params_1() -> str:
    return json.dumps({'name': 'localstack', 'namespace': 'localstack', 'pull_count': 178900000, 'star_count': 198, 'user': 'localstack'})


@pytest.fixture()
def date_str_params_2() -> str:
    return '2024-01-01T10:00:00.087021Z'


@pytest.fixture()
def datetime_params_2() -> datetime.datetime:
    return datetime.datetime(2024, 1, 1, 10, 0, 0, 87021)


@pytest.fixture()
def object_key_params_2() -> str:
    return 'raw/year=2024/month=01/day=01/2024_01_01_100000.json'


@pytest.fixture()
def data_params_2() -> str:
    return json.dumps({'name': 'localstack', 'namespace': 'localstack', 'pull_count': 185000000, 'star_count': 2010, 'user': 'localstack'})
