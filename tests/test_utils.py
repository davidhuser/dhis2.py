# -*- coding: utf-8 -*-

import csv
import os
import re
import sys
import tempfile
from types import GeneratorType

import pytest
from requests import Response

from dhis2 import exceptions, Api
from dhis2.exceptions import ClientException
from dhis2.utils import (
    load_csv,
    load_json,
    partition_payload,
    version_to_int,
    generate_uid,
    is_valid_uid,
    pretty_json,
    clean_obj,
    import_response_ok
)
from .common import BASEURL


@pytest.fixture  # BASE FIXTURE
def api():
    return Api(BASEURL, "admin", "district")


@pytest.fixture
def csv_file():
    content = ["abc,def", "1,2", "3,4", "ñ,äü"]
    tmp = tempfile.gettempdir()
    filename = os.path.join(tmp, "file.csv")
    with open(filename, "w") as f:
        w = csv.writer(f, delimiter=",")
        w.writerows([x.split(",") for x in content])
    yield filename
    os.remove(filename)


def test_load_csv(csv_file):
    expected = [
        {u"abc": u"1", "def": u"2"},
        {u"abc": u"3", "def": u"4"},
        {u"abc": u"ñ", "def": u"äü"},
    ]
    tmp = tempfile.gettempdir()
    filename = os.path.join(tmp, "file.csv")
    loaded = list(load_csv(filename))
    assert loaded == expected
    for d in loaded:
        for k, v in d.items():
            assert isinstance(k, str) and isinstance(v, str)


def test_load_csv_not_found():
    with pytest.raises(exceptions.ClientException):
        for _ in load_csv("nothere.csv"):
            pass


def test_load_json_not_found():
    with pytest.raises(exceptions.ClientException):
        load_json("nothere.json")


@pytest.mark.parametrize(
    "payload,threshold,expected",
    [
        (
            {"dataElements": [1, 2, 3, 4, 5, 6, 7, 8]},
            3,
            [
                {"dataElements": [1, 2, 3]},
                {"dataElements": [4, 5, 6]},
                {"dataElements": [7, 8]},
            ],
        ),
        (
            {"dataElements": [1, 2, 3, 4, 5, 6, 7, 8]},
            9,
            [{"dataElements": [1, 2, 3, 4, 5, 6, 7, 8]}],
        ),
    ],
)
def test_partition_payload(payload, threshold, expected):
    key = "dataElements"
    c_gen = partition_payload(payload, key, threshold)
    assert isinstance(c_gen, GeneratorType)
    assert list(c_gen) == expected


@pytest.mark.parametrize(
    "version,expected",
    [
        ("2.30", 30),
        ("2.30-SNAPSHOT", 30),
        ("2.30-RC1", 30),
        ("2.31.1", 31),
        ("2.31.2", 31),
        ("unknown", None),
    ],
)
def test_version_to_int(version, expected):
    assert version_to_int(version) == expected


def test_generate_uids():
    uid_regex = r"^[A-Za-z][A-Za-z0-9]{10}$"
    assert all(
        [re.match(uid_regex, uid) for uid in [generate_uid() for _ in range(100000)]]
    )


@pytest.mark.parametrize(
    "uid_list,result",
    [
        ({"RAQaLoYJEuS", "QTIquqiULFK", "NqkDeV7vRTK", "NyghHtH5oNm"}, True),
        ({"RAQaLoYJEu", "", None, 123456}, False),
    ],
)
def test_is_uid(uid_list, result):
    assert all([is_valid_uid(uid) is result for uid in uid_list])


@pytest.mark.parametrize(
    "obj",
    [
        {"data": [1, 2, 3]},
        '{"pager": {"page": 1}}',
    ],
)
def test_pretty_json(capsys, obj):
    pretty_json(obj)
    out, err = capsys.readouterr()
    sys.stdout.write(out)
    sys.stderr.write(err)
    assert out.startswith("{")


@pytest.mark.parametrize("obj", ["", '{"pager": {"page": }}'])
def test_pretty_json_not_json_string(obj):
    with pytest.raises(exceptions.ClientException):
        pretty_json(obj)


@pytest.mark.parametrize(
    "obj,key_to_clean,expected",
    [
        (  # remove sharing
            {
                "dataElements": [
                    {"id": "abc", "publicAccess": "1", "userGroupAccesses": [1, 2, 3]}
                ]
            },
            ["userGroupAccesses"],
            {
                "dataElements": [
                    {
                        "id": "abc",
                        "publicAccess": "1",
                    }
                ]
            },
        ),
        (  # nested dict still works
            {
                "dataElements": [
                    {
                        "id": "abc",
                        "publicAccess": "1",
                        "userGroupAccesses": [{"userGroupAccesses": [1, 2, 3]}],
                    }
                ]
            },
            ["userGroupAccesses"],
            {
                "dataElements": [
                    {
                        "id": "abc",
                        "publicAccess": "1",
                    }
                ]
            },
        ),
        (  # works even with `remove` being just a string
            {
                "dataElements": [
                    {"id": "abc", "publicAccess": "1", "userGroupAccesses": [1, 2, 3]}
                ]
            },
            "userGroupAccesses",
            {
                "dataElements": [
                    {
                        "id": "abc",
                        "publicAccess": "1",
                    }
                ]
            },
        ),
        (  # works with no keys matching
            {
                "dataElements": [
                    {
                        "id": "abc",
                        "publicAccess": "1",
                    }
                ]
            },
            "notHere",
            {
                "dataElements": [
                    {
                        "id": "abc",
                        "publicAccess": "1",
                    }
                ]
            },
        ),
        ({}, {}, {}),
        ({}, "justChecking", {}),
        (None, "hello", None),
        ([[1, 3], (1, 2), [3]]),
    ],
)
def test_remove_keys(obj, key_to_clean, expected):
    assert clean_obj(obj, key_to_clean) == expected


@pytest.mark.parametrize(
    "obj,key_to_clean,expected",
    [
        ([1, None, 1]),
        ({"a": 1, "b": 2}, None, "_"),
        ({None: 1, "b": 2}, None, "_"),
        (None, None, None),
    ],
)
def test_remove_keys_invalid(obj, key_to_clean, expected):
    with pytest.raises(exceptions.ClientException):
        _ = clean_obj(obj, key_to_clean) == expected


def test_import_response_ok_status_error():
    response = {
        "description": "The import process failed: java.lang.String cannot be cast to java.lang.Boolean",
        "importCount": {
            "deleted": 0,
            "ignored": 0,
            "imported": 0,
            "updated": 0
        },
        "responseType": "ImportSummary",
        "status": "ERROR"
    }
    assert import_response_ok(response) is False


def test_import_response_ok_count_ignored():
    response = {
        "description": "The import process failed: java.lang.String cannot be cast to java.lang.Boolean",
        "importCount": {
            "deleted": 0,
            "ignored": 1,
            "imported": 0,
            "updated": 0
        },
        "responseType": "ImportSummary",
        "status": "SUCCESS"
    }
    assert import_response_ok(response) is False


def test_import_response_ok_no_change():
    response = {
        "description": "The import process failed: java.lang.String cannot be cast to java.lang.Boolean",
        "importCount": {
            "deleted": 0,
            "ignored": 0,
            "imported": 0,
            "updated": 0
        },
        "responseType": "ImportSummary",
        "status": "SUCCESS"
    }
    assert import_response_ok(response) is False


def test_import_response_ok_status_success():
    response = {
        "description": "The import process failed: java.lang.String cannot be cast to java.lang.Boolean",
        "importCount": {
            "deleted": 0,
            "ignored": 0,
            "imported": 0,
            "updated": 1
        },
        "responseType": "ImportSummary",
        "status": "SUCCESS"
    }
    assert import_response_ok(response) is True


def test_import_response_ok_status_ok():
    response = {
        "description": "Status ok",
        "importCount": {
            "deleted": 0,
            "ignored": 0,
            "imported": 0,
            "updated": 1
        },
        "responseType": "ImportSummary",
        "status": "OK"
    }
    assert import_response_ok(response) is True


def test_import_response_ok_metadata():
    response = {
        "stats": {
            "created": 0,
            "deleted": 0,
            "ignored": 0,
            "total": 1,
            "updated": 1
        },
        "status": "OK",
        "typeReports": [
            {
                "klass": "org.hisp.dhis.dataset.DataSet",
                "objectReports": [],
                "stats": {
                    "created": 0,
                    "deleted": 0,
                    "ignored": 0,
                    "total": 1,
                    "updated": 1
                }
            }
        ]
    }
    assert import_response_ok(response)

def test_import_response_ok_event():
    response = {
        "deleted": 0,
        "ignored": 13,
        "importSummaries": [
            {
                "conflicts": [],
                "description": "Event.orgUnit does not point to a valid organisation unit: bS2F7wCpPsj",
                "importCount": {
                    "deleted": 0,
                    "ignored": 1,
                    "imported": 0,
                    "updated": 0
                },
                "reference": "GL5ef5j2rX5",
                "responseType": "ImportSummary",
                "status": "ERROR"
            },
            {
                "conflicts": [],
                "description": "Event.orgUnit does not point to a valid organisation unit: bS2F7wCpPsj",
                "importCount": {
                    "deleted": 0,
                    "ignored": 1,
                    "imported": 0,
                    "updated": 0
                },
                "reference": "dyXsEQMOlTd",
                "responseType": "ImportSummary",
                "status": "ERROR"
            }
        ],
        "imported": 0,
        "responseType": "ImportSummaries",
        "status": "ERROR",
        "total": 13,
        "updated": 0
    }
    assert import_response_ok(response) is False


def test_import_response_ok_tracked_entity_instances():
    response = {
        "httpStatus": "Conflict",
        "httpStatusCode": 409,
        "message": "An error occurred, please check import summary.",
        "response": {
            "deleted": 0,
            "ignored": 1,
            "importSummaries": [
                {
                    "conflicts": [
                        {
                            "object": "OrganisationUnit",
                            "value": "Org unit ImspTQwCqd does not exist"
                        }
                    ],
                    "enrollments": {
                        "deleted": 0,
                        "ignored": 0,
                        "importSummaries": [],
                        "imported": 0,
                        "responseType": "ImportSummaries",
                        "status": "SUCCESS",
                        "total": 0,
                        "updated": 0
                    },
                    "importCount": {
                        "deleted": 0,
                        "ignored": 1,
                        "imported": 0,
                        "updated": 0
                    },
                    "reference": "AHgGHO6ZH9b",
                    "responseType": "ImportSummary",
                    "status": "ERROR"
                }
            ],
            "imported": 0,
            "responseType": "ImportSummaries",
            "status": "ERROR",
            "total": 5,
            "updated": 4
        },
        "status": "ERROR"
}
    assert import_response_ok(response) is False


@pytest.mark.parametrize("response", [
    {"no status": "hello"},
    False,
    None,
    {"status": [1, 2, 3]},
    {"status": {"importCount"}},
    {1: 3}
])
def test_import_response_ok_invalid_response(response):
    with pytest.raises(ClientException):
        import_response_ok(response)
