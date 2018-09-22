import codecs
from contextlib import closing
from itertools import chain

try:
    from urllib.parse import urlparse, urlunparse  # py3
except ImportError:
    from urlparse import urlparse, urlunparse  # py2

import requests

from .common import *
from .exceptions import ClientException, APIException
from .utils import (
    load_json,
    chunk_number,
    partition_payload,
    search_auth_file,
    version_to_int
)


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
            raise ClientException("Do not include /api/ in the DHIS2 server argument")

        server = server.strip()

        is_local = 'localhost' in server or '127.0.0.1' in server
        has_scheme = '://' in server

        # add http / https schemes when missing
        if is_local and not has_scheme:
            url = 'http://{}'.format(server)
        elif not is_local and not has_scheme:
            url = 'https://{}'.format(server)
        else:
            url = server

        o = urlparse(url)
        self._base_url = urlunparse((o.scheme, o.netloc, o.path, '', '', ''))

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
        if params:
            if not isinstance(params, (dict, list)):
                raise ClientException("params must be a dict or list of tuples, not {}".format(params.__class__.__name__))
            if isinstance(params, list) and not all([isinstance(elem, tuple) for elem in params]):
                raise ClientException("params list must all be tuples")
        if data and not isinstance(data, dict):
            raise ClientException("data must be a dict, not {}".format(data.__class__.__name__))

    def _make_request(self, method, endpoint, **kwargs):
        if isinstance(kwargs.get('file_type'), string_types):
            file_type = kwargs['file_type'].lower()
        else:
            file_type = 'json'
        params = kwargs.get('params')

        data = kwargs.get('data', kwargs.get('json', None))
        url = '{}/{}'.format(self.api_url, endpoint)
        self._validate_request(endpoint, file_type, data, params)

        if method == 'get':
            stream = kwargs.get('stream', False)
            url = '{}.{}'.format(url, file_type)
            r = self.session.get(url, params=params, stream=stream)

        elif method == 'post':
            r = self.session.post(url=url, json=data, params=params)

        elif method == 'put':
            r = self.session.put(url=url, json=data, params=params)

        elif method == 'patch':
            r = self.session.patch(url=url, json=data, params=params)

        elif method == 'delete':
            r = self.session.delete(url=url)

        else:
            raise ClientException("Non-supported HTTP method: {}".format(method))

        return self._validate_response(r)

    def get(self, endpoint, file_type='json', params=None, stream=False):
        """GET from DHIS2
        :param endpoint: DHIS2 API endpoint
        :param file_type: DHIS2 API File Type (json, xml, csv), defaults to JSON
        :param params: HTTP parameters (dict), defaults to None
        :param stream: use requests' stream parameter
        :return: requests object
        """
        return self._make_request('get', endpoint, params=params, file_type=file_type, stream=stream)

    def post(self, endpoint, json=None, params=None, **kwargs):
        """POST to DHIS2
        :param endpoint: DHIS2 API endpoint
        :param json: HTTP payload
        :param params: HTTP parameters (dict)
        :return: requests object
        """
        json = kwargs['data'] if 'data' in kwargs else json
        return self._make_request('post', endpoint, data=json, params=params)

    def put(self, endpoint, json=None, params=None, **kwargs):
        """PUT to DHIS2
        :param endpoint: DHIS2 API endpoint
        :param json: HTTP payload
        :param params: HTTP parameters (dict)
        :return: requests object
        """
        json = kwargs['data'] if 'data' in kwargs else json
        return self._make_request('put', endpoint, data=json, params=params)

    def patch(self, endpoint, json=None, params=None, **kwargs):
        """PATCH to DHIS2
        :param endpoint: DHIS2 API endpoint
        :param json: HTTP payload
        :param params: HTTP parameters (dict)
        :return: requests object
        """
        json = kwargs['data'] if 'data' in kwargs else json
        return self._make_request('patch', endpoint, data=json, params=params)

    def delete(self, endpoint):
        """DELETE from DHIS2
        :param endpoint: DHIS2 API endpoint
        :return: requests object
        """
        return self._make_request('delete', endpoint)

    def get_paged(self, endpoint, params=None, page_size=50, merge=False):
        """GET with paging (for large payloads).
        :param page_size: how many objects per page
        :param endpoint: DHIS2 API endpoint
        :param params: HTTP parameters (dict), defaults to None
        :param merge: If true, return a list containing all pages instead of one page. Defaults to False.
        :return: normal DHIS2 response dict, e.g. {"organisationUnits": [...]}
        """
        try:
            if not isinstance(page_size, (string_types, int)) or int(page_size) < 1:
                raise ValueError
        except ValueError:
            raise ClientException("page_size must be > 1")

        params = {} if not params else params
        if 'paging' in params:
            raise ClientException("Can't set paging manually in params when using get_paged")
        params['pageSize'] = page_size
        params['page'] = 1
        params['totalPages'] = True

        collection = endpoint.split('/')[0]  # only use e.g. events when submitting events/query as endpoint

        def page_generator():
            page = self.get(endpoint=endpoint, file_type='json', params=params).json()
            page_count = page['pager']['pageCount']
            yield page

            while page['pager']['page'] < page_count:
                params['page'] += 1
                page = self.get(endpoint=endpoint, file_type='json', params=params).json()
                yield page

        if not merge:
            return page_generator()
        else:
            data = []
            for p in page_generator():
                data.append(p[collection])
            return {collection: list(chain.from_iterable(data))}

    def get_sqlview(self, uid, execute=False, var=None, criteria=None, merge=False):
        """GET SQL View data
        :param uid: sqlView UID
        :param execute: materialize sqlView before downloading its data
        :param var: for QUERY types, a dict of variables to query the sqlView
        :param criteria: for VIEW / MATERIALIZED_VIEW types, a dict of criteria to filter the sqlView
        :param merge: If true, return a list containing all pages instead of one page. Defaults to False.
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

        def page_generator():
            with closing(self.get('sqlViews/{}/data'.format(uid), file_type='csv', params=params, stream=True)) as r:
                reader = csv.DictReader(codecs.iterdecode(r.iter_lines(), 'utf-8'), delimiter=',', quotechar='"')
                for row in reader:
                    yield row

        if not merge:
            return page_generator()
        else:
            return list(page_generator())

    def post_partitioned(self, endpoint, json, params=None, thresh=1000):
        """
        Post a payload in chunks to prevent 'Request Entity Too Large' Timeout errors
        :param endpoint: the API endpoint to use
        :param json: payload dict
        :param params: request parameters
        :param thresh: the maximum amount to partition into
        :yield: response objects
        """

        if not isinstance(json, dict) or len(json.keys()) != 1:
            raise ClientException('Must submit exactly one key in payload (which needs to be a dict)'
                                  ' - e.g. json={"dataElements": [...]"}')
        if not isinstance(thresh, int) or thresh < 2:
            raise ClientException("thresh must be integer of 2 or larger")

        key = next(iter(json))  # the (only) key in the payload
        if not json[key]:
            raise ClientException("payload for key '{}' is empty".format(key))

        for data in partition_payload(data=json, key=key, thresh=thresh):
            yield self.post(endpoint, json=data, params=params)

    def generate_uids(self, amount):
        """
        Create UIDs on the server
        :param amount: the number of UIDs to generate
        :return: list of UIDs
        """

        uids = []
        for limit in chunk_number(amount):
            codes = self.get('system/id', params={'limit': limit}).json()['codes']
            uids.extend(codes)
        return uids
