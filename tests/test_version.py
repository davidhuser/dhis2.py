from dhis2.__version__ import (
    __title__,
    __description__,
    __url__,
    __version__,
    __author__,
    __author_email__,
    __license__,
)


def test_version_attributes():
    assert __title__
    assert __description__
    assert __url__
    assert __version__
    assert __author__
    assert __author_email__
    assert __license__
