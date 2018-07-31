import json
import os
import shutil
import tempfile

import pytest
import requests

from .common import override_environ

from dhis2.api import Dhis, search_auth_file
from dhis2 import exceptions


@pytest.mark.parametrize("entered,expected", [
    ('https://play.dhis2.org/demo', 'https://play.dhis2.org/demo'),
    ('play.dhis2.org/demo', 'https://play.dhis2.org/demo'),
    ('localhost:8080', 'http://localhost:8080'),
    ('127.0.0.1:8080', 'http://127.0.0.1:8080'),
    ('http://localhost:8080', 'http://localhost:8080'),
    ('http://example.com', 'https://example.com'),
])
def test_api_url(entered, expected):
    api = Dhis(entered, 'admin', 'district')
    assert api.base_url == expected
    assert api.username == 'admin'
    assert '{}/api'.format(api.base_url) == '{}/api'.format(expected)


def test_base_url_with_api():
    with pytest.raises(exceptions.ClientException):
        Dhis('https://play.dhis2.org/demo/api', 'admin', 'district')


def test_base_url_api_version():
    api = Dhis('https://play.dhis2.org/demo', 'admin', 'district', 29)
    assert api.api_url == 'https://play.dhis2.org/demo/api/29'
    assert api.username == 'admin'


def test_base_url_api_version_non_integer():
    with pytest.raises(exceptions.ClientException):
        Dhis('https://play.dhis2.org/demo', 'admin', 'district', '123notanumber')


def test_base_url_api_version_below_25():
    with pytest.raises(exceptions.ClientException):
        Dhis('https://play.dhis2.org/demo', 'admin', 'district', 24)


def test_user_agent():
    api = Dhis('https://play.dhis2.org/demo', 'admin', 'district', 29, user_agent='customLib/0.0.1')
    assert 'user-agent' in api.session.headers and api.session.headers['user-agent'] == 'customLib/0.0.1'


def test_user_agent_not_set():
    api = Dhis('https://play.dhis2.org/demo', 'admin', 'district', 29)
    assert 'user-agent' in api.session.headers and api.session.headers['user-agent']


def test_session():
    api = Dhis('https://play.dhis2.org/demo', 'admin', 'district')
    assert isinstance(api.session, requests.Session)


@pytest.fixture
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
    api = Dhis.from_auth_file(location=filename)
    assert api.base_url == 'https://play.dhis2.org/demo'
    assert api.username == 'admin'


def test_from_auth_file_not_named(auth_file):
    tmp = tempfile.gettempdir()
    filename = os.path.join(tmp, 'auth_test.json')
    api = Dhis.from_auth_file(filename)
    assert api.base_url == 'https://play.dhis2.org/demo'
    assert api.username == 'admin'


@pytest.fixture
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
        Dhis.from_auth_file(location=filename)


@pytest.fixture
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
    assert api.base_url == 'https://play.dhis2.org/demo'
    assert api.username == 'admin'


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
        assert api.base_url == 'https://play.dhis2.org/demo'
        assert api.username == 'admin'


def test_from_auth_file_not_found():
    kwargs = {}
    with override_environ(**kwargs) and pytest.raises(exceptions.ClientException):
        Dhis.from_auth_file('not_here.json')


def test_search_auth_file_not_found():
    kwargs = {}
    with override_environ(**kwargs) and pytest.raises(exceptions.ClientException):
        search_auth_file('not_here.json')


def test_str():
    api = Dhis('https://play.dhis2.org/demo', 'admin', 'district')
    assert str(api).startswith('DHIS2')

