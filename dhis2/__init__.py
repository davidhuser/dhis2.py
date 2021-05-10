# -*- coding: utf-8 -*-

"""
dhis2.py - Python wrapper for DHIS2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A Python library for DHIS2 wrapping requests (github.com/requests/requests)

:copyright: (c) 2018 by David Huser
:license: MIT, see LICENSE for more details.
"""

from .exceptions import Dhis2PyException, RequestException, ClientException
from .api import Api
from .utils import (
    load_json,
    load_csv,
    pretty_json,
    clean_obj,
    generate_uid,
    is_valid_uid,
)
from .logger import setup_logger
from logzero import logger as logger


__all__ = (
    "Api",
    "Dhis2PyException",
    "RequestException",
    "ClientException",
    "setup_logger",
    "logger",
    "load_json",
    "load_csv",
    "pretty_json",
    "clean_obj",
    "generate_uid",
    "is_valid_uid",
)


# Set default logging handler to avoid "No handler found" warnings.
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
