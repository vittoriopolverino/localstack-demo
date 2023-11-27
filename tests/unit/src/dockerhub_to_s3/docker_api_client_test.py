import pytest


def test_get_data_from_api(docker_api_client):
    file_content = docker_api_client.get_data_from_api()
    assert isinstance(file_content, dict)
    assert 'user' in file_content
    assert 'name' in file_content
    assert 'namespace' in file_content
    assert 'star_count' in file_content
    assert 'pull_count' in file_content
    assert 'last_updated' in file_content


@pytest.mark.parametrize('api_url', ['https://fake.api.url.com/'])
def test_get_data_from_api_exception(docker_api_client, api_url):
    docker_api_client.docker_api_url = api_url
    with pytest.raises(Exception):
        docker_api_client.get_data_from_api()
