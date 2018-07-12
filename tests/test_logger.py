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


@pytest.fixture
def log_file():
    tmp = tempfile.gettempdir()
    filename = os.path.join(tmp, 'logfile.log')
    yield filename
    os.remove(filename)


def test_setup_logger_to_file(log_file):

    from dhis2.logger import setup_logger
    from dhis2 import logger
    setup_logger(logfile=log_file)
    logger.info("info")
    logger.warn("warn")
    logger.debug("debug")
    logger.error("error")

    assert os.path.isfile(log_file)


