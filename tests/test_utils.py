import os

import pytest

from dhis2 import exceptions, load_csv, load_json


@pytest.fixture
def csv_file():
    content = [
        'abc,def',
        '1,2',
        '3,4'
    ]
    filename = '/tmp/file.csv'
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
    loaded = list(load_csv('/tmp/file.csv'))
    assert loaded == expected


def test_load_csv_not_found():
    with pytest.raises(exceptions.ClientException):
        for _ in load_csv('nothere.csv'):
            pass


def test_load_json_not_found():
    with pytest.raises(exceptions.ClientException):
        load_json('nothere.json')
