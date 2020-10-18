# -*- coding: utf-8 -*-

"""
dhis2.exceptions
~~~~~~~~~~~~~~~~~

This module contains dhis2.py exceptions.
"""

from typing import Any

import requests


class Dhis2PyException(Exception):
    """ Base exception for all custom exceptions"""


class RequestException(Dhis2PyException, requests.RequestException):
    """DHIS2 API call error"""

    def __init__(
        self, code: int, url: str, description: str, *args: Any, **kwargs: Any
    ) -> None:
        super(RequestException, self).__init__(*args, **kwargs)
        self.code = code
        self.url = url
        self.description = description

    def __repr__(self) -> str:
        return "Dhis2ApiException({}, '{}', '{}')".format(
            self.code, self.url, self.description
        )

    def __str__(self) -> str:
        return "code: {}, url: {}, description: {}".format(
            self.code, self.url, self.description
        )


class ClientException(Dhis2PyException):
    """Exceptions not involving DHIS2's API."""
