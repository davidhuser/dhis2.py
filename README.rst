dhis2.py
########

|Latest version| |Downloads| |Build| |BuildWin| |Coverage| |LGTM| |CodeClimate|

A Python library for `DHIS2 <https://dhis2.org>`_ wrapping `requests <http://docs.python-requests.org/en/master/user/quickstart/>`_
for **general-purpose API interaction** with DHIS2. It attempts to be **useful for any data/metadata import and export tasks**
including various utilities like file loading, UID generation and logging. A strong focus is on JSON.

Supported and tested on Linux/macOS, Windows and DHIS2 versions >= 2.25. Python 3.6+ is required.

.. contents::
.. section-numbering::


Installation
=============

Python 3.6+ is required.

.. code:: bash

    pip install dhis2.py

For instructions on installing Python / pip for your operating system see `realpython.com/installing-python <https://realpython.com/installing-python>`_.


Quickstart
==========

Create an ``Api`` object:

.. code:: python

    from dhis2 import Api

    api = Api('play.dhis2.org/demo', 'admin', 'district')

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

see below for more methods.

They all return a *Response* object from `requests <http://docs.python-requests.org/en/master/user/quickstart/>`_
except noted otherwise. This means methods and attributes are equally available
(e.g. ``Response.url``, ``Response.text``, ``Response.status_code`` etc.).

Usage
=====

Api instance creation
-----------------------

Authentication in code
^^^^^^^^^^^^^^^^^^^^^^

Create an API object

.. code:: python

    from dhis2 import Api

    api = Api('play.dhis2.org/demo', 'admin', 'district')

optional arguments:

- ``api_version``: DHIS2 API version
- ``user_agent``: submit your own User-Agent header. This is useful if you need to parse e.g. Nginx logs later.


Authentication from file
^^^^^^^^^^^^^^^^^^^^^^^^^

Load from a auth JSON file in order to not store credentials in scripts.
Must have the following structure:

.. code:: json

    {
      "dhis": {
        "baseurl": "http://localhost:8080",
        "username": "admin",
        "password": "district"
      }
    }

.. code:: python

    from dhis2 import Api

    api = Api.from_auth_file('path/to/auth.json', api_version=29, user_agent='myApp/1.0')


If no file path is specified, it tries to find a file called ``dish.json`` in:

1. the ``DHIS_HOME`` environment variable
2. your Home folder


Get info about the DHIS2 instance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

API version as a string:

.. code:: python

    print(api.version)
    # '2.30'

API version as an integer:

.. code:: python

    print(api.version_int)
    # 30

API revision / build:

.. code:: python

    print(api.revision)
    # '17f7f0b'

API URL:

.. code:: python

    print(api.api_url)
    # 'https://play.dhis2.org/demo/api/30'

Base URL:

.. code:: python

    print(api.base_url)
    # 'https://play.dhis2.org/demo'

system info (this is persisted across the session):

.. code:: python

    print(api.info)
    # {
    #   "lastAnalyticsTableRuntime": "11 m, 51 s",
    #   "systemId": "eed3d451-4ff5-4193-b951-ffcc68954299",
    #   "contextPath": "https://play.dhis2.org/2.30",
    #   ...


Getting things
--------------

Normal method: ``api.get()``, e.g.

.. code:: python

    r = api.get('organisationUnits/Rp268JB6Ne4', params={'fields': 'id,name'})
    data = r.json()

Parameters:

- `timeout`: to override the timeout value (default: 5 seconds) in order to prevent the client to wait indefinitely on a server response.


Paging
^^^^^^

Paging for larger GET requests via ``api.get_paged()``

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

*Note:* Returns directly a JSON object, not a requests.Response object unlike normal GETs.


SQL Views
^^^^^^^^^^

Get SQL View data as if you'd open a CSV file, optimized for larger payloads, via ``api.get_sqlview()``

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



GET other content types
^^^^^^^^^^^^^^^^^^^^^^^

Usually defaults to JSON but you can get other file types:

.. code:: python

    r = api.get('organisationUnits/Rp268JB6Ne4', file_type='xml')
    print(r.text)
    # <?xml version='1.0' encoding='UTF-8'?><organisationUnit ...

    r = api.get('organisationUnits/Rp268JB6Ne4', file_type='pdf')
    with open('/path/to/file.pdf', 'wb') as f:
        f.write(r.content)



Updating / deleting things
--------------------------

Normal methods:

* ``api.post()``
* ``api.put()``
* ``api.patch()``
* ``api.delete()``


Post partitioned payloads
^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have such a large payload (e.g. metadata imports) that you frequently get a HTTP Error:
``413 Request Entity Too Large`` response e.g. from Nginx you might benefit from using
the following method that splits your payload in partitions / chunks and posts them one-by-one.
You define the amount of elements in each POST by specifying a number in ``thresh`` (default: ``1000``).

Note that it is only possible to submit one key per payload (e.g. ``dataElements`` only, not additionally ``organisationUnits`` in the same payload).

``api.post_partitioned()``

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


Multiple params with same key
-----------------------------

If you need to pass multiple parameters to your request with the same key, you may submit as a list of tuples instead when e.g.:

.. code:: python

    r = api.get('dataValueSets', params=[
            ('dataSet', 'pBOMPrpg1QX'), ('dataSet', 'BfMAe6Itzgt'),
            ('orgUnit', 'YuQRtpLP10I'), ('orgUnit', 'vWbkYPRmKyS'),
            ('startDate', '2013-01-01'), ('endDate', '2013-01-31')
        ]
    )

alternatively:

.. code:: python

    r = api.get('dataValueSets', params={
        'dataSet': ['pBOMPrpg1QX', 'BfMAe6Itzgt'],
        'orgUnit': ['YuQRtpLP10I', 'vWbkYPRmKyS'],
        'startDate': '2013-01-01',
        'endDate': '2013-01-31'
    })


Utilities
---------

Load JSON file
^^^^^^^^^^^^^^^^^

.. code:: python

    from dhis2 import load_json

    json_data = load_json('/path/to/file.json')
    print(json_data)
    # { "id": ... }


Load CSV file
^^^^^^^^^^^^^^^^

Via a Python generator:

.. code:: python

    from dhis2 import load_csv

    for row in load_csv('/path/to/file.csv'):
        print(row)
        # { "id": ... }

Via a normal list, loaded fully into memory:

.. code:: python

    data = list(load_csv('/path/to/file.csv'))

Generate UID
^^^^^^^^^^^^

Create a DHIS2 UID:

.. code:: python

    uid = generate_uid()
    print(uid)
    # 'Rp268JB6Ne4'

To create a list of 1000 UIDs:

.. code:: python

    uids = [generate_uid() for _ in range(1000)]


Validate UID
^^^^^^^^^^^^

Check if something is a valid DHIS2 UID:

.. code:: python

    uid = 'MmwcGkxy876'
    print(is_valid_uid(uid))
    # True

    uid = 25329
    print(is_valid_uid(uid))
    # False

    uid = 'MmwcGkxy876 '
    print(is_valid_uid(uid))
    # False


Clean an object
^^^^^^^^^^^^^^^^

Useful for deep-removing certain keys in an object,
e.g. remove all sharing by recursively removing all ``user`` and ``userGroupAccesses`` fields.

.. code:: python

    from dhis2 import clean_obj

    metadata = {
        "dataElements": [
            {
                "name": "ANC 1st visit",
                "id": "fbfJHSPpUQD",
                "publicAccess": "rw------",
                "userGroupAccesses": [
                    {
                        "access": "r-r-----",
                        "userGroupUid": "Rg8wusV7QYi",
                        "displayName": "HIV Program Coordinators",
                        "id": "Rg8wusV7QYi"
                    },
                    {
                        "access": "rwr-----",
                        "userGroupUid": "qMjBflJMOfB",
                        "displayName": "Family Planning Program",
                        "id": "qMjBflJMOfB"
                    }
                ]
            }
        ],
        "dataSets": [
            {
                "name": "ART monthly summary",
                "id": "lyLU2wR22tC",
                "publicAccess": "rwr-----",
                "userGroupAccesses": [
                    {
                        "access": "r-rw----",
                        "userGroupUid": "GogLpGmkL0g",
                        "displayName": "_DATASET_Child Health Program Manager",
                        "id": "GogLpGmkL0g"
                    }
                ]
            }
        ]
    }


    cleaned = clean_obj(metadata, ['userGroupAccesses', 'publicAccess'])
    pretty_json(cleaned)

Which would eventually recursively remove all keys matching to ``userGroupAccesses`` or ``publicAccess``:

.. code:: json

    {
      "dataElements": [
        {
          "name": "ANC 1st visit",
          "id": "fbfJHSPpUQD"
        }
      ],
      "dataSets": [
        {
          "name": "ART monthly summary",
          "id": "lyLU2wR22tC"
        }
      ]
    }


Print pretty JSON
^^^^^^^^^^^^^^^^^

Print easy-readable JSON objects with colors, utilizes `Pygments <http://pygments.org/>`_.

.. code:: python

    from dhis2 import pretty_json

    obj = {"dataElements": [{"name": "Accute Flaccid Paralysis (Deaths < 5 yrs)", "id": "FTRrcoaog83", "aggregationType": "SUM"}]}
    pretty_json(obj)

... prints (in a terminal it will have colors):

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


Logging
-------

Logging utilizes `logzero <https://github.com/metachris/logzero>`_.

- Color output depending on log level
- DHIS2 log format including the line of the caller
- optional ``logfile=`` specifies a rotating log file path (20 x 10MB files)


.. code:: python

    from dhis2 import setup_logger, logger

    setup_logger(logfile='/var/log/app.log')

    logger.info('my log message')
    logger.warning('missing something')
    logger.error('something went wrong')
    logger.exception('with stacktrace')

::

    * INFO  2018-06-01 18:19:40,001  my log message [script:86]
    * ERROR  2018-06-01 18:19:40,007  something went wrong [script:87]

Use ``setup_logger(include_caller=False)`` if you want to remove ``[script:86]`` from logs.

Exceptions
----------

There are two exceptions:

- ``RequestException``: DHIS2 didn't like what you requested. See the exception's ``code``, ``url`` and ``description``.
- ``ClientException``: Something didn't work with the client not involving DHIS2.

They both inherit from ``Dhis2PyException``.


Examples
========

* Real-world script examples can be found in the ``examples`` folder.
* dhis2.py is used in `dhis2-pk <https://github.com/davidhuser/dhis2-pk>`_ (dhis2-pocket-knife)

Changelog
==========

Versions `changelog <https://github.com/davidhuser/dhis2.py/blob/master/CHANGELOG.rst>`_

Contribute
==========

Feedback welcome!

- Add `issue <https://github.com/davidhuser/dhis2.py/issues/new>`_
- Install the dev environment (see below)
- Fork, add changes to *master* branch, ensure tests pass with full coverage and add a Pull Request

.. code:: bash

    pip install pipenv
    git clone https://github.com/davidhuser/dhis2.py
    cd dhis2.py
    pipenv install --dev
    pipenv run tests

    # install pre-commit hooks
    pipenv run pre-commit install

    # run type annotation check
    pipenv run mypy dhis2

    # run flake8 style guide enforcement
    pipenv run flake8

License
=======

dhis2.py's source is provided under MIT license.
See LICENCE for details.

* Copyright (c), 2020, David Huser


.. |Latest version| image:: https://img.shields.io/pypi/v/dhis2.py.svg?label=PyPi
   :target: https://pypi.org/project/dhis2.py
   :alt: PyPi version
   
.. |Downloads| image:: https://static.pepy.tech/badge/dhis2-py/month
   :target: https://pepy.tech/project/dhis2.py
   :alt: Downloads

.. |Build| image:: https://img.shields.io/circleci/project/github/davidhuser/dhis2.py/master.svg?label=Linux%20build
   :target: https://circleci.com/gh/davidhuser/dhis2.py
   :alt: CircleCI build

.. |BuildWin| image:: https://img.shields.io/appveyor/ci/davidhuser/dhis2-py.svg?label=Windows%20build
   :target: https://ci.appveyor.com/project/davidhuser/dhis2-py
   :alt: Appveyor build

.. |Coverage| image:: https://img.shields.io/codecov/c/github/davidhuser/dhis2.py.svg?label=Coverage
   :target: https://codecov.io/gh/davidhuser/dhis2.py
   :alt: Test coverage

.. |LGTM| image:: https://img.shields.io/lgtm/grade/python/g/davidhuser/dhis2.py.svg?label=Code%20quality
   :target: https://lgtm.com/projects/g/davidhuser/dhis2.py
   :alt: Code quality

.. |CodeClimate| image:: https://img.shields.io/codeclimate/maintainability/davidhuser/dhis2.py.svg?label=Maintainability
   :target: https://codeclimate.com/github/davidhuser/dhis2.py/maintainability
   :alt: Code maintainability
