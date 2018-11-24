dhis2.py
########

|Latest version| |Build| |BuildWin| |Coverage| |LGTM| |CodeClimate|

A Python library for `DHIS2 <https://dhis2.org>`_ wrapping `requests <https://github.com/requests/requests>`_
for **general-purpose API interaction** with DHIS2. It attempts to be **useful for any data/metadata import tasks**
including various utilities like file loading, UID generation and logging. A strong focus is on JSON.

Supported and tested on Python 2 and 3 on Linux/macOS, Windows and DHIS2 versions >= 2.25.

.. contents::
.. section-numbering::


Installation
=============

with ``pipenv``
----------------

Simply use `pipenv <https://docs.pipenv.org>`_:

.. code:: bash

    pipenv install dhis2.py --upgrade


with ``pip``
------------

.. code:: bash

    pip install dhis2.py --upgrade

For instructions on installing Python / pip for your operating system see `The Hitchhiker's Guide to
Python <http://docs.python-guide.org/en/latest/starting/installation/>`_.


Quickstart
==========

Create an API object:

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

Normal method: ``api.get()``

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

*Note:* Returns directly a JSON object, not a requests.response object unlike normal GETs.

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
to use the ``stream=True`` parameter of the ``Api.get()`` method.


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

Generate UIDs
^^^^^^^^^^^^^

Create UIDs on the server (not limited to 10000):

.. code:: python

    uids = api.generate_uids(20000)
    print(uids)
    # ['Rp268JB6Ne4', 'fa7uwpCKIwa', ... ]

If you want UIDs generated locally (no server calls), add ``local=True``.


Clean an object
^^^^^^^^^^^^^^^^

Useful for removing e.g. all ``user`` or ``userGroupAccesses`` from an object.

.. code:: python

    from dhis2 import clean_obj

    # obj = {
    #   "dataElements": [
    #       {
    #           "name": "GL- DE001",
    #           "user": {
    #               "id": "gONaRemoveThis"
    #           }
    #       }
    #   ]
    # }

    cleaned = clean_obj(obj, 'user')
    print(cleaned)

    # obj = {
    #     "dataElements": [
    #         {
    #             "name": "GL- DE001",
    #         }
    #     ]
    # }

Submit more keys to remove by wrapping them into a list or set. This works recursively.

Print pretty JSON
^^^^^^^^^^^^^^^^^

Print easy-readable JSON objects with colors, utilizes `pygments <http://pygments.org/>`_.

.. code:: python

    from dhis2 import pretty_json

    obj = {"dataElements": [{"name": "Accute Flaccid Paralysis (Deaths < 5 yrs)", "id": "FTRrcoaog83", "aggregationType": "SUM"}]}
    pretty_json(obj)

... prints:

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
    logger.warn('missing something')
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

License
=======

dhis2.py's source is provided under MIT license.
See LICENCE for details.

* Copyright (c), 2018, David Huser


.. |Latest version| image:: https://img.shields.io/pypi/v/dhis2.py.svg?label=pip&style=flat-square
   :target: https://pypi.org/project/dhis2.py
   :alt: PyPi version

.. |Build| image:: https://img.shields.io/travis/davidhuser/dhis2.py/master.svg?label=travis%20ci&style=flat-square
   :target: https://travis-ci.org/davidhuser/dhis2.py
   :alt: Travis build

.. |BuildWin| image:: https://img.shields.io/appveyor/ci/davidhuser/dhis2-py.svg?label=appveyor%20ci&style=flat-square
   :target: https://ci.appveyor.com/project/davidhuser/dhis2-py
   :alt: Appveyor build

.. |Coverage| image:: https://img.shields.io/coveralls/davidhuser/dhis2.py/master.svg?style=flat-square
   :target: https://coveralls.io/github/davidhuser/dhis2.py?branch=master
   :alt: Test coverage

.. |LGTM| image:: https://img.shields.io/lgtm/grade/python/g/davidhuser/dhis2.py.svg?label=code%20quality&style=flat-square
   :target: https://lgtm.com/projects/g/davidhuser/dhis2.py
   :alt: Code quality

.. |CodeClimate| image:: https://img.shields.io/codeclimate/maintainability/davidhuser/dhis2.py.svg?style=flat-square
   :target: https://codeclimate.com/github/davidhuser/dhis2.py/maintainability
   :alt: Code maintainability