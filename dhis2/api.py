import codecs
from contextlib import closing

try:
    from urllib.parse import urlparse, urlunparse  # py3
except ImportError:
    from urlparse import urlparse, urlunparse  # py2

import requests

from .common import *
from .exceptions import ClientException, APIException
from .utils import load_json, chunk, search_auth_file, version_to_int


class Dhis(object):

    def __init__(self, server, username, password, api_version=None, user_agent=None):
        """
        Dhis API class
        :param server: baseurl, e.g. 'play.dhis2.org/demo'
        :param username: DHIS2 username
        :param password: DHIS2 password
        :param api_version: optional, creates a url like /api/29/schemas
        :param user_agent: optional, add user-agent to header. otherwise it uses requests' user-agent.
        """
        self._base_url, self._api_version, self._info, self._version, self._version_int, self._revision = (None,)*6

        self.base_url = server
        self.api_version = api_version

        self.session = requests.Session()
        self.username = username
        self.session.auth = (self.username, password)
        if user_agent:
            self.session.headers['user-agent'] = user_agent

    @property
    def base_url(self):
        return self._base_url

    @base_url.setter
    def base_url(self, server):
        if '/api' in server:
            raise ClientException("Do not include /api/ in the DHIS2 URL")
        o = urlparse(server)
        if 'localhost' in (o.netloc + o.path) or '127.0.0.1' in (o.netloc + o.path):  # only allow http for localhost
            scheme = 'http'
        else:
            scheme = 'https'

        if not o.scheme and not o.netloc and o.path:
            base = o.path
            path = ''
        else:
            base = o.netloc
            path = o.path
        self._base_url = urlunparse((scheme, base, path, '', '', ''))

    @property
    def api_version(self):
        return self._api_version

    @api_version.setter
    def api_version(self, number):
        if number:
            try:
                i = int(number)
                if i < 25:
                    raise ValueError
            except ValueError:
                raise ClientException("api_version must be 25 or greater: {}".format(number))
            else:
                self._api_version = i
        else:
            self._api_version = None

    @property
    def api_url(self):
        if self._api_version:
            return '{}/api/{}'.format(self._base_url, self._api_version)
        else:
            return '{}/api'.format(self._base_url)

    @property
    def info(self):
        if not self._info:
            self._info = self.get('system/info').json()
        return self._info

    @property
    def version(self):
        return self._version if self._version else self.info['version']

    @property
    def revision(self):
        return self._revision if self._revision else self.info['revision']

    @property
    def version_int(self):
        if not self._version_int:
            self._version_int = version_to_int(self.version)
        return self._version_int

    def __str__(self):
        s = "DHIS2 Base URL: '{}'\n" \
            "API URL: '{}'\n" \
            "Username: '{}'".format(self.base_url, self.api_url, self.username)
        return s

    @classmethod
    def from_auth_file(cls, location=None, api_version=None, user_agent=None):
        """
        Alternative constructor to load from JSON file.
        If auth_file_path is not specified, it tries to find `dish.json` in:
        - DHIS_HOME
        - Home folder
        :param location: authentication file path
        :param api_version: see Dhis
        :param user_agent: see Dhis
        :return: Dhis instance
        """
        location = search_auth_file() if not location else location

        a = load_json(location)
        try:
            section = a['dhis']
            baseurl = section['baseurl']
            username = section['username']
            password = section['password']
            assert all([baseurl, username, password])
        except (KeyError, AssertionError):
            raise ClientException("Auth file found but not valid: {}".format(location))
        else:
            return cls(baseurl, username, password, api_version=api_version, user_agent=user_agent)

    @staticmethod
    def _validate_response(response):
        """
        Return response if ok, raise APIException if not ok
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

    @staticmethod
    def _validate_request(endpoint, file_type='json', data=None, params=None):
        """
        Validate request before calling API
        :param endpoint: API endpoint
        :param file_type: file type requested
        :param data: payload
        :param params: HTTP parameters
        """
        if not isinstance(endpoint, string_types) or endpoint.strip() == '':
            raise ClientException("Must submit endpoint for DHIS2 API")
        if not isinstance(file_type, string_types) or file_type.lower() not in ('json', 'csv', 'xml', 'pdf', 'xlsx'):
            raise ClientException("Invalid file_type: {}".format(file_type))
        if params and not isinstance(params, dict):
            raise ClientException("params must be a dict, not {}".format(params.__class__.__name__))
        if data and not isinstance(data, dict):
            raise ClientException("data must be a dict, not {}".format(data.__class__.__name__))

    def get(self, endpoint, file_type='json', params=None, stream=False):
        """GET from DHIS2
        :param endpoint: DHIS2 API endpoint
        :param file_type: DHIS2 API File Type (json, xml, csv), defaults to JSON
        :param params: HTTP parameters (dict), defaults to None
        :param stream: use requests' stream parameter
        :return: requests object
        """
        self._validate_request(endpoint, file_type=file_type, params=params)
        url = '{}/{}.{}'.format(self.api_url, endpoint, file_type.lower())
        r = self.session.get(url, params=params, stream=stream)
        return self._validate_response(r)

    def post(self, endpoint, data=None, params=None):
        """POST to DHIS2
        :param endpoint: DHIS2 API endpoint
        :param data: HTTP payload
        :param params: HTTP parameters (dict)
        :return: requests object
        """
        self._validate_request(endpoint, data=data, params=params)
        url = '{}/{}'.format(self.api_url, endpoint)
        r = self.session.post(url=url, json=data, params=params)
        return self._validate_response(r)

    def put(self, endpoint, data, params=None):
        """PUT to DHIS2
        :param endpoint: DHIS2 API endpoint
        :param data: HTTP payload
        :param params: HTTP parameters (dict)
        :return: requests object
        """
        self._validate_request(endpoint, data=data, params=params)
        url = '{}/{}'.format(self.api_url, endpoint)
        r = self.session.put(url=url, json=data, params=params)
        return self._validate_response(r)

    def patch(self, endpoint, data, params=None):
        """PATCH to DHIS2
        :param endpoint: DHIS2 API endpoint
        :param data: HTTP payload
        :param params: HTTP parameters (dict)
        :return: requests object
        """
        self._validate_request(endpoint, data=data, params=params)
        url = '{}/{}'.format(self.api_url, endpoint)
        r = self.session.patch(url=url, json=data, params=params)
        return self._validate_response(r)

    def delete(self, endpoint):
        """DELETE from DHIS2
        :param endpoint: DHIS2 API endpoint
        :return: requests object
        """
        self._validate_request(endpoint)
        url = '{}/{}'.format(self.api_url, endpoint)
        r = self.session.delete(url=url)
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

    def get_sqlview(self, uid, execute=False, var=None, criteria=None):
        """GET SQL View data
        :param uid: sqlView UID
        :param execute: materialize sqlView before downloading its data
        :param var: for QUERY types, a dict of variables to query the sqlView
        :param criteria: for VIEW / MATERIALIZED_VIEW types, a dict of criteria to filter the sqlView
        """
        params = {}
        sqlview_type = self.get('sqlViews/{}'.format(uid), params={'fields': 'type'}).json().get('type')
        if sqlview_type == 'QUERY':
            if not isinstance(var, dict):
                raise ClientException("Use a dict to submit variables: e.g. var={'key1': 'value1', 'key2': 'value2'}")
            var = ['{}:{}'.format(k, v) for k, v in var.items()]
            params['var'] = var
            if execute:
                raise ClientException("SQL view of type QUERY, no view to create (no execute=True)")

        else:  # MATERIALIZED_VIEW / VIEW
            if criteria:
                if not isinstance(criteria, dict):
                    raise ClientException("Use a dict to submit criteria: { 'col1': 'value1', 'col2': 'value2' }")
                criteria = ['{}:{}'.format(k, v) for k, v in criteria.items()]
                params['criteria'] = criteria

            if execute:  # materialize
                self.post('sqlViews/{}/execute'.format(uid))

        with closing(self.get('sqlViews/{}/data'.format(uid), file_type='csv', params=params, stream=True)) as r:
            reader = csv.DictReader(codecs.iterdecode(r.iter_lines(), 'utf-8'), delimiter=',', quotechar='"')
            for row in reader:
                yield row

    def generate_uids(self, amount):
        """
        Create UIDs on the server
        :param amount: the number of UIDs to generate
        :return: list of UIDs
        """

        uids = []
        for limit in chunk(amount):
            codes = self.get('system/id', params={'limit': limit}).json()['codes']
            uids.extend(codes)
        return uids
