dhis2.py
========

|Latest version| |Build| |BuildWin| |Coverage| |LGTM| |CodeClimate|

A Python library for `DHIS2 <https://dhis2.org>`_ wrapping `requests <https://github.com/requests/requests>`_
for **general-purpose API interaction** with DHIS2. It attempts to be **useful for any data/metadata import tasks**
including various utilities like file loading, UID generation and logging. A strong focus is on JSON.

Supported and tested on Python 2 and 3 on Linux/macOS, Windows and DHIS2 versions >= 2.25.

* Code is hosted at `github.com/davidhuser/dhis2.py <https://github.com/davidhuser/dhis2.py>`_


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation.rst
   quickstart.rst
   api_instance.rst
   get.rst
   create_update_delete.rst
   utils.rst
   logging.rst
   exceptions.rst
   examples.rst
   changelog.rst
   modules.rst
   contribute.rst




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


License
--------

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
