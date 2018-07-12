import os
import tempfile

import pytest

from dhis2 import exceptions
from dhis2.utils import load_csv, load_json, chunk, version_to_int


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
def test_chunk(amount, expected):
    c = chunk(amount)
    assert set(c) == set(expected)


@pytest.mark.parametrize("version,expected", [
    ("2.30", 30),
    ("2.30-SNAPSHOT", 30),
    ("2.30-RC1", 30),
    ("unknown", None)
])
def test_version_to_int(version, expected):
    assert version_to_int(version) == expected
