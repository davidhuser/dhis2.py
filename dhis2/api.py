import json
import os

import requests

from .exceptions import ClientException, APIException
from .utils import load_json


class Dhis(object):

    def __init__(self, server, username, password, api_version=None):
        if '/api' in server:
            raise ClientException("Do not specify /api/ in baseurl")
        self.base_url = ''
        if server.startswith('localhost') or server.startswith('127.0.0.1'):
            self.base_url = 'http://{}'.format(server)
        elif server.startswith('http://'):
            self.base_url = server
        elif server.startswith('https://'):
            self.base_url = server
        else:
            self.base_url = 'https://{}'.format(server)

        if api_version:
            self.api_url = '{}/api/{}'.format(self.base_url, api_version)
        else:
            self.api_url = '{}/api'.format(self.base_url)

        self.username = username
        self._session = requests.Session()
        self._session.auth = (self.username, password)

    @property
    def session(self):
        return self._session

    @staticmethod
    def _validate_response(response):
        """
        Return if ok, raise APIException if not ok
        :param response: requests.response object
        :return: requests.response object
        """
        if response.status_code == requests.codes.ok:
            return response
        else:
            try:
                response.raise_for_status()
            except requests.RequestException:
                raise APIException(
                    code=response.status_code,
                    url=response.url,
                    description=response.text)

    def get(self, endpoint, file_type='json', params=None):
        """GET from DHIS2
        :param endpoint: DHIS2 API endpoint
        :param file_type: DHIS2 API File Type (json, xml, csv), defaults to JSON
        :param params: HTTP parameters (dict), defaults to None
        :return: requests object
        """
        url = '{}/{}.{}'.format(self.api_url, endpoint, file_type)
        r = self._session.get(url, params=params)
        return self._validate_response(r)

    def post(self, endpoint, data, params=None):
        """POST to DHIS2
        :param endpoint: DHIS2 API endpoint
        :param data: HTTP payload
        :param params: HTTP parameters (dict)
        :return: requests object
        """
        url = '{}/{}'.format(self.api_url, endpoint)
        r = self._session.post(url=url, json=data, params=params)
        return self._validate_response(r)

    def put(self, endpoint, data, params=None):
        """PUT to DHIS2
        :param endpoint: DHIS2 API endpoint
        :param data: HTTP payload
        :param params: HTTP parameters (dict)
        :return: requests object
        """
        url = '{}/{}'.format(self.api_url, endpoint)
        r = self._session.put(url=url, json=data, params=params)
        return self._validate_response(r)

    def patch(self, endpoint, data, params=None):
        """PATCH to DHIS2
        :param endpoint: DHIS2 API endpoint
        :param data: HTTP payload
        :param params: HTTP parameters (dict)
        :return: requests object
        """
        url = '{}/{}'.format(self.api_url, endpoint)
        r = self._session.patch(url=url, json=data, params=params)
        return self._validate_response(r)

    def delete(self, endpoint):
        """DELETE from DHIS2
        :param endpoint: DHIS2 API endpoint
        :return: requests object
        """
        url = '{}/{}'.format(self.api_url, endpoint)
        r = self._session.delete(url=url)
        return self._validate_response(r)

    def get_paged(self, endpoint, params=None, page_size=50):
        """GET with paging (for large payloads)
        :param page_size: how many objects per page
        :param endpoint: DHIS2 API endpoint
        :param params: HTTP parameters (dict), defaults to None
        :return: requests object
        :rtype: dict (generator)
        """
        if not params:
            params = {}
        if page_size < 1:
            raise ClientException("Can't set page_size to < 1")
        if 'paging' in params:
            raise ClientException("Can't set paging manually in params when using get_paged")
        params['pageSize'] = page_size
        params['page'] = 1
        page = self.get(endpoint=endpoint, file_type='json', params=params).json()
        yield page
        while page['pager'].get('nextPage'):
            params['page'] += 1
            page = self.get(endpoint=endpoint, file_type='json', params=params).json()
            yield page

    @classmethod
    def from_auth_file(cls, auth_file_path='', dish_filename='dish.json'):
        if not auth_file_path:
            if 'DHIS_HOME' in os.environ:
                auth_file_path = os.path.join(os.environ['DHIS_HOME'], dish_filename)
            else:
                home_path = os.path.expanduser(os.path.join('~'))
                for root, dirs, files in os.walk(home_path):
                    if dish_filename in files:
                        auth_file_path = os.path.join(root, dish_filename)
                        break
        if not auth_file_path:
            raise ClientException("'{}' not found - searched in $DHIS_HOME and in home folder".format(dish_filename))

        a = load_json(auth_file_path)
        try:
            section = a['dhis']
            baseurl = section['baseurl']
            username = section['username']
            password = section['password']
            assert all([baseurl, username, password])
        except (KeyError, AssertionError):
            raise ClientException("Auth file found but not valid: {}".format(auth_file_path))
        else:
            return cls(server=baseurl, username=username, password=password)

    def __str__(self):
        s = 'DHIS2 server: {}\n' \
            'API URL: {}\n' \
            'Username: {}'.format(self.base_url, self.api_url, self.username)
        return s

    def info(self):
        return json.dumps(self.get(endpoint='system/info').json(), indent=2)

    def dhis_version(self):
        """
        :return: DHIS2 Version as Integer (e.g. 28)
        """
        version = self.get(endpoint='system/info').json().get('version')
        if '-SNAPSHOT' in version:
            version = version.replace('-SNAPSHOT', '')
        try:
            return int(version.split('.')[1])
        except (ValueError, IndexError):
            raise ClientException("Cannot handle DHIS2 version '{}'".format(version))

    @staticmethod
    def _chunk(num, thresh=10000):
        """
        Chunk a number into a list of numbers
        :param num: the number to chunk
        :param thresh: the maximum value of a chunk
        """
        while num:
            to_yield = min(num, thresh)
            yield to_yield
            num -= to_yield

    def generate_uids(self, amount):
        """
        Create UIDs on the server
        :param amount: the number of UIDs to generate
        :return: list of UIDs
        """

        uids = []
        for limit in self._chunk(amount):
            codes = self.get('system/id', params={'limit': limit}).json()['codes']
            uids.extend(codes)
        return uids
