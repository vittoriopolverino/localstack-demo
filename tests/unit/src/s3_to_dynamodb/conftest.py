import os

import pytest


@pytest.fixture(autouse=True)
def setup_environment():
    os.environ['S3_ENDPOINT_URL'] = 'http://s3.localhost.localstack.cloud:4566'
    os.environ['DYNAMODB_ENDPOINT_URL'] = 'http://localhost.localstack.cloud:4566'
    yield
