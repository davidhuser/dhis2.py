import json

from urllib.parse import urlencode  # py2

import pytest
import responses

from dhis2 import exceptions
from dhis2.api import Api

from .common import BASEURL, API_URL


@pytest.fixture  # BASE FIXTURE
def api():
    return Api(BASEURL, 'admin', 'district')


@pytest.fixture  # BASE FIXTURE
def api_with_api_version():
    return Api(BASEURL, 'admin', 'district', api_version=30)

# ------------------
# GENERAL API STUFF
# ------------------


@responses.activate
def test_post(api):
    url = '{}/metadata'.format(API_URL)
    p = {"obj": "some data"}

    responses.add(responses.POST, url, json=p, status=201)

    api.post(endpoint='metadata', data=p)

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == url


@responses.activate
def test_put(api):
    url = '{}/organisationUnits/uid'.format(API_URL)
    p = {"obj": "some data"}

    responses.add(responses.PUT, url, json=p, status=200)

    api.put(endpoint='organisationUnits/uid', data=p)

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == url


@responses.activate
def test_patch(api):
    url = '{}/organisationUnits/uid'.format(API_URL)
    p = {"obj": "some data"}

    responses.add(responses.PATCH, url, json=p, status=200)

    api.patch(endpoint='organisationUnits/uid', data=p)

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == url


@responses.activate
def test_delete(api):
    url = '{}/organisationUnits/uid?a=b'.format(API_URL)
    p = {"obj": "some data"}

    responses.add(responses.DELETE, url, json=p, status=200)

    api.delete(endpoint='organisationUnits/uid', json=p, params={'a': 'b'})

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == url


@responses.activate
def test_info(api):
    url = '{}/system/info.json'.format(API_URL)
    r = {"contextPath": "https://play.dhis2.org/2.30"}

    responses.add(responses.GET, url, json=r, status=200)

    prop = api.info

    assert prop == r
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == url
    assert responses.calls[0].response.text == json.dumps(r)


@pytest.mark.parametrize("status_code", [
    400, 401, 402, 403, 404, 405, 406, 407, 408, 409,
    410, 411, 412, 413, 414, 415, 416, 417, 418, 421,
    422, 423, 424, 426, 428, 429, 431, 451, 444, 494,
    495, 496, 497, 499, 500, 501, 502, 503, 504, 505,
    506, 507, 508, 510, 511
])
@responses.activate
def test_client_server_errors(api, status_code):
    url = '{}/dataElements/foo.json'.format(API_URL)

    responses.add(responses.GET, url, body='something failed', status=status_code)

    with pytest.raises(exceptions.RequestException) as e:
        api.get(endpoint='dataElements/foo')
    assert e.value.code == status_code
    assert e.value.url == url
    assert e.value.description == 'something failed'
    assert str(e.value)
    assert repr(e.value)

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == url

# ------------------
# PRE-REQUEST VALIDATION
# ------------------


@pytest.mark.parametrize("endpoint", [
    '', ' ', None, [], {'endpoint': 'organisationUnits'}
])
def test_requests_invalid_endpoint(api, endpoint):
    with pytest.raises(exceptions.ClientException):
        api.get(endpoint)


@pytest.mark.parametrize("endpoint", [
   'organisationUnits', 'schemas', u'schemas'
])
@responses.activate
def test_requests_valid_endpoint(api, endpoint):
    url = '{}/{}.json'.format(API_URL, endpoint)
    r = {"version": "unknown"}

    responses.add(responses.GET, url, json=r, status=200)
    api.get(endpoint)
    assert endpoint in responses.calls[0].request.url


@pytest.mark.parametrize("file_type", [
    '.hello', '', ' ', u'EXCEL'
])
def test_requests_invalid_file_type(api, file_type):
    with pytest.raises(exceptions.ClientException):
        api.get('organisationUnits', file_type=file_type)


@pytest.mark.parametrize("file_type", [
   'csv', 'CSV', 'JSON', 'xml', 'pdf'
])
@responses.activate
def test_requests_valid_file_type(api, file_type):
    endpoint = 'dataElements'
    url = '{}/{}.{}'.format(API_URL, endpoint, file_type.lower())

    responses.add(responses.GET, url, status=200)
    api.get(endpoint, file_type=file_type)
    assert '{}.{}'.format(endpoint, file_type.lower()) in responses.calls[0].request.url


@pytest.mark.parametrize("params", [
    '{ "hello": "yes" }', (1, 2)
])
def test_requests_invalid_params(api, params):
    with pytest.raises(exceptions.ClientException):
        api.get('organisationUnits', params=params)


@pytest.mark.parametrize("params", [
    dict(),
    {'data': 'something'},
    [('data', 'something')]
])
@responses.activate
def test_requests_valid_params(api, params):
    endpoint = 'dataElements'
    url = '{}/{}.json'.format(API_URL, endpoint)

    responses.add(responses.GET, url, status=200)
    api.get(endpoint, params=params)
    param_string = urlencode(params)
    assert param_string in responses.calls[0].request.url


@pytest.mark.parametrize("params", [
    ('paging', False),  # must be list
    [('paging', False), 3]  # must be list of tuples
])
def test_requests_invalid_params(api, params):
    with pytest.raises(exceptions.ClientException):
        api.get('organisationUnits', params=params)


@pytest.mark.parametrize("data", [
    '{ "hello": "yes" }', (1, 2)
])
def test_requests_invalid_data(api, data):
    with pytest.raises(exceptions.ClientException):
        api.post('organisationUnits', data=data)


@pytest.mark.parametrize("data", [
   {'data': 'something'}
])
@responses.activate
def test_requests_valid_data(api, data):
    endpoint = 'dataElements'
    url = '{}/{}'.format(API_URL, endpoint)
    responses.add(responses.POST, url, json=data, status=204)
    api.post(endpoint, data=data)


def test_invalid_http_method(api):
    with pytest.raises(exceptions.ClientException):
        api._make_request('update', 'dataElements')


@responses.activate
def test_json_arg_valid(api):
    endpoint = 'dataElements'
    url = '{}/{}'.format(API_URL, endpoint)
    data = {'data': 'something'}
    responses.add(responses.POST, url, json=data, status=204)
    api.post(endpoint, data=data)
    api.post(endpoint, json=data)
