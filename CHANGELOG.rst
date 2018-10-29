=========
CHANGELOG
=========

1.7.3
------
- update _requests_ to 2.20.0 due to `CVE-2018-18074 <https://nvd.nist.gov/vuln/detail/CVE-2018-18074>`_

1.7.2
------
- maintenance & testing environment: pin test dependencies, CI tests

1.7.1
------
- allow ``delete()`` to have params

1.7.0
------
- ``clean_obj`` to recursively remove e.g. ``userGroupAccesses`` keys from an object
- require ``six`` as a dependency

1.6.2
-----
- various minor bug fixes and clean up

1.6.1
-----
- argument ``local`` to ``.generate_uids()`` to create UIDs locally (no network calls to DHIS2)
- ``pretty_json()`` to print easy-readable JSON

1.5.3
------
- partitioned payloads with ``.post_partitioned()`` to split large payloads into smaller ones

1.5.2
-----
- allow to use ``https://`` scheme and *no scheme* for localhost urls (e.g. ``localhost:8080``)
- allow to use ``json`` alongside ``data`` argument in Dhis ``.get`` / ``.post`` / ``.put`` / ``.patch`` to standardize with ``requests``

1.5.1
-----
- ``setup_logger`` to choose if caller and line of script should be included - e.g. ``[script:123]``
- CI testing fixes

1.5.0
-----
- allow list of tuples as params to HTTP requests - `#4 <https://github.com/davidhuser/dhis2.py/issues/4>`_
- ``get_paged.page_size`` validation
- this changelog

1.4.x
-----
- ``merge`` support for ``get_sqlview``
- enable paging of events
