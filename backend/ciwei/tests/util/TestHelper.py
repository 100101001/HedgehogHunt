from mock import mock


def test_mock(url, method, data, response):
    mock_method = mock.Mock(return_value=response)
    return mock_method(url, method, data)


def build_api_url(suffix):
    return "http://127.0.0.1:8999/api/" + suffix
