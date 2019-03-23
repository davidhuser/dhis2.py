import json
import os
import shutil
import tempfile

import pytest
import requests
import responses

from .common import BASEURL, API_URL, override_environ

from dhis2.api import Api, search_auth_file
from dhis2 import exceptions


@pytest.fixture  # BASE FIXTURE
def api():
    return Api(BASEURL, 'admin', 'district')


@pytest.fixture  # BASE FIXTURE
def api_with_api_version():
    return Api(BASEURL, 'admin', 'district', api_version=30)


@pytest.mark.parametrize("entered,expected", [
    ('https://play.dhis2.org/demo ', 'https://play.dhis2.org/demo'),  # strip whitespace
    ('https://play.dhis2.org/demo', 'https://play.dhis2.org/demo'),  # standard url
    ('play.dhis2.org/demo', 'https://play.dhis2.org/demo'),  # url w/o scheme to go as https://
    ('localhost:8080', 'http://localhost:8080'),  # localhost to use http
    ('127.0.0.1:8080', 'http://127.0.0.1:8080'),  # localhost to use http
    ('localhost:8080/dhis', 'http://localhost:8080/dhis'),  # localhost works with additional path
    ('http://1.2.3.4', 'http://1.2.3.4'),  # public IP to use provided scheme http
    ('https://1.2.3.4', 'https://1.2.3.4'),  # public IP to use provided scheme https
    ('http://localhost:8080', 'http://localhost:8080'),  # localhost to use provided scheme http
    ('https://localhost:8080', 'https://localhost:8080'),  # localhost to use provided scheme https
    ('http://example.com', 'http://example.com'),  # public addresses to use provided scheme http
    ('https://example.com', 'https://example.com'),  # public addresses to use provided scheme https
])
def test_api_url(entered, expected):
    api = Api(entered, 'admin', 'district')
    assert api.base_url == expected
    assert api.username == 'admin'
    assert '{}/api'.format(api.base_url) == '{}/api'.format(expected)


def test_base_url_with_api():
    with pytest.raises(exceptions.ClientException):
        Api('https://play.dhis2.org/demo/api', 'admin', 'district')


def test_base_url_api_version():
    api = Api('https://play.dhis2.org/demo', 'admin', 'district', 30)
    assert api.api_url == 'https://play.dhis2.org/demo/api/30'
    assert api.username == 'admin'


def test_base_url_api_version_non_integer():
    with pytest.raises(exceptions.ClientException):
        Api('https://play.dhis2.org/demo', 'admin', 'district', '123notanumber')


def test_base_url_api_version_below_25():
    with pytest.raises(exceptions.ClientException):
        Api('https://play.dhis2.org/demo', 'admin', 'district', 24)


def test_user_agent():
    api = Api('https://play.dhis2.org/demo', 'admin', 'district', 30, user_agent='customLib/0.0.1')
    assert 'user-agent' in api.session.headers and api.session.headers['user-agent'] == 'customLib/0.0.1'


def test_user_agent_not_set():
    api = Api('https://play.dhis2.org/demo', 'admin', 'district', 30)
    assert 'user-agent' in api.session.headers and api.session.headers['user-agent']


def test_session():
    api = Api('https://play.dhis2.org/demo', 'admin', 'district')
    assert isinstance(api.session, requests.Session)


def test_api_version(api_with_api_version):
    assert api_with_api_version.api_version == 30
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
    api = Api.from_auth_file(location=filename)
    assert api.base_url == 'https://play.dhis2.org/demo'
    assert api.username == 'admin'


def test_from_auth_file_not_named(auth_file):
    tmp = tempfile.gettempdir()
    filename = os.path.join(tmp, 'auth_test.json')
    api = Api.from_auth_file(filename)
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
        Api.from_auth_file(location=filename)


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
    api = Api.from_auth_file()
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
        api = Api.from_auth_file()
        assert api.base_url == 'https://play.dhis2.org/demo'
        assert api.username == 'admin'


def test_from_auth_file_not_found():
    kwargs = {}
    with override_environ(**kwargs) and pytest.raises(exceptions.ClientException):
        Api.from_auth_file('not_here.json')


def test_search_auth_file_not_found():
    kwargs = {}
    with override_environ(**kwargs) and pytest.raises(exceptions.ClientException):
        search_auth_file('not_here.json')


def test_str():
    api = Api('https://play.dhis2.org/demo', 'admin', 'district')
    assert str(api).startswith('DHIS2')

