import json
import re
import sys

from .exceptions import ClientException

# unicode support is already ok for Py3
if sys.version_info < (3,):
    import unicodecsv as csv
else:
    import csv


def load_csv(path, delimiter=','):
    """Load CSV file efficiently.
    Detects delimiter automatically.

    Usage:

    for row in load_csv('/path/to/file'):
        print(row)

    :type delimiter: char
    :param path: file path
    :return: row (from generator)
    """
    try:
        with open(path, 'r') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            for row in reader:
                yield row
    except FileNotFoundError:
        raise ClientException("File not found: {}".format(path))


def load_json(path):
    """Load JSON file from path
    :param path: file path
    :return: dict
    """
    try:
        with open(path, 'r') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        raise ClientException("File not found: {}".format(path))
