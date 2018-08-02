import uuid

import pytest
import responses

from dhis2 import exceptions, Dhis
from .common import API_URL, BASEURL


@pytest.fixture  # BASE FIXTURE
def api():
    return Dhis(BASEURL, 'admin', 'district')


@pytest.fixture  # BASE FIXTURE
def api_with_api_version():
    return Dhis(BASEURL, 'admin', 'district', api_version=29)


@pytest.mark.parametrize("endpoint,page_size,no_of_pages,expected_amount", [
    ('organisationUnits', 1000, 3, 2005),
    ('events', 50, 6, 255),
    ('trackedEntityInstances', 50, 1, 50),
    ('enrollments', 50, 6, 255),
    ('events/query', 50, 6, 255),
    ('trackedEntityInstances/query', 50, 6, 255)
])
@responses.activate
def test_get_paged_merge(api, endpoint, page_size, no_of_pages, expected_amount):

    overflow = 5
    collection = endpoint.split('/')[0]

    # one page response
    if no_of_pages == 1:
        r = {
            "pager": {
                "page": 1,
                "pageCount": expected_amount,
                "total": expected_amount,
                "pageSize": page_size
            },
            "organisationUnits": [str(uuid.uuid4()) for _ in range(expected_amount)]
        }
        url = '{}/{}.json?pageSize={}&totalPages=true&page=1'.format(API_URL, endpoint, page_size)
        responses.add(responses.GET, url, json=r, status=200)

    # multi-page response
    else:
        # normal page (=> amount of objects is equal to page size)
        for i in range(1, no_of_pages):
            r = {
                "pager": {
                    "page": i,
                    "pageCount": no_of_pages,
                    "total": expected_amount,
                    "pageSize": page_size
                },
                collection: [str(uuid.uuid4()) for _ in range(page_size)]
            }
            url = '{}/{}.json?pageSize={}&totalPages=true&page={}'.format(API_URL, endpoint, page_size, i)
            responses.add(responses.GET, url, json=r, status=200)

        # last page containing only 5 objects (overflow value)
        last_amount = page_size - overflow
        last_page = {
            "pager": {
                "page": no_of_pages,
                "pageCount": last_amount,
                "total": expected_amount,
                "pageSize": page_size
            },
            collection: [str(uuid.uuid4()) for _ in range(overflow)]
        }
        url = '{}/{}.json?pageSize={}&totalPages=true&page={}'.format(API_URL, endpoint, page_size, no_of_pages)
        responses.add(responses.GET, url, json=last_page, status=200)

        data = api.get_paged(endpoint, merge=True)
        assert len(data[collection]) == expected_amount
        assert len(responses.calls) == no_of_pages


@pytest.mark.parametrize("endpoint,page_size,no_of_pages,expected_amount", [
    ('organisationUnits', 1000, 3, 2005),
    ('events', 50, 6, 255),
    ('trackedEntityInstances', 50, 1, 50),
    ('enrollments', 50, 6, 255),
    ('events/query', 50, 6, 255),
    ('trackedEntityInstances/query', 50, 6, 255)
])
@responses.activate
def test_get_paged_generator(api, endpoint, page_size, no_of_pages, expected_amount):

    overflow = 5
    collection = endpoint.split('/')[0]

    # one page response
    if no_of_pages == 1:
        r = {
            "pager": {
                "page": 1,
                "pageCount": expected_amount,
                "total": expected_amount,
                "pageSize": page_size
            },
            "organisationUnits": [str(uuid.uuid4()) for _ in range(expected_amount)]
        }
        url = '{}/{}.json?pageSize={}&totalPages=true&page=1'.format(API_URL, endpoint, page_size)
        responses.add(responses.GET, url, json=r, status=200)

    # multi-page response
    else:
        # normal page (=> amount of objects is equal to page size)
        for i in range(1, no_of_pages):
            r = {
                "pager": {
                    "page": i,
                    "pageCount": no_of_pages,
                    "total": expected_amount,
                    "pageSize": page_size
                },
                collection: [str(uuid.uuid4()) for _ in range(page_size)]
            }
            url = '{}/{}.json?pageSize={}&totalPages=true&page={}'.format(API_URL, endpoint, page_size, i)
            responses.add(responses.GET, url, json=r, status=200)

        # last page containing only 5 objects (overflow value)
        last_amount = page_size - overflow
        last_page = {
            "pager": {
                "page": no_of_pages,
                "pageCount": last_amount,
                "total": expected_amount,
                "pageSize": page_size
            },
            collection: [str(uuid.uuid4()) for _ in range(overflow)]
        }
        url = '{}/{}.json?pageSize={}&totalPages=true&page={}'.format(API_URL, endpoint, page_size, no_of_pages)
        responses.add(responses.GET, url, json=last_page, status=200)

        counter = 0
        uid_list = []
        for page in api.get_paged(endpoint, page_size=page_size, merge=False):
            counter += len(page[collection])
            uid_list.extend(page[collection])
        assert counter == expected_amount
        assert len(set(uid_list)) == len(uid_list)
        assert len(responses.calls) == no_of_pages


@responses.activate
def test_get_paged_empty(api):
    page_size = 50

    first_page = {
        "pager": {
            "page": 1,
            "pageCount": 1,
            "total": 0,
            "pageSize": page_size
        },
        "organisationUnits": []
    }
    url = '{}/organisationUnits.json?pageSize={}&totalPages=true&page=1'.format(API_URL, page_size)
    responses.add(responses.GET, url, json=first_page, status=200)

    data = api.get_paged('organisationUnits', page_size=50, merge=True)

    assert len(data['organisationUnits']) == 0
    assert len(responses.calls) == 1


@responses.activate
def test_page_size_zero(api):
    with pytest.raises(exceptions.ClientException):
        api.get_paged('organisationUnits', page_size=0)


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
        api.get_paged('organisationUnits', params=params)
