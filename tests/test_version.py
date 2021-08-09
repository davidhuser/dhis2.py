from dhis2.__version__ import (
    __title__,
    __description__,
    __url__,
    __version__,
    __author__,
    __author_email__,
    __license__
)

def test_version():
    assert all([
        __title__,
        __description__,
        __url__,
        __version__,
        __author__,
        __author_email__,
        __license__
    ])