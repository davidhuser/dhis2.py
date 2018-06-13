import json
import os
import shutil
import contextlib
import tempfile

import pytest
import requests

from dhis2 import Dhis, exceptions


@contextlib.contextmanager
def override_environ(**kwargs):
    save_env = dict(os.environ)
    for key, value in kwargs.items():
        if value is None:
            del os.environ[key]
        else:
            os.environ[key] = value
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(save_env)


@pytest.mark.parametrize("entered,expected", [
    ('https://play.dhis2.org/demo', 'https://play.dhis2.org/demo'),
    ('play.dhis2.org/demo', 'https://play.dhis2.org/demo'),
    ('localhost:8080', 'http://localhost:8080'),
    ('127.0.0.1:8080', 'http://127.0.0.1:8080'),
    ('http://localhost:8080', 'http://localhost:8080'),
    ('http://example.com', 'http://example.com'),
])
def test_api_url(entered, expected):
    api = Dhis(entered, 'admin', 'district')
    assert api.base_url == expected
    assert '{}/api'.format(api.base_url) == '{}/api'.format(expected)


def test_base_url_with_api():
    with pytest.raises(exceptions.ClientException):
        Dhis('https://play.dhis2.org/demo/api', 'admin', 'district')


def test_base_url_api_version():
    api = Dhis('https://play.dhis2.org/demo', 'admin', 'district', 29)
    assert api.api_url == 'https://play.dhis2.org/demo/api/29'


def test_session():
    api = Dhis('https://play.dhis2.org/demo', 'admin', 'district')
    assert isinstance(api.session, requests.Session)


@pytest.fixture()
def auth_file():
    content = {
        "dhis": {
            "baseurl": "https://play.dhis2.org/demo",
            "username": "admin",
            "password": "district"
        }
    }
    tmp = tempfile.gettempdir()
    filename = os.path.join(tmp, 'auth_test.json')
    with open(filename, 'w') as f:
        json.dump(content, f)
    yield filename
    os.remove(filename)


def test_from_auth_file_named(auth_file):
    tmp = tempfile.gettempdir()
    filename = os.path.join(tmp, 'auth_test.json')
    api = Dhis.from_auth_file(auth_file_path=filename)
    assert api.base_url == "https://play.dhis2.org/demo"


def test_from_auth_file_not_named(auth_file):
    tmp = tempfile.gettempdir()
    filename = os.path.join(tmp, 'auth_test.json')
    api = Dhis.from_auth_file(filename)
    assert api.base_url == "https://play.dhis2.org/demo"

@pytest.fixture()
def auth_file_invalid():
    content = {
        "dhis": {
            "username": "admin",
            "password": "district"
        }
    }
    tmp = tempfile.gettempdir()
    filename = os.path.join(tmp, 'auth_test_invalid.json')
    with open(filename, 'w') as f:
        json.dump(content, f)
    yield filename
    os.remove(filename)


def test_from_auth_file_not_valid(auth_file_invalid):
    with pytest.raises(exceptions.ClientException):
        tmp = tempfile.gettempdir()
        filename = os.path.join(tmp, 'auth_test_invalid.json')
        Dhis.from_auth_file(auth_file_path=filename)


@pytest.fixture()
def auth_file_home():
    content = {
        "dhis": {
            "baseurl": "https://play.dhis2.org/demo",
            "username": "admin",
            "password": "district"
        }
    }
    filename = os.path.join(os.path.expanduser(os.path.join('~')), 'dish.json')
    with open(filename, 'w') as f:
        json.dump(content, f)
    yield filename
    os.remove(filename)


def test_from_auth_file_in_home(auth_file_home):
    api = Dhis.from_auth_file()
    assert api.base_url == "https://play.dhis2.org/demo"


@pytest.fixture
def auth_file_in_dhishome():
    content = {
        "dhis": {
            "baseurl": "https://play.dhis2.org/demo",
            "username": "admin",
            "password": "district"
        }
    }
    home = os.path.join(os.path.expanduser(os.path.join('~')))
    dhis_home = os.path.join(home, 'tomcat-dhis-test-524')
    if not os.path.exists(dhis_home):
        os.mkdir(dhis_home)

    filename = os.path.join(dhis_home, 'dish.json')
    with open(filename, 'w') as f:
        json.dump(content, f)

    yield filename

    os.remove(filename)
    shutil.rmtree(dhis_home)


def test_from_auth_file_in_dhishome(auth_file_in_dhishome):
    home = os.path.join(os.path.expanduser(os.path.join('~')))
    dhis_home = os.path.join(home, 'tomcat-dhis-test-524')
    kwargs = {'DHIS_HOME': dhis_home}
    with override_environ(**kwargs):
        api = Dhis.from_auth_file()
        assert api.base_url == "https://play.dhis2.org/demo"


def test_from_auth_file_not_found():
    kwargs = {}
    with override_environ(**kwargs) and pytest.raises(exceptions.ClientException):
        Dhis.from_auth_file(dish_filename='nothere.json')


def test_str():
    api = Dhis('https://play.dhis2.org/demo', 'admin', 'district')
    expected = 'DHIS2 server: https://play.dhis2.org/demo\n' \
               'API URL: https://play.dhis2.org/demo/api\n' \
               'Username: admin'
    assert str(api) == expected

