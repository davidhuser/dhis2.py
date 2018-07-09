dhis2.py - Python wrapper for DHIS2
====================================

|Build| |BuildWin| |Coverage| |PyPi|

Python wrapper for `DHIS2 <https://dhis2.org>`_.

- Common HTTP operations (GET, POST, PUT, PATCH, DELETE)
- CSV/JSON file loading
- Server-side UID generation
- SQLViews
- `requests <https://github.com/requests/requests>`_ as HTTP library
- `logzero <https://github.com/metachris/logzero>`_ as drop-in logging library
- Defaults to JSON, supported GETs: XML, CSV, PDF, XLS
- Supported and tested on Python 2.7, 3.4-3.6 and DHIS2 versions >= 2.25

Install
--------

Simply use `pipenv <https://docs.pipenv.org>`_ (or ``pip``):

.. code:: bash

    pipenv install dhis2.py --user --upgrade


Basics
-------

Create an API object:

.. code:: python

    from dhis2 import Dhis

    api = Dhis('play.dhis2.org/demo', 'admin', 'district', api_version=29)

optional arguments:

- ``api_version``: DHIS2 API version
- ``user_agent``: submit your own User-Agent header

Then run requests on it:

.. code:: python

    print(api.dhis_version())
    # (29, '80d2c77')

    print(api.info())
    # { "systemName": "DHIS 2 Demo - Sierra Leone", "version": "2.29", ... }

    r = api.get('organisationUnits/Rp268JB6Ne4', params={'fields': 'id,name'})

    print(r.json())
    # { "name": "Adonkia CHP", "id": "Rp268JB6Ne4" }

    print(r.status_code)
    # 200



Load authentication from file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Load from a auth JSON file in order to not store credentials in scripts.
Must have the following structure:

.. code:: json

    {
      "dhis": {
        "baseurl": "https://play.dhis2.org/demo",
        "username": "admin",
        "password": "district"
      }
    }

.. code:: python

    from dhis2 import Dhis

    api = Dhis.from_auth_file('path/to/auth.json', api_version=29, user_agent='myApp/1.0')


If no argument is specified, it tries to find a file called ``dish.json`` in:

1. the ``DHIS_HOME`` environment variable
2. your Home folder



Load a JSON file
^^^^^^^^^^^^^^^^^

.. code:: python

    from dhis2 import load_json

    json_data = load_json('/path/to/file.json')
    print(json_data)
    # { "id": ... }


Load a CSV file
^^^^^^^^^^^^^^^^

.. code:: python

    from dhis2 import load_csv

    for row in load_csv('/path/to/file.csv'):
        print(row)
        # { "id": ... }

    # or for a normal list
    data = list(load_csv('/path/to/file.csv'))


API paging
^^^^^^^^^^^

Paging for large GET requests (JSON only)

.. code:: python

    for page in api.get_paged('organisationUnits', page_size=100):
        print(page)
        # { "organisationUnits": [ {...}, {...} ] } (100 elements each)


SQL Views
^^^^^^^^^^

Get SQL View data as if you'd open a CSV file, optimized for larger payloads:

.. code:: python

    # poll a sqlView of type VIEW or MATERIALIZED_VIEW:
    for row in api.get_sqlview('YOaOY605rzh', execute=True, criteria={'name': '0-11m'}):
        print(row)
        # {'code': 'COC_358963', 'name': '0-11m'}

    # similarly, poll a sqlView of type QUERY:
    for row in api.get_sqlview('qMYMT0iUGkG', var={'valueType': 'INTEGER'}):
        print(row)

    # again, if you want a list directly:
    data = list(api.get_sqlview('qMYMT0iUGkG', var={'valueType': 'INTEGER'}))

Beginning of 2.26 you can also use normal filtering on sqlViews. In that case, it's recommended
to use the ``stream`` parameter of the ``Dhis.get()`` method.


Generate UIDs
^^^^^^^^^^^^^

Get server-generated UIDs (not limited to 10000)

.. code:: python

    from dhis2 import generate_uids

    uids = generate_uids(20000)
    print(uids)
    # ['Rp268JB6Ne4', 'fa7uwpCKIwa', ... ]


GET other content types
^^^^^^^^^^^^^^^^^^^^^^^^

Usually defaults to JSON but you can get other file types:

.. code:: python

    r = api.get('organisationUnits/Rp268JB6Ne4', file_type='xml')
    print(r.text)
    # <?xml version='1.0' encoding='UTF-8'?><organisationUnit ...

    r = api.get('organisationUnits/Rp268JB6Ne4', file_type='pdf')
    with open('/path/to/file.pdf', 'wb') as f:
        f.write(r.content)

Logging
^^^^^^^^

- optional ``logfile=`` specifies log file destination
- Color output depending on log level
- DHIS2 log format

.. code:: python

    from dhis2 import setup_logger, logger

    setup_logger(logfile='/var/log/app.log')

    logger.warn(data)
    logger.error('hello')
    logger.warn('blup')

Exceptions
^^^^^^^^^^^

There should be only two exceptions:

- ``APIException``: DHIS2 didn't like what you requested. See the exception's ``code``, ``url`` and ``description``.
- ``ClientException``: Something didn't work with the client not involving DHIS2.

They both inherit from ``Dhis2PyException``.


Contribute
-----------

Feedback welcome!

Add `issue <https://github.com/davidhuser/dhis2.py/issues/new>`_

and/or install the dev environment:

.. code:: bash

    pip install pipenv
    git clone https://github.com/davidhuser/dhis2.py && cd dhis2.py
    pipenv install --dev
    pipenv run tests



.. |Build| image:: https://travis-ci.org/davidhuser/dhis2.py.svg?branch=master
   :target: https://travis-ci.org/davidhuser/dhis2.py

.. |BuildWin| image:: https://ci.appveyor.com/api/projects/status/9lkxdi8o8r8o5jy7?svg=true
   :target: https://ci.appveyor.com/project/davidhuser/dhis2-py

.. |Coverage| image:: https://coveralls.io/repos/github/davidhuser/dhis2.py/badge.svg?branch=master
   :target: https://coveralls.io/github/davidhuser/dhis2.py?branch=master

.. |PyPi| image:: https://img.shields.io/pypi/v/dhis2.py.svg
   :target: https://pypi.org/project/dhis2.py

