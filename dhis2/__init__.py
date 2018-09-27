# -*- coding: utf-8 -*-

from .__version__ import __title__, __description__, __url__, __version__
from .__version__ import __author__, __author_email__, __license__

from .api import Dhis
from .exceptions import Dhis2PyException, APIException, ClientException
from .utils import load_json, load_csv, pretty_json
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
    'pretty_json'
)


# Set default logging handler to avoid "No handler found" warnings.
import logging
from logging import NullHandler  # py 2.7+

logging.getLogger(__name__).addHandler(NullHandler())
