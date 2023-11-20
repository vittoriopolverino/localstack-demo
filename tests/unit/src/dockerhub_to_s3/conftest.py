import datetime
import os

import pytest


@pytest.fixture(autouse=True)
def setup_environment():
    os.environ['DOCKER_API_URL'] = 'https://hub.docker.com/v2/repositories/localstack/localstack/'
    yield


@pytest.fixture()
def date_str_params_1() -> str:
    return '2023-09-14T15:00:00.087021Z'


@pytest.fixture()
def date_str_params_2() -> str:
    return '2024-01-01T10:00:00.087021Z'


@pytest.fixture()
def expected_result_params_1() -> datetime.datetime:
    return datetime.datetime(2023, 9, 14, 15, 0, 0, 87021)


@pytest.fixture()
def expected_result_params_2() -> datetime.datetime:
    return datetime.datetime(2024, 1, 1, 10, 0, 0, 87021)
