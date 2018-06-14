import requests


class Dhis2PyException(Exception):
    """ Base exception for all"""


class APIException(Dhis2PyException, requests.RequestException):
    """DHIS2 API call error"""

    def __init__(self, code, url, description, *args, **kwargs):
        super(APIException, self).__init__(*args, **kwargs)
        self.code = code
        self.url = url
        self.description = description

    def __repr__(self):
        return "Dhis2ApiException({}, '{}', '{}')".format(
            self.code,
            self.url,
            self.description
        )

    def __str__(self):
        return 'code: {}, url: {}, description: {}'.format(
            self.code,
            self.url,
            self.description
        )


class ClientException(Dhis2PyException):
    """Exceptions not involving DHIS2's API."""
