import os
import contextlib


@contextlib.contextmanager
def override_environ(**kwargs):
    save_env = dict(os.environ)
    for key, value in kwargs.items():
        if value is None:
            del os.environ[key]
        else:
            os.environ[key] = value
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(save_env)


BASEURL = "https://play.dhis2.org/demo"
API_URL = "{}/api".format(BASEURL)
