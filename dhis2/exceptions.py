class Dhis2PyException(Exception):
    """Base Exception all other exceptions inherit from"""


class APIException(Dhis2PyException):
    """Indicate exception that involve responses from DHIS2's API."""


class ClientException(Dhis2PyException):
    """Indicate exceptions that don't involve interaction with DHIS2's API."""
