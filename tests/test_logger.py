""" TODO

import os
import tempfile
import logzero


def test_setup_logger_default(capsys):
    from dhis2.logger import setup_logger
    from dhis2 import logger
    setup_logger()
    logger.info("hello1")

    captured = capsys.readouterr()
    assert "hello1" in captured.out
    assert "hello1" in captured.err
"""
