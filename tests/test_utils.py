import os
import re
import tempfile
from types import GeneratorType

import pytest
import responses

from dhis2 import exceptions, Dhis
from dhis2.utils import (
    load_csv,
    load_json,
    chunk_number,
    partition_payload,
    version_to_int,
    create_uid
)

from .common import API_URL, BASEURL


@pytest.fixture  # BASE FIXTURE
def api():
    return Dhis(BASEURL, 'admin', 'district')


@pytest.fixture
def csv_file():
    content = [
        'abc,def',
        '1,2',
        '3,4'
    ]
    tmp = tempfile.gettempdir()
    filename = os.path.join(tmp, 'file.csv')

    import csv
    with open(filename, 'w') as f:
        w = csv.writer(f, delimiter=',')
        w.writerows([x.split(',') for x in content])
    yield filename
    os.remove(filename)


def test_load_csv(csv_file):
    expected = [
        {"abc": "1", "def": "2"},
        {"abc": "3", "def": "4"}
    ]
    tmp = tempfile.gettempdir()
    filename = os.path.join(tmp, 'file.csv')
    loaded = list(load_csv(filename))
    assert loaded == expected


def test_load_csv_not_found():
    with pytest.raises(exceptions.ClientException):
        for _ in load_csv('nothere.csv'):
            pass


def test_load_json_not_found():
    with pytest.raises(exceptions.ClientException):
        load_json('nothere.json')


@pytest.mark.parametrize("amount,expected", [
    (100, [100]),
    (10000, [10000]),
    (13000, [10000, 3000]),
    (23000, [10000, 10000, 3000])
])
def test_chunk_number(amount, expected):
    c = chunk_number(amount)
    assert set(c) == set(expected)


@pytest.mark.parametrize("payload,threshold,expected", [
    (
            {"dataElements": [1, 2, 3, 4, 5, 6, 7, 8]},
            3,
            [
                {"dataElements": [1, 2, 3]},
                {"dataElements": [4, 5, 6]},
                {"dataElements": [7, 8]}
            ]
    ),
    (
            {"dataElements": [1, 2, 3, 4, 5, 6, 7, 8]},
            9,
            [
                {"dataElements": [1, 2, 3, 4, 5, 6, 7, 8]}
            ]
    )
])
def test_partition_payload(payload, threshold, expected):
    key = 'dataElements'
    c_gen = partition_payload(payload, key, threshold)
    assert isinstance(c_gen, GeneratorType)
    assert list(c_gen) == expected


@pytest.mark.parametrize("version,expected", [
    ("2.30", 30),
    ("2.30-SNAPSHOT", 30),
    ("2.30-RC1", 30),
    ("unknown", None)
])
def test_version_to_int(version, expected):
    assert version_to_int(version) == expected


@responses.activate
def test_generate_uids(api):
    amount = 13000
    url = '{}/system/id.json'.format(API_URL, amount)

    responses.add_passthru(url)
    uids = api.generate_uids(amount)
    assert isinstance(uids, list)
    assert len(uids) == amount


@responses.activate
def test_generate_uids_locally(api):
    amount = 1000
    uids = api.generate_uids(amount, local=True)
    assert isinstance(uids, list)
    assert len(uids) == amount
    assert len(set(uids)) == len(uids)
    assert len(responses.calls) == 0


@pytest.mark.parametrize("amount", [
    None, -1, 0, 100.5
])
def test_generate_uids_amount_not_int(api, amount):
    with pytest.raises(exceptions.ClientException):
        api.generate_uids(amount)


def test_create_uids():
    uid_regex = r"^[A-Za-z][A-Za-z0-9]{10}$"
    assert all([re.match(uid_regex, uid) for uid in [create_uid() for _ in range(100000)]])
