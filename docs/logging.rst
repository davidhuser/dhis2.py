Logging
========

Logging utilizes `logzero <https://github.com/metachris/logzero>`_.

- Color output depending on log level
- DHIS2 log format including the line of the caller
- optional ``logfile=`` specifies a rotating log file path (20 x 10MB files)


.. code:: python

    from dhis2 import setup_logger, logger

    setup_logger(logfile='/var/log/app.log')

    logger.info('my log message')
    logger.warn('missing something')
    logger.error('something went wrong')
    logger.exception('with stacktrace')

::

    * INFO  2018-06-01 18:19:40,001  my log message [script:86]
    * ERROR  2018-06-01 18:19:40,007  something went wrong [script:87]

Use ``setup_logger(include_caller=False)`` if you want to remove ``[script:86]`` from logs.