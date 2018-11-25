Create / update / delete
========================

Normal methods:

* ``api.post()``
* ``api.put()``
* ``api.patch()``
* ``api.delete()``


Post partitioned payloads
--------------------------

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
