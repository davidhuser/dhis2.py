Contribute
==========

Feedback welcome!

- Add `issue <https://github.com/davidhuser/dhis2.py/issues/new>`_
- Install the dev environment (see below)
- Fork, add changes to *master* branch, ensure tests pass with full coverage and add a Pull Request

.. code:: bash

    pip install pipenv
    git clone https://github.com/davidhuser/dhis2.py
    cd dhis2.py
    pipenv install --dev
    pipenv run tests

Unit tests
----------

.. code:: bash

    pipenv run tests