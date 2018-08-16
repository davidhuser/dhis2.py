import tempfile
import os


def test_setup_logger_default():
    from dhis2 import logger, setup_logger
    setup_logger()
    logger.info("info")
    logger.warn("warn")
    logger.debug("debug")
    logger.error("error")


def test_setup_logger_to_file():
    from dhis2 import logger, setup_logger

    filename = os.path.join(tempfile.gettempdir(), 'logfile.log')

    setup_logger(logfile=filename)
    logger.info("info")
    logger.warn("warn")
    logger.debug("debug")
    logger.error("error")

    assert os.path.isfile(filename)


def test_set_log_format():
    from dhis2 import logger, setup_logger
    from dhis2.logger import _set_log_format

    color_true_caller_true = '%(color)s* %(levelname)1s%(end_color)s  %(asctime)s,%(msecs)03d  %(message)s [%(module)s:%(lineno)d]'  # noqa
    color_true_caller_false = '%(color)s* %(levelname)1s%(end_color)s  %(asctime)s,%(msecs)03d  %(message)s'
    color_false_caller_true = '* %(levelname)1s  %(asctime)s,%(msecs)03d  %(message)s [%(module)s:%(lineno)d]'
    color_false_caller_false = '* %(levelname)1s  %(asctime)s,%(msecs)03d  %(message)s'

    assert _set_log_format(color=True, include_caller=True) == color_true_caller_true
    assert _set_log_format(color=True, include_caller=False) == color_true_caller_false
    assert _set_log_format(color=False, include_caller=True) == color_false_caller_true
    assert _set_log_format(color=False, include_caller=False) == color_false_caller_false



