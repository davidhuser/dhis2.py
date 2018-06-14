dhis2.py - Minimalistic Python wrapper for DHIS2
=================================================

|Build| |BuildWin| |Coverage| |PyPi|

Minimalistic API wrapper for `DHIS2 <https://dhis2.org>`_ written in Python.

- Common HTTP operations (GET, POST, PUT, PATCH, DELETE) which return a `requests <https://github.com/requests/requests>`_ response object
- Some utils like file loading (CSV, JSON) and UID generation
- Supported: Python 2.7, 3.4-3.6 and all DHIS2 versions

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

    api = Dhis('play.dhis2.org/demo', 'admin', 'district')


Then run requests on it:

.. code:: python

    print(api.dhis_version())
    # 28

    print(api.info())
    # { "serverDate": "2018-07-25T08:47:48.911", ... }

    r = api.get('organisationUnits/Rp268JB6Ne4', params={'fields': 'id,name'})

    print(r.json())
    # { "name": "Adonkia CHP", "id": "Rp268JB6Ne4" }

    print(r.text)
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

    api = Dhis.from_auth_file('path/to/auth.json')


If no argument is specified, it tries to find a file called ``dish.json`` in:

1. the ``DHIS_HOME`` environment variable
2. your Home folder



Load a JSON file
^^^^^^^^^^^^^^^

.. code:: python

    from dhis2 import Dhis, load_json

    api = Dhis('play.dhis2.org/demo', 'admin', 'district')

    json_data = load_json('/path/to/file.json')
    print(json_data)
    # { "id": ... }

    p = api.post('metadata', data=json_data, params={'preheatCache': False})
    print(p.text)
    # <DHIS2 response>


Load a CSV file
^^^^^^^^^^^^^^

.. code:: python

    from dhis2 import Dhis, load_csv

    for row in load_csv('/path/to/file.csv'):
        print(row)
        # { "id": ... }

        p = api.patch('organisationUnits/{}'.format(row['id']), data=row)
        print(p.text)
        # <DHIS2 response>

    # or for a normal list
    data = list(load_csv('/path/to/file.csv'))


API paging
^^^^^^^^^^^

Paging for large GET requests (JSON only)

.. code:: python

    from dhis2 import Dhis, load_csv

    api = Dhis('play.dhis2.org/demo', 'admin', 'district')

    for page in api.get_paged('organisationUnits', page_size=100):
        print(page)
        # { "organisationUnits": [ {...}, {...} ] } (100 elements each)


Generate UIDs
^^^^^^^^^^^^^

Get server-generated UIDs (not limited to 10000)

.. code:: python

    from dhis2 import generate_uids

    uids = generate_uids(20000)
    print(uids)
    # ['Rp268JB6Ne4', 'fa7uwpCKIwa', ... ]


Exceptions
^^^^^^^^^^^

There should be only two exceptions:

- ``APIException``: DHIS2 didn't like what you requested. See the exception's ``code``, ``url`` and ``description``.
- ``ClientException``: Something didn't work with the client not involving DHIS2.

They both inherit from ``Dhis2PyException``.

Testing
--------

.. code:: bash

    pipenv install --dev
    pipenv run tests


Contribute
-----------

- Add `issue <https://github.com/davidhuser/dhis2.py/issues/new>`_
- Fork, test, add code, add tests, test, push, Pull Request

.. |Build| image:: https://travis-ci.org/davidhuser/dhis2.py.svg?branch=master
   :target: https://travis-ci.org/davidhuser/dhis2.py

.. |BuildWin| image:: https://ci.appveyor.com/api/projects/status/9lkxdi8o8r8o5jy7?svg=true
   :target: https://ci.appveyor.com/project/d4h-va/dhis2-py

.. |Coverage| image:: https://coveralls.io/repos/github/davidhuser/dhis2.py/badge.svg?branch=master
   :target: https://coveralls.io/github/davidhuser/dhis2.py?branch=master

.. |PyPi| image:: https://img.shields.io/pypi/v/dhis2.py.svg
   :target: https://pypi.org/project/dhis2.py

