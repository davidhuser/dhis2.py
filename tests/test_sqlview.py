import pytest
import responses

from dhis2 import exceptions, Dhis

from .common import API_URL, BASEURL


SQL_VIEW = 'YOaOY605rzh'


@pytest.fixture  # BASE FIXTURE
def api():
    return Dhis(BASEURL, 'admin', 'district')


@pytest.fixture  # BASE FIXTURE
def api_with_api_version():
    return Dhis(BASEURL, 'admin', 'district', api_version=29)


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
            continue


def test_get_sqlview_criteria_none(api, sql_view_view):
        for _ in api.get_sqlview(SQL_VIEW, True):
            continue


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
            continue


@responses.activate
def test_get_sqlview_variable_query_no_dict(api, sql_view_query):
    with pytest.raises(exceptions.ClientException):
        for _ in api.get_sqlview(SQL_VIEW, var='NODICT'):
            continue
