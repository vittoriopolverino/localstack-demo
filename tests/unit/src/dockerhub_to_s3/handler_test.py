import datetime

import pytest

from src.dockerhub_to_s3.handler import get_data_from_docker_api
from src.dockerhub_to_s3.handler import convert_to_datetime


def test_get_data_from_docker_api():
    file_content = get_data_from_docker_api()
    assert isinstance(file_content, dict)
    assert 'user' in file_content
    assert 'name' in file_content
    assert 'namespace' in file_content
    assert 'star_count' in file_content
    assert 'pull_count' in file_content
    assert 'last_updated' in file_content


@pytest.mark.parametrize(
    'date_str, expected', [('date_str_params_1', 'expected_result_params_1'), ('date_str_params_2', 'expected_result_params_2')]
)
def test_convert_to_datetime(date_str, expected, request):
    date_str = request.getfixturevalue(date_str)
    expected = request.getfixturevalue(expected)
    result = convert_to_datetime(date_str=date_str)
    assert isinstance(result, datetime.datetime)
    assert result == expected
