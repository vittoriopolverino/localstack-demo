import os
from typing import Generator

import boto3
import pytest

from src.dockerhub_to_s3.docker_api_client import DockerAPIClient
from src.dockerhub_to_s3.pipeline import Pipeline


@pytest.fixture(autouse=True)
def setup_environment():
    os.environ['DOCKER_API_URL'] = 'https://hub.docker.com/v2/repositories/localstack/localstack/'
    os.environ['S3_ENDPOINT_URL'] = 'http://s3.localhost.localstack.cloud:4566'
    os.environ['BUCKET_NAME'] = 'test-bucket'
    yield
    del os.environ['DOCKER_API_URL']
    del os.environ['S3_ENDPOINT_URL']
    del os.environ['BUCKET_NAME']


@pytest.fixture()
def pipeline(docker_api_client) -> Generator[Pipeline, None, None]:
    bucket_name = os.environ['BUCKET_NAME']
    pipeline = Pipeline()
    session = boto3.Session(profile_name='localstack')
    pipeline.s3 = session.client('s3', endpoint_url=os.getenv('S3_ENDPOINT_URL'))
    pipeline.bucket_name = bucket_name
    pipeline.s3.create_bucket(Bucket=bucket_name)
    pipeline.docker_api_client = docker_api_client
    yield pipeline
    # tear down
    objects = pipeline.s3.list_objects(Bucket=bucket_name).get('Contents', [])
    for obj in objects:
        pipeline.s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
    pipeline.s3.delete_bucket(Bucket=bucket_name)


@pytest.fixture()
def docker_api_client() -> DockerAPIClient:
    docker_api_client = DockerAPIClient()
    docker_api_client.docker_api_url = os.getenv('DOCKER_API_URL')
    return docker_api_client
