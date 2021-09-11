=========
CHANGELOG
=========

2.3.0
-----
- Feat: ``import_response_ok()`` to check on the importSummary of a DHIS2 import request for data values, events, metadata.

2.2.1
-----
- Fix: no default ``timeout`` parameter value (previous: 5 seconds) in ``Api.get()``. Implementations are advised to set this per connection (see requests documentation).


2.2.0
-----
- Feat: allow a ``timeout`` parameter in ``Api.get()`` to prevent requests from waiting indefinitely on a response (see `here <https://docs.python-requests.org/en/master/user/quickstart/#timeouts>`_)


2.1.2
-----
- Fix: set ``python_requires`` correctly in setup.py

2.1.1
-----
- Chore: drop `black` from dev-packages

2.1.0
-----
- Chore: Drop Python 2.7 and 3.5 support, Python 3.6+ is required
- Chore: use type annotations, flake8, mypy, and black

2.0.2
-----
- Chore: Maintenance release for documentation

2.0.1
-----
- Chore: Maintenance release for documentation

2.0.0
-----
- Chore: ``Dhis`` class was renamed to ``Api``
- Chore: ``APIException`` was renamed to ``RequestException``
- Feat: ``generate_uids()`` was completely removed. Use ``generate_uid()`` for a single UID, not requiring an existing ``Api`` instance.

1.8.0
-----
- Feat: allow ``delete()`` to have payload

1.7.3
------
- Chore: update *requests* to 2.20.0 due to `CVE-2018-18074 <https://nvd.nist.gov/vuln/detail/CVE-2018-18074>`_

1.7.2
------
- Chore: pin test dependencies, CI tests

1.7.1
------
- Feat: allow ``delete()`` to have params

1.7.0
------
- Feat: ``clean_obj()`` to recursively remove e.g. ``userGroupAccesses`` keys from an object
- Chore: require ``six`` as a dependency

1.6.2
-----
- Chore: various minor bug fixes and clean up

1.6.1
-----
- Feat: argument ``local`` to ``generate_uids()`` to create UIDs locally (no network calls to DHIS2)
- Feat: ``pretty_json()`` to print easy-readable JSON

1.5.3
------
- Feat: partitioned payloads with ``.post_partitioned()`` to split large payloads into smaller ones

1.5.2
-----
- Feat: allow to use ``https://`` scheme and *no scheme* for localhost urls (e.g. ``localhost:8080``)
- Feat: allow to use ``json`` alongside ``data`` argument in Dhis ``.get`` / ``.post`` / ``.put`` / ``.patch`` to standardize with ``requests``

1.5.1
-----
- Feat: ``setup_logger()`` to choose if caller and line of script should be included - e.g. ``[script:123]``
- Chore: CI testing fixes

1.5.0
-----
- Feat: allow list of tuples as params to HTTP requests - `#4 <https://github.com/davidhuser/dhis2.py/issues/4>`_
- Fix: ``get_paged.page_size`` validation
- Feat: this changelog

1.4.x
-----
- Feat: ``merge`` support for ``get_sqlview()``
- Feat: enable paging of events
