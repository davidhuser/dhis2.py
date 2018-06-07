import json
import re
import sys

from .exceptions import ClientException

if sys.version_info < (3,):
    import unicodecsv as csv
else:
    import csv


def load_csv(path):
    """Load CSV file efficiently.
    Detects delimiter automatically.

    Usage:

    for row in load_csv('/path/to/file'):
        print(row)

    :param path: file path
    :return: row (from generator)
    """
    with open(path, 'rb') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(), delimiters=';,')
        csvfile.seek(0)
        reader = csv.DictReader(csvfile, dialect=dialect)
        for row in reader:
            yield row


def load_json(path):
    """Load JSON file from path
    :param path: file path
    :return: dict
    """
    with open(path, 'r') as json_file:
        try:
            return json.load(json_file)
        except ValueError:
            raise ClientException("File empty: {}".format(path))
        except IOError:
            raise ClientException("File not found: {}".format(path))


def valid_uid(uid):
    """Check if string matches DHIS2 UID pattern
    :return: bool
    """
    return re.compile("^[A-Za-z][A-Za-z0-9]{10}$").match(uid)
