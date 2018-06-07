dhis2.py - minimalistic wrapper around the DHIS2 API
=====================================================

Minimalistic API wrapper for `DHIS2 <https://dhis2.org>`_ written in Python.

- HTTP operations (GET, POST, PUT, PATCH, DELETE) which return a `requests <https://github.com/requests/requests>`_ object
- File loading (CSV, JSON)

Install
--------

.. code:: bash

    pipenv install dhis2.py --user --upgrade


Examples
----------

Basic
^^^^^^

.. code:: python

    from dhis2 import Dhis

    api = Dhis('play.dhis2.org/demo', 'admin', 'district')

    print(api.dhis_version())
    # 28

    print(api.info())
    # { "serverDate": "2018-07-25T08:47:48.911", ... }

    print(api.get('organisationUnits/Rp268JB6Ne4', params={'fields': 'id,name'}).json())
    # { "name": "Adonkia CHP", "id": "Rp268JB6Ne4" }

    # use paging for large GET requests (50 items per page) - JSON only
    for page in api.get_paged('organisationUnits', params={'paging': False}):
        if page and page.get('organisationUnits'):
            print(page)
            # { "organisationUnits": [ {...}, {...} ] }


Load authentication from file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Load from a auth file. Must have the following structure:

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


If no path is specified, it tries to find a file called ``dish.json`` in:

1. the ``DHIS_HOME`` environment variable
2. your Home folder



Load JSON file
^^^^^^^^^^^^^^^

.. code:: python

    from dhis2 import Dhis
    from dhis2 import load_json

    api = Dhis('play.dhis2.org/demo', 'admin', 'district')

    json_data = load_json('/path/to/file.json')
    print(json_data)
    # { "id": ... }

    p = api.post('metadata', data=json_data, params={'preheatCache': False})
    print(p.text)
    # <DHIS2 response>


Load CSV file
^^^^^^^^^^^^^^

.. code:: python

    from dhis2 import Dhis
    from dhis2 import load_csv

    for row in load_csv('/path/to/file.csv'):
        print(row)
        # { "id": ... }

        p = api.patch('organisationUnits/{}'.format(row['id']), data=row)
        print(p.text)
        # <DHIS2 response>

    # or for a normal list
    data = list(load_csv('/path/to/file.csv'))


Validate UID
^^^^^^^^^^^^^

.. code:: python

    from dhis2py import valid_uid

    print(valid_uid('Rp268JB6Ne4')
    # True

    print(valid_uid('bleep')
    # False


Generate UIDs
^^^^^^^^^^^^^

.. code:: python

    from dhis2py import generate_uids

    uids = generate_uids(20000)
    print(uids)
    # ['Rp268JB6Ne4', 'fa7uwpCKIwa', ... ]


