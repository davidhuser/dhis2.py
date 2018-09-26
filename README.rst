dhis2.py
=========

|Latest version| |Build| |BuildWin| |Coverage| |PyUp|

A Python library for `DHIS2 <https://dhis2.org>`_ wrapping `requests <https://github.com/requests/requests>`_.

- Common **HTTP operations** (GET, POST, PUT, PATCH, DELETE)
- Additional utilities like **paging** with GET or **partitioned** POSTs
- **SQL Views**
- Server-side UID generation
- CSV/JSON file loading
- Defaults to ``json``, supported GETs: ``xml``, ``csv``, ``pdf``, ``xls``
- `logzero <https://github.com/metachris/logzero>`_ for logging
- **Supported and tested** on Python 2.7, 3.4-3.7 and DHIS2 versions >= 2.25

Installation
-------------

Simply use `pipenv <https://docs.pipenv.org>`_ (or ``pip``):

.. code:: bash

    pipenv install dhis2.py --upgrade

For instructions on installing Python / pip see `The Hitchhiker's Guide to
Python <http://docs.python-guide.org/en/latest/starting/installation/>`_.


Quickstart
-----------

Create an API object:

.. code:: python

    from dhis2 import Dhis

    api = Dhis('play.dhis2.org/demo', 'admin', 'district', api_version=29, user_agent='myApp/0.1')

optional arguments:

- ``api_version``: DHIS2 API version
- ``user_agent``: submit your own User-Agent header

Then run requests on it:

.. code:: python

    r = api.get('organisationUnits/Rp268JB6Ne4', params={'fields': 'id,name'})

    print(r.json())
    # { "name": "Adonkia CHP", "id": "Rp268JB6Ne4" }

    r = api.post('metadata', json={'dataElements': [ ... ] })
    print(r.status_code) # 200


- ``api.get()``
- ``api.post()``
- ``api.put()``
- ``api.patch()``
- ``api.delete()``


Examples
^^^^^^^^

Real-world script examples can be found in the ``examples`` folder.


Get info about the DHIS2 instance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    print(api.version)
    # '2.29'

    print(api.version_int)
    # 29

    print(api.revision)
    # '17f7f0b'

    print(api.api_url)
    # 'https://play.dhis2.org/2.29/api/29'

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


If no file path is specified, it tries to find a file called ``dish.json`` in:

1. the ``DHIS_HOME`` environment variable
2. your Home folder


API paging
^^^^^^^^^^^

Paging for larger GET requests.

Two possible ways:

a) Process every page as they come in:

.. code:: python

    for page in api.get_paged('organisationUnits', page_size=100):
        print(page)
        # { "organisationUnits": [ {...}, {...} ] } (100 organisationUnits)

b) Load all pages before proceeding (this may take a long time) - to do this, do not use ``for`` and add ``merge=True``:

.. code:: python

    all_pages = api.get_paged('organisationUnits', page_size=100, merge=True):
    print(all_pages)
    # { "organisationUnits": [ {...}, {...} ] } (all organisationUnits)

*Note:* Returns directly a JSON object, not a requests.response object unlike normal GETs.

Multiple params
^^^^^^^^^^^^^^^

You may submit params as a list of tuples instead when you need to pass multiple parameters with the same key, e.g.:

.. code:: python

    r = api.get('dataValueSets', params=[
            ('dataSet', 'pBOMPrpg1QX'), ('dataSet', 'BfMAe6Itzgt'),
            ('orgUnit', 'YuQRtpLP10I'), ('orgUnit', 'vWbkYPRmKyS'),
            ('startDate', '2013-01-01'), ('endDate', '2013-01-31')
        ]
    )

or

.. code:: python

    r = api.get('dataValueSets', params={
        'dataSet': ['pBOMPrpg1QX', 'BfMAe6Itzgt'],
        'orgUnit': ['YuQRtpLP10I', 'vWbkYPRmKyS'],
        'startDate': '2013-01-01',
        'endDate': '2013-01-31'
    })

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

    # if you want a list directly, cast it to a ``list`` or add ``merge=True``:
    data = list(api.get_sqlview('qMYMT0iUGkG', var={'valueType': 'INTEGER'}))
    # OR
    # data = api.get_sqlview('qMYMT0iUGkG', var={'valueType': 'INTEGER'}, merge=True)

*Note:* Returns directly a JSON object, not a requests.response object unlike normal GETs.

Beginning of 2.26 you can also use normal filtering on sqlViews. In that case, it's recommended
to use the ``stream=True`` parameter of the ``Dhis.get()`` method.


Post partitioned payloads
^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have such a large payload (e.g. metadata imports) that you frequently get a HTTP Error:``413 Request Entity Too Large`` response e.g. from Nginx you might benefit from using the following method that splits your payload in partitions / chunks and posts them one-by-one. You define the amount of elements in each POST by specifying a number in ``thresh`` (default: ``1000``). Note that it is only possible to submit one key per payload (e.g. ``dataElements`` only, not additionally ``organisationUnits`` in the same payload).

.. code:: python
    
    import json
    
    data = {
        "organisationUnits": [
            {...},
            {...} # very large number of org units
        ]
    {
    for response in api.post_partitioned('metadata', json=data, thresh=5000):
        text = json.loads(response.text)
        print('[{}] - {}'.format(text['status'], json.dumps(text['stats'])))


Generate UIDs
^^^^^^^^^^^^^

Create UIDs on the server (not limited to 10000):

.. code:: python

    uids = api.generate_uids(20000)
    print(uids)
    # ['Rp268JB6Ne4', 'fa7uwpCKIwa', ... ]

If you want UIDs generated locally (no server calls), add ``local=True``.


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

Logging
^^^^^^^^

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


Pretty JSON
^^^^^^^^^^^^

Print easy-readable JSON objects.

.. code:: python

    obj = {"dataElements": [{"name": "Accute Flaccid Paralysis (Deaths < 5 yrs)", "id": "FTRrcoaog83", "aggregationType": "SUM"}]}
    pretty_json(obj)

.. code:: json

    {
      "dataElements": [
        {
          "aggregationType": "SUM",
          "id": "FTRrcoaog83",
          "name": "Accute Flaccid Paralysis (Deaths < 5 yrs)"
        }
      ]
    }


Exceptions
^^^^^^^^^^^

There are two exceptions:

- ``APIException``: DHIS2 didn't like what you requested. See the exception's ``code``, ``url`` and ``description``.
- ``ClientException``: Something didn't work with the client not involving DHIS2.

They both inherit from ``Dhis2PyException``.


Contribute
-----------

Feedback welcome!

- Check the `changelog <https://github.com/davidhuser/dhis2.py/blob/master/CHANGELOG.rst>`_
- Add `issue <https://github.com/davidhuser/dhis2.py/issues/new>`_
- Install the dev environment (see below)
- Fork, add changes to *master* branch, ensure tests pass with full coverage and add a Pull Request

.. code:: bash

    pip install pipenv
    git clone https://github.com/davidhuser/dhis2.py && cd dhis2.py
    pipenv install --dev
    pipenv run tests


.. |Latest version| image:: https://img.shields.io/pypi/v/dhis2.py.svg?label=pip
   :target: https://pypi.org/project/dhis2.py

.. |Build| image:: https://img.shields.io/travis/davidhuser/dhis2.py/master.svg?label=travis-ci
   :target: https://travis-ci.org/davidhuser/dhis2.py

.. |BuildWin| image:: https://img.shields.io/appveyor/ci/davidhuser/dhis2-py.svg?label=appveyor-ci
   :target: https://ci.appveyor.com/project/davidhuser/dhis2-py

.. |Coverage| image:: https://img.shields.io/coveralls/davidhuser/dhis2.py/master.svg
   :target: https://coveralls.io/github/davidhuser/dhis2.py?branch=master

.. |PyUp| image:: https://pyup.io/repos/github/davidhuser/dhis2.py/shield.svg
   :target: https://pyup.io/repos/github/davidhuser/dhis2.py
