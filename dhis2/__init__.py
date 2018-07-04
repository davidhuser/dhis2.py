# -*- coding: utf-8 -*-
import sys

from .__version__ import __title__, __description__, __url__, __version__
from .__version__ import __author__, __author_email__, __license__

from .api import Dhis
from .exceptions import Dhis2PyException, APIException, ClientException
from .utils import load_json, load_csv
from .logger import setup_logger
from logzero import logger as logger


__all__ = (
    'Dhis',
    'Dhis2PyException',
    'APIException',
    'ClientException',
    'setup_logger',
    'logger',
    'load_json',
    'load_csv',
)


# Set default logging handler to avoid "No handler found" warnings.
# https://docs.python.org/2/howto/logging.html#configuring-logging-for-a-library
import logging
try:
    from logging import NullHandler  # py3
except ImportError:
    # py2
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
