def test_setup_logger_default():
    from dhis2.logger import setup_logger
    from dhis2 import logger
    setup_logger()
    logger.info("info")
    logger.warn("warn")
    logger.debug("debug")
    logger.error("error")

