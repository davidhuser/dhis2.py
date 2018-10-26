import pytest
import responses
import time

from dhis2 import exceptions, Dhis

from .common import API_URL, BASEURL


SQL_VIEW = 'YOaOY605rzh'


@pytest.fixture  # BASE FIXTURE
def api():
    return Dhis(BASEURL, 'admin', 'district')


@pytest.fixture  # BASE FIXTURE
def api_with_api_version():
    return Dhis(BASEURL, 'admin', 'district', api_version=30)


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
name,code,attr\n
0-11m,COC_358963,123\n
0-11m,,456
"""
    responses.add(responses.GET, '{}/data.csv'.format(sql_view_view), body=r, status=200)

    expected = [
        {'name': '0-11m', 'code': 'COC_358963', 'attr': '123'},
        {'name': '0-11m', 'code': '', 'attr': '456'},
    ]
    for index, row in enumerate(api.get_sqlview(SQL_VIEW, True, criteria={'name': '0-11m'})):
        assert isinstance(row, dict)
        assert row == expected[index]


def test_get_sqlview_criteria(api, sql_view_view):
    with pytest.raises(exceptions.ClientException):
        for _ in api.get_sqlview(SQL_VIEW, True, criteria='code:name'):
            continue


def test_get_sqlview_criteria_none(api, sql_view_view):
        for _ in api.get_sqlview(SQL_VIEW, True):
            continue


@responses.activate
def test_get_sqlview_variable_query(api, sql_view_query):

    r = """
dataelementid,name,valueType\n
1151060,Inpatient cases,INTEGER\n
1151042,MNCH vacuum/forceps delivery,INTEGER
"""
    responses.add(responses.GET, '{}/data.csv'.format(sql_view_query), body=r, status=200)

    expected = [
        {'dataelementid': '1151060', 'name': 'Inpatient cases', 'valueType': 'INTEGER'},
        {'dataelementid': '1151042', 'name': 'MNCH vacuum/forceps delivery', 'valueType': 'INTEGER'}
    ]
    for index, row in enumerate(api.get_sqlview(SQL_VIEW, var={'valueType': 'INTEGER'})):
        assert isinstance(row, dict)
        assert row == expected[index]


@responses.activate
def test_get_sqlview_variable_query_execute_throws(api, sql_view_query):  # noqa
    responses.add(responses.POST, '{}/execute'.format(sql_view_query), status=200)
    with pytest.raises(exceptions.ClientException):
        for _ in api.get_sqlview(SQL_VIEW, execute=True, var={'valueType': 'INTEGER'}):
            continue


@pytest.mark.flaky(reruns=3, reruns_delay=30)
@responses.activate
def test_get_sqlview_variable_query_no_dict(api, sql_view_query):  # noqa
    time.sleep(3)  # prevent ConnectionError when running concurrent CI tests
    with pytest.raises(exceptions.ClientException):
        for _ in api.get_sqlview(SQL_VIEW, var='NODICT'):
            continue


@responses.activate
def test_get_sqlview_merged(api, sql_view_query):

    r = """
dataelementid,name,valueType\n
1151060,Inpatient cases,INTEGER\n
1151042,MNCH vacuum/forceps delivery,INTEGER
"""
    responses.add(responses.GET, '{}/data.csv'.format(sql_view_query), body=r, status=200)

    expected = [
        {'dataelementid': '1151060', 'name': 'Inpatient cases', 'valueType': 'INTEGER'},
        {'dataelementid': '1151042', 'name': 'MNCH vacuum/forceps delivery', 'valueType': 'INTEGER'}
    ]
    # calling with list()
    data = list(api.get_sqlview(SQL_VIEW, var={'valueType': 'INTEGER'}))
    assert isinstance(data, list)
    assert data == expected

    # calling with merge=True
    data = api.get_sqlview(SQL_VIEW, var={'valueType': 'INTEGER'}, merge=True)
    assert isinstance(data, list)
    assert data == expected
