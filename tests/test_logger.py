import tempfile
import os

import pytest


def test_setup_logger_default():
    from dhis2.logger import setup_logger
    from dhis2 import logger
    setup_logger()
    logger.info("info")
    logger.warn("warn")
    logger.debug("debug")
    logger.error("error")


def test_setup_logger_to_file():

    from dhis2.logger import setup_logger
    from dhis2 import logger

    filename = os.path.join(tempfile.gettempdir(), 'logfile.log')

    setup_logger(logfile=filename)
    logger.info("info")
    logger.warn("warn")
    logger.debug("debug")
    logger.error("error")

    assert os.path.isfile(filename)



