import logging
import logzero

# DHIS2 logging format incl. [file:codeline]
log_format = '* %(levelname)1s  %(asctime)s,%(msecs)03d  %(message)s [%(module)s:%(lineno)d]'

# Including color depending on log level
log_format_color = '%(color)s* %(levelname)1s%(end_color)s  %(asctime)s,%(msecs)03d  %(message)s [%(module)s:%(lineno)d]'  # noqa


def setup_logger(logfile=None, backup_count=20, log_level=logging.INFO):
    """
    Setup logzero logger. if logfile is specified, create additional file logger
    :param logfile: path to log file destination
    :param backup_count: number of rotating files
    :param log_level: min. log level FOR FILE LOGGING
    """
    formatter = logzero.LogFormatter(fmt=log_format_color, datefmt='%Y-%m-%d %H:%M:%S')
    logzero.setup_default_logger(formatter=formatter)

    if logfile:
        formatter = logzero.LogFormatter(fmt=log_format)
        logzero.logfile(logfile, formatter=formatter, loglevel=log_level, maxBytes=int(1e7), backupCount=backup_count)
