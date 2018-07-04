import json
import uuid

try:
    from urllib.parse import urlencode  # py2
except ImportError:
    from urllib import urlencode  # py2

import pytest
import responses

from dhis2 import exceptions
from dhis2.api import Dhis

BASEURL = 'https://play.dhis2.org/2.29'
API_URL = '{}/api'.format(BASEURL)


@pytest.fixture
def api():
    return Dhis(BASEURL, 'admin', 'district')

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
    url = '{}/organisationUnits/uid'.format(API_URL)

    responses.add(responses.DELETE, url, status=200)

    api.delete(endpoint='organisationUnits/uid')

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == url


@responses.activate
def test_info(api):
    url = '{}/system/info.json'.format(API_URL)
    r = {"contextPath": "https://play.dhis2.org/2.29"}

    responses.add(responses.GET, url, json=r, status=200)

    resp = api.info()

    assert resp == json.dumps(r, indent=2)
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

    with pytest.raises(exceptions.APIException) as e:
        api.get(endpoint='dataElements/foo')
    assert e.value.code == status_code
    assert e.value.url == url
    assert e.value.description == 'something failed'
    assert str(e.value)
    assert repr(e.value)

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == url

# ------------------
# PAGING
# ------------------


@pytest.mark.parametrize("page_size,no_of_pages,expected_amount", [
    [50, 2, 95],
    [100, 2, 195],
    [200, 3, 595],
    [20, 1, 15]
])
@responses.activate
def test_get_paged(api, page_size, no_of_pages, expected_amount):
    """
    first page: $page_size
    second page: $page_size minus overflow
    """
    overflow = 5

    # one page response
    if no_of_pages == 1:
        single_page = {
            "pager": {
                "page": 1,
                "pageCount": expected_amount,
                "total": expected_amount,
                "pageSize": page_size
            },
            "organisationUnits": [str(uuid.uuid4()) for _ in range(expected_amount)]
        }
        url = '{}/organisationUnits.json?pageSize={}&page=1'.format(API_URL, page_size)
        responses.add(responses.GET, url, json=single_page, status=200)

    # multi page response
    else:
        for i in range(1, no_of_pages):
            normal_page = {
                "pager": {
                    "page": i,
                    "pageCount": page_size,
                    "total": expected_amount,
                    "pageSize": page_size,
                    "nextPage": "{}/organisationUnits?page={}".format(API_URL, i + 1)
                },
                "organisationUnits": [str(uuid.uuid4()) for _ in range(page_size)]
            }
            url = '{}/organisationUnits.json?pageSize={}'.format(API_URL, page_size)
            responses.add(responses.GET, url, json=normal_page, status=200)

        # last page of multi page response
        last_amount = page_size - overflow
        last_page = {
            "pager": {
                "page": no_of_pages,
                "pageCount": last_amount,
                "total": expected_amount,
                "pageSize": page_size
            },
            "organisationUnits": [str(uuid.uuid4()) for _ in range(last_amount)]
        }
        url = '{}/organisationUnits.json?pageSize={}&page={}'.format(API_URL, page_size, no_of_pages)
        responses.add(responses.GET, url, json=last_page, status=200)

    counter = 0
    uid_list = []
    for page in api.get_paged('organisationUnits', page_size=page_size):
        counter += len(page['organisationUnits'])
        uid_list.extend(page['organisationUnits'])
    assert counter == expected_amount
    assert len(set(uid_list)) == len(uid_list)
    assert len(responses.calls) == no_of_pages


@responses.activate
def test_get_paged_empty(api):
    page_size = 50

    first_page = {
        "pager": {
            "page": 1,
            "pageCount": 2,
            "total": 0,
            "pageSize": page_size
        },
        "organisationUnits": []
    }
    url = '{}/organisationUnits.json?pageSize={}&page=1'.format(API_URL, page_size)
    responses.add(responses.GET, url, json=first_page, status=200)

    counter = 0
    for page in api.get_paged('organisationUnits', page_size=50):
        counter += len(page['organisationUnits'])
    assert counter == 0
    assert len(responses.calls) == 1


@responses.activate
def test_page_size_zero(api):
    with pytest.raises(exceptions.ClientException):
        for _ in api.get_paged('organisationUnits', page_size=0):
            pass


@responses.activate
def test_paging_with_params(api):
    url = '{}/organisationUnits.json?pageSize=50&paging=False'.format(API_URL)
    r = {
        "pager": {
            "page": 1,
            "pageCount": 1,
            "total": 0,
            "pageSize": 50
        },
        "organisationUnits": []
    }
    responses.add(responses.GET, url, json=r, status=200)
    with pytest.raises(exceptions.ClientException):
        params = {'paging': False}
        for _ in api.get_paged('organisationUnits', params=params):
            pass


@pytest.mark.parametrize("from_server,integer", [
    ("2.29", 29),
    ("2.30", 30),
    ("2.30-SNAPSHOT", 30)
])
@responses.activate
def test_dhis_version(api, from_server, integer):
    url = '{}/system/info.json'.format(API_URL)
    r = {"version": from_server}

    responses.add(responses.GET, url, json=r, status=200)

    resp = api.dhis_version()

    assert resp == integer
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == url
    assert responses.calls[0].response.text == json.dumps(r)


@responses.activate
def test_dhis_version_invalid(api):
    url = '{}/system/info.json'.format(API_URL)
    r = {"version": "unknown"}

    responses.add(responses.GET, url, json=r, status=200)

    with pytest.raises(exceptions.ClientException):
        api.dhis_version()

# ------------------
# UID GENERATION
# ------------------


@responses.activate
def test_generate_uids(api):
    amount = 13000
    url = '{}/system/id.json'.format(API_URL, amount)

    responses.add_passthru(url)
    uids = api.generate_uids(amount)
    assert (len(uids) == amount)


# ------------------
# SQL VIEW
# ------------------

SQL_VIEW = 'YOaOY605rzh'


@pytest.fixture
def sql_view_view():
    url = '{}/sqlViews/{}'.format(API_URL, SQL_VIEW)
    r = {'type': 'VIEW'}
    responses.add(responses.GET, "{}.json?fields=type".format(url), json=r, status=200)
    return url


@pytest.fixture
def sql_view_query():
    url = '{}/sqlViews/{}'.format(API_URL, SQL_VIEW)
    r = {'type': 'QUERY'}
    responses.add(responses.GET, "{}.json?fields=type".format(url), json=r, status=200)
    return url


@responses.activate
def test_get_sqlview(api, sql_view_view):

    # execute
    responses.add(responses.POST, '{}/execute'.format(sql_view_view), status=200)

    # get data
    r = """
name,code
0-11m,COC_358963
0-11m,
0-4y,COC_358907
    """
    responses.add(responses.GET, '{}/data.csv'.format(sql_view_view), json=r, status=200)

    expected = [
        {'name': '0-11m', 'code': 'COC_358963'},
        {'name': '0-11m'},
        # don't include this {'name': '0-4y', 'code': 'COC_358907'}
    ]
    for index, row in enumerate(api.get_sqlview(SQL_VIEW, True, criteria={'name': '0-11m'})):
        assert row == expected[index]


def test_get_sqlview_criteria(api, sql_view_view):
    with pytest.raises(exceptions.ClientException):
        for _ in api.get_sqlview(SQL_VIEW, True, criteria='code:name'):
            pass


def test_get_sqlview_criteria_none(api, sql_view_view):
        for _ in api.get_sqlview(SQL_VIEW, True):
            pass


@responses.activate
def test_get_sqlview_variable_query(api, sql_view_query):

    r = """
dataelementid,name,valueType
1151060,Inpatient cases,INTEGER
1151042,MNCH vacuum/forceps delivery,INTEGER    
    """
    responses.add(responses.GET, '{}/data.csv'.format(sql_view_query), json=r, status=200)

    expected = [
        {'dataelementid': '1151060', 'name': 'Inpatient cases', 'valueType': 'INTEGER'},
        {'dataelementid': '1151042', 'name': 'MNCH vacuum / forceps delivery', 'valueType': 'INTEGER'}
    ]
    for index, row in enumerate(api.get_sqlview(SQL_VIEW, var={'valueType': 'INTEGER'})):
        assert row == expected[index]


@responses.activate
def test_get_sqlview_variable_query_execute_throws(api, sql_view_query):
    with pytest.raises(exceptions.ClientException):
        for _ in api.get_sqlview(SQL_VIEW, execute=True, var={'valueType': 'INTEGER'}):
            pass


@responses.activate
def test_get_sqlview_variable_query_no_dict(api, sql_view_query):
    with pytest.raises(exceptions.ClientException):
        for _ in api.get_sqlview(SQL_VIEW, var='NODICT'):
            pass

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
   'organisationUnits', 'schemas'
])
@responses.activate
def test_requests_valid_endpoint(api, endpoint):
    url = '{}/{}.json'.format(API_URL, endpoint)
    r = {"version": "unknown"}

    responses.add(responses.GET, url, json=r, status=200)
    api.get(endpoint)
    assert endpoint in responses.calls[0].request.url


@pytest.mark.parametrize("file_type", [
    '.hello', '', None, u'EXCEL'
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
   dict(), {'data': 'something'}
])
@responses.activate
def test_requests_valid_params(api, params):
    endpoint = 'dataElements'
    url = '{}/{}.json'.format(API_URL, endpoint)

    responses.add(responses.GET, url, status=200)
    api.get(endpoint, params=params)
    param_string = urlencode(params)
    assert param_string in responses.calls[0].request.url


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
