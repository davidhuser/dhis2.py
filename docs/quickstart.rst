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

see usage for more methods.