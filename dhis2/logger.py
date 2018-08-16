import logging
import logzero


def _set_log_format(color, include_caller):
    """
    Set log format
    :param color: Log message is colored
    :param include_caller: At the end, put a [caller:line-of-code], e.g. [script:123]
    :return: string of log format
    """
    level_name = '* %(levelname)1s'
    time = '%(asctime)s,%(msecs)03d'
    message = '%(message)s'
    color_start = '%(color)s'
    color_end = '%(end_color)s'
    caller = '[%(module)s:%(lineno)d]'

    if color:
        if include_caller:
            return '{}{}{}  {}  {} {}'.format(color_start, level_name, color_end, time, message, caller)
        else:
            return '{}{}{}  {}  {}'.format(color_start, level_name, color_end, time, message)
    else:
        if include_caller:
            return '{}  {}  {} {}'.format(level_name, time, message, caller)
        else:
            return '{}  {}  {}'.format(level_name, time, message)


def setup_logger(logfile=None, backup_count=20, log_level=logging.INFO, include_caller=True):
    """
    Setup logzero logger. if logfile is specified, create additional file logger
    :param logfile: path to log file destination
    :param backup_count: number of rotating files
    :param log_level: min. log level FOR FILE LOGGING
    :param include_caller: whether to include the caller in the log output to STDOUT, e.g. [script:123]
    """
    formatter = logzero.LogFormatter(
        fmt=_set_log_format(color=True, include_caller=include_caller),
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logzero.setup_default_logger(formatter=formatter)

    if logfile:
        formatter = logzero.LogFormatter(
            fmt=_set_log_format(color=False, include_caller=True),
            datefmt='%Y-%m-%d %H:%M:%S')
        logzero.logfile(logfile, formatter=formatter, loglevel=log_level, maxBytes=int(1e7), backupCount=backup_count)
