Get
====

Normal method: ``api.get()``

Paging
------

.. autofunction:: dhis2.api

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
---------

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
------------------------

Usually defaults to JSON but you can get other file types:

.. code:: python

    r = api.get('organisationUnits/Rp268JB6Ne4', file_type='xml')
    print(r.text)
    # <?xml version='1.0' encoding='UTF-8'?><organisationUnit ...

    r = api.get('organisationUnits/Rp268JB6Ne4', file_type='pdf')
    with open('/path/to/file.pdf', 'wb') as f:
        f.write(r.content)