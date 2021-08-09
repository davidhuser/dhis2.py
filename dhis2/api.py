# -*- coding: utf-8 -*-

"""
dhis2.api
~~~~~~~~~

This module implements DHIS2 API operations via the Api class.
"""

import codecs
from contextlib import closing
from itertools import chain
from typing import Union, Optional, Generator, List, Any, Iterator

from urllib.parse import urlparse, urlunparse

import requests
from csv import DictReader

from .exceptions import ClientException, RequestException
from .utils import load_json, partition_payload, search_auth_file, version_to_int


class Api(object):
    """A Python interface to the DHIS2 API

    Example usage:

    from dhis2 import Api

    api = Api('play.dhis2.org/demo', 'admin', 'district')

    """

    def __init__(
        self,
        server: str,
        username: str,
        password: str,
        api_version: Union[int, str] = None,
        user_agent: str = None,
    ) -> None:
        """

        :param server: baseurl, e.g. 'play.dhis2.org/demo'
        :param username: DHIS2 username
        :param password: DHIS2 password
        :param api_version: optional, creates a url like /api/29/schemas
        :param user_agent: optional, add user-agent to header. otherwise it uses requests' user-agent.
        """
        (
            self._base_url,
            self._api_version,
            self._info,
            self._version,
            self._version_int,
            self._revision,
        ) = (None,) * 6

        self.base_url = server
        self.api_version = api_version

        self.session = requests.Session()
        self.username = username
        self.session.auth = (self.username, password)
        if user_agent:
            self.session.headers["user-agent"] = user_agent

    def get_base_url(self) -> Optional[str]:
        return self._base_url

    def set_base_url(self, server: str) -> None:
        if "/api" in server:
            raise ClientException("Do not include /api/ in the DHIS2 `server` argument")

        server = server.strip()

        is_local = "localhost" in server or "127.0.0.1" in server
        has_scheme = "://" in server

        # add http / https schemes when missing
        if is_local and not has_scheme:
            url = "http://{}".format(server)
        elif not is_local and not has_scheme:
            url = "https://{}".format(server)
        else:
            url = server

        o = urlparse(url)
        self._base_url = "{}".format(
            urlunparse((o.scheme, o.netloc, o.path, "", "", ""))
        )

    def get_api_version(self) -> Optional[int]:
        return self._api_version

    def set_api_version(self, number: Union[str, int]) -> None:
        if number:
            try:
                i = int(number)
                if i < 25:
                    raise ValueError
            except ValueError:
                raise ClientException(
                    "`api_version` must be 25 or greater: {}".format(number)
                )
            else:
                self._api_version = i
        else:
            self._api_version = None

    def get_api_url(self) -> str:
        if self._api_version:
            return "{}/api/{}".format(self._base_url, self._api_version)
        else:
            return "{}/api".format(self._base_url)

    def get_info(self) -> dict:
        if not self._info:
            self._info = self.get("system/info").json()
        return self._info

    def get_version(self) -> str:
        return self._version if self._version else self.info["version"]

    def get_revision(self) -> str:
        return self._revision if self._revision else self.info["revision"]

    def get_version_int(self) -> Optional[int]:
        if not self._version_int:
            self._version_int = version_to_int(self.version)  # type: ignore
        return self._version_int

    # using property class to allow for type hinting of property (instead of @property)
    base_url = property(get_base_url, set_base_url)
    api_version = property(get_api_version, set_api_version)
    api_url = property(get_api_url)
    info = property(get_info)
    version = property(get_version)
    revision = property(get_revision)
    version_int = property(get_version_int)

    def __str__(self):
        s = (
            "DHIS2 Base URL: '{}'\n"
            "API URL: '{}'\n"
            "Username: '{}'".format(self.base_url, self.api_url, self.username)
        )
        return s

    @classmethod
    def from_auth_file(
        cls,
        location: str = None,
        api_version: Union[int, str] = None,
        user_agent: str = None,
    ) -> "Api":
        """
        Alternative constructor to load from JSON file.
        If auth_file_path is not specified, it tries to find `dish.json` in:
        - DHIS_HOME
        - Home folder
        :param location: authentication file path
        :param api_version: see Api
        :param user_agent: see Api
        :return: Api instance
        """
        location = search_auth_file() if not location else location

        a = load_json(location)
        try:
            section = a["dhis"]
            baseurl = section["baseurl"]
            username = section["username"]
            password = section["password"]
            assert all([baseurl, username, password])
        except (KeyError, AssertionError):
            raise ClientException("Auth file found but not valid: {}".format(location))
        else:
            return cls(
                baseurl,
                username,
                password,
                api_version=api_version,
                user_agent=user_agent,
            )

    @staticmethod
    def _validate_response(response: requests.Response) -> requests.Response:
        """
        Return response if ok, raise RequestException if not ok
        :param response: requests.response object
        :return: requests.response object
        """
        try:
            response.raise_for_status()
        except requests.RequestException:
            raise RequestException(
                code=response.status_code, url=response.url, description=response.text
            )
        else:
            return response

    @staticmethod
    def _validate_request(
        endpoint: str,
        file_type: str = "json",
        data: dict = None,
        params: Union[dict, List[tuple]] = None,
    ) -> None:
        """
        Validate request before calling API
        :param endpoint: API endpoint
        :param file_type: file type requested
        :param data: payload
        :param params: HTTP parameters
        """
        if not isinstance(endpoint, str) or endpoint.strip() == "":
            raise ClientException("Must submit `endpoint` for DHIS2 API")
        if not isinstance(file_type, str) or file_type.lower() not in (
            "json",
            "csv",
            "xml",
            "pdf",
            "xlsx",
        ):
            raise ClientException("Invalid file_type: {}".format(file_type))
        if params:
            if not isinstance(params, (dict, list)):
                raise ClientException(
                    "`params` must be a dict or list of tuples, not {}".format(
                        params.__class__.__name__  # type: ignore
                    )
                )
            if isinstance(params, list) and not all(
                [isinstance(elem, tuple) for elem in params]
            ):
                raise ClientException("`params` list must all be tuples")
        if data and not isinstance(data, dict):
            raise ClientException(
                "`data` must be a dict, not {}".format(data.__class__.__name__)  # type: ignore
            )

    def _make_request(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> requests.Response:
        """
        Do the actual request with supplied HTTP method
        :param method: HTTP method
        :param endpoint: DHIS2 API endpoint
        :param kwargs: keyword args
        :return: response if ok, RequestException if not
        """
        if isinstance(kwargs.get("file_type"), str):
            file_type = kwargs["file_type"].lower()
        else:
            file_type = "json"
        params = kwargs.get("params")

        data = kwargs.get("data", kwargs.get("json", None))
        timeout = kwargs.get("timeout")

        url = "{}/{}".format(self.api_url, endpoint)
        self._validate_request(endpoint, file_type, data, params)

        if method == "get":
            stream = kwargs.get("stream", False)
            url = "{}.{}".format(url, file_type)
            r = self.session.get(url, params=params, stream=stream, timeout=timeout)

        elif method == "post":
            r = self.session.post(url=url, json=data, params=params, timeout=timeout)

        elif method == "put":
            r = self.session.put(url=url, json=data, params=params, timeout=timeout)

        elif method == "patch":
            r = self.session.patch(url=url, json=data, params=params, timeout=timeout)

        elif method == "delete":
            r = self.session.delete(url=url, params=params, timeout=timeout)

        else:
            raise ClientException("Non-supported HTTP method: {}".format(method))

        return self._validate_response(r)

    def get(
        self,
        endpoint: str,
        file_type: str = "json",
        params: Union[dict, List[tuple]] = None,
        stream: bool = False,
        timeout: int = 5
    ) -> requests.Response:
        """
        GET from DHIS2
        :param endpoint: DHIS2 API endpoint
        :param file_type: DHIS2 API File Type (json, xml, csv), defaults to JSON
        :param params: HTTP parameters
        :param stream: use requests' stream parameter
        :param timeout: request timeout in seconds
        :return: requests.Response object
        """
        return self._make_request(
            "get", endpoint, params=params, file_type=file_type, stream=stream, timeout=timeout
        )

    def post(
        self,
        endpoint: str,
        json: dict = None,
        params: Union[dict, List[tuple]] = None,
        **kwargs: Any
    ) -> requests.Response:
        """POST to DHIS2
        :param endpoint: DHIS2 API endpoint
        :param json: HTTP payload
        :param params: HTTP parameters
        :return: requests.Response object
        """
        json = kwargs["data"] if "data" in kwargs else json
        return self._make_request("post", endpoint, data=json, params=params)

    def put(
        self,
        endpoint: str,
        json: dict = None,
        params: Union[dict, List[tuple]] = None,
        **kwargs: Any
    ) -> requests.Response:
        """
        PUT to DHIS2
        :param endpoint: DHIS2 API endpoint
        :param json: HTTP payload
        :param params: HTTP parameters
        :return: requests.Response object
        """
        json = kwargs["data"] if "data" in kwargs else json
        return self._make_request("put", endpoint, data=json, params=params)

    def patch(
        self,
        endpoint: str,
        json: dict = None,
        params: Union[dict, List[tuple]] = None,
        **kwargs: Any
    ) -> requests.Response:
        """
        PATCH to DHIS2
        :param endpoint: DHIS2 API endpoint
        :param json: HTTP payload
        :param params: HTTP parameters (dict)
        :return: requests.Response object
        """
        json = kwargs["data"] if "data" in kwargs else json
        return self._make_request("patch", endpoint, data=json, params=params)

    def delete(
        self,
        endpoint: str,
        json: dict = None,
        params: Union[dict, List[tuple]] = None,
        **kwargs: Any
    ) -> requests.Response:
        """
        DELETE from DHIS2
        :param endpoint: DHIS2 API endpoint
        :param json: HTTP payload
        :param params: HTTP parameters (dict)
        :return: requests.Response object
        """
        json = kwargs["data"] if "data" in kwargs else json
        return self._make_request("delete", endpoint, data=json, params=params)

    def get_paged(
        self,
        endpoint: str,
        params: Union[dict, List[tuple]] = None,
        page_size: Union[int, str] = 50,
        merge: bool = False,
    ) -> Union[Generator[dict, dict, None], dict]:
        """
        GET with paging (for large payloads).
        :param page_size: how many objects per page
        :param endpoint: DHIS2 API endpoint
        :param params: HTTP parameters (dict), defaults to None
        :param merge: If true, return a list containing all pages instead of one page. Defaults to False.
        :return: generator OR a normal DHIS2 response dict, e.g. {"organisationUnits": [...]}
        """
        try:
            if not isinstance(page_size, (str, int)) or int(page_size) < 1:
                raise ValueError
        except ValueError:
            raise ClientException("page_size must be > 1")

        params = {} if not params else params
        if "paging" in params:
            raise ClientException(
                "Can't set paging manually in `params` when using `get_paged`"
            )
        params["pageSize"] = page_size  # type: ignore
        params["page"] = 1  # type: ignore
        params["totalPages"] = True  # type: ignore

        collection = endpoint.split("/")[
            0
        ]  # only use e.g. events when submitting events/query as endpoint

        def page_generator() -> Generator[dict, dict, None]:
            """Yield pages"""
            page = self.get(endpoint=endpoint, file_type="json", params=params).json()
            page_count = page["pager"]["pageCount"]
            yield page

            while page["pager"]["page"] < page_count:
                params["page"] += 1  # type: ignore
                page = self.get(
                    endpoint=endpoint, file_type="json", params=params
                ).json()
                yield page

        if not merge:
            return page_generator()
        else:
            data = []
            for p in page_generator():
                data.append(p[collection])
            return {collection: list(chain.from_iterable(data))}

    def get_sqlview(
        self,
        uid: str,
        execute: bool = False,
        var: dict = None,
        criteria: dict = None,
        merge: bool = False,
    ) -> Union[Generator, List[dict]]:
        """
        GET SQL View data
        :param uid: sqlView UID
        :param execute: materialize sqlView before downloading its data
        :param var: for QUERY types, a dict of variables to query the sqlView
        :param criteria: for VIEW / MATERIALIZED_VIEW types, a dict of criteria to filter the sqlView
        :param merge: If true, return a list containing all pages instead of one page. Defaults to False.
        :return: a list OR generator where __next__ is a 'row' of the SQL View
        """
        params = {}
        sqlview_type = (
            self.get("sqlViews/{}".format(uid), params={"fields": "type"})
            .json()
            .get("type")
        )
        if sqlview_type == "QUERY":
            if not isinstance(var, dict):
                raise ClientException(
                    "Use a dict to submit variables: e.g. var={'key1': 'value1', 'key2': 'value2'}"
                )
            var = ["{}:{}".format(k, v) for k, v in var.items()]  # type: ignore
            params["var"] = var  # type: ignore
            if execute:
                raise ClientException(
                    "SQL view of type QUERY, no view to create (no execute=True)"
                )

        else:  # MATERIALIZED_VIEW / VIEW
            if criteria:
                if not isinstance(criteria, dict):
                    raise ClientException(
                        "Use a dict to submit criteria: { 'col1': 'value1', 'col2': 'value2' }"
                    )
                criteria = ["{}:{}".format(k, v) for k, v in criteria.items()]  # type: ignore
                params["criteria"] = criteria  # type: ignore

            if execute:  # materialize
                self.post("sqlViews/{}/execute".format(uid))

        def page_generator() -> Generator[dict, dict, None]:
            with closing(
                self.get(
                    "sqlViews/{}/data".format(uid),
                    file_type="csv",
                    params=params,
                    stream=True,
                )
            ) as r:
                # do not need to use unicodecsv.DictReader as data comes in bytes already
                reader = DictReader(
                    codecs.iterdecode(r.iter_lines(), "utf-8"),
                    delimiter=",",
                    quotechar='"',
                )
                for row in reader:
                    yield row

        if not merge:
            return page_generator()
        else:
            return list(page_generator())

    def post_partitioned(
        self,
        endpoint: str,
        json: dict,
        params: Union[dict, List[tuple]] = None,
        thresh: int = 1000,
    ) -> Iterator[requests.Response]:
        """
        Post a payload in chunks to prevent 'Request Entity Too Large' Timeout errors
        :param endpoint: the API endpoint to use
        :param json: payload dict
        :param params: request parameters
        :param thresh: the maximum amount to partition into
        :return: generator where __next__ is a requests.Response object
        """

        if not isinstance(json, dict):
            raise ClientException("Parameter `json` must be a dict")
        if not isinstance(thresh, int) or thresh < 2:
            raise ClientException("`thresh` must be integer of 2 or larger")

        try:
            key = next(iter(json))  # the (only) key in the payload
        except StopIteration:
            raise ClientException("`json` is empty")
        else:
            if len(json.keys()) != 1:
                raise ClientException(
                    'Must submit exactly one key in payload - e.g. json={"dataElements": [...]"}'
                )
            if not json.get(key):
                raise ClientException("payload for key '{}' is empty".format(key))
            else:
                for data in partition_payload(data=json, key=key, thresh=thresh):
                    yield self.post(endpoint, json=data, params=params)
