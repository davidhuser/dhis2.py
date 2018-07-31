import uuid

import pytest
import responses

from .common import API_URL, BASEURL

from dhis2 import exceptions, Dhis


@pytest.fixture  # BASE FIXTURE
def api():
    return Dhis(BASEURL, 'admin', 'district')


@pytest.fixture  # BASE FIXTURE
def api_with_api_version():
    return Dhis(BASEURL, 'admin', 'district', api_version=29)


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
            continue


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
            continue


def test_api_version(api_with_api_version):
    assert api_with_api_version.api_version == 29
    assert len(responses.calls) == 0


@responses.activate
def test_dhis_version(api):
    url = '{}/system/info.json'.format(API_URL)
    r = {'version': 'customBuild', 'revision': '80d2c77'}

    responses.add(responses.GET, url, json=r, status=200)
    assert api.version == 'customBuild'


@responses.activate
def test_dhis_version_int(api):
    url = '{}/system/info.json'.format(API_URL)
    r = {'version': '2.30', 'revision': '80d2c77'}

    responses.add(responses.GET, url, json=r, status=200)
    assert api.version_int == 30


@responses.activate
def test_dhis_revision(api):
    url = '{}/system/info.json'.format(API_URL)
    r = {'version': '2.30', 'revision': '80d2c77'}

    responses.add(responses.GET, url, json=r, status=200)
    assert api.revision == '80d2c77'
