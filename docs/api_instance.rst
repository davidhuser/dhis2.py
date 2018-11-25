Api instance creation
======================

Authentication in code
-----------------------

Create an API object

.. code:: python

    from dhis2 import Api

    api = Api('play.dhis2.org/demo', 'admin', 'district')

optional arguments:

- ``api_version``: DHIS2 API version
- ``user_agent``: submit your own User-Agent header. This is useful if you need to parse e.g. Nginx logs later.


Authentication from file
-------------------------

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


Api instance attributes
-----------------------

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

System info (this is persisted across the session):

.. code:: python

    print(api.info)
    # {
    #   "lastAnalyticsTableRuntime": "11 m, 51 s",
    #   "systemId": "eed3d451-4ff5-4193-b951-ffcc68954299",
    #   "contextPath": "https://play.dhis2.org/2.30",
    #   ...
