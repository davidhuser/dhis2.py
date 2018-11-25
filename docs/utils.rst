Utilities
==========

Load JSON file
---------------

.. code:: python

    from dhis2 import load_json

    json_data = load_json('/path/to/file.json')
    print(json_data)
    # { "id": ... }


Load CSV file
-------------

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
-------------

Create UIDs:

.. code:: python

    uids = api.generate_uids(20000)
    print(uids)
    # ['Rp268JB6Ne4', 'fa7uwpCKIwa', ... ]

If you want UIDs generated on the server, add ``local=False``.


Validate UID
------------

.. code:: python

    uid = 'MmwcGkxy876'
    print(is_valid_uid(uid))
    # True

    uid = 25329
    print(is_valid_uid(uid))
    # False


Clean an object
----------------

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
-----------------

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
