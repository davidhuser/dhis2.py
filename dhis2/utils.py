# -*- coding: utf-8 -*-

"""
dhis2.utils
~~~~~~~~~~~

This module provides utility functions that are used within dhis2.py
"""

import json
import os
import re
import random
import string
from six import string_types, iteritems

from unicodecsv import DictReader
from pygments import highlight
from pygments.lexers.data import JsonLexer
from pygments.formatters.terminal import TerminalFormatter

from .exceptions import ClientException


def load_csv(path, delimiter=','):
    """
    Load CSV file from path and yield CSV rows

    Usage:

    for row in load_csv('/path/to/file'):
        print(row)
    or
    list(load_csv('/path/to/file'))

    :param path: file path
    :param delimiter: CSV delimiter
    :return: a generator where __next__ is a row of the CSV
    """
    try:
        with open(path, 'rb') as csvfile:
            reader = DictReader(csvfile, delimiter=delimiter)
            for row in reader:
                yield row
    except (OSError, IOError):
        raise ClientException("File not found: {}".format(path))


def load_json(path):
    """
    Load JSON file from path
    :param path: file path
    :return: A Python object (e.g. a dict)
    """
    try:
        with open(path, 'r') as json_file:
            return json.load(json_file)
    except (OSError, IOError):
        raise ClientException("File not found: {}".format(path))


def partition_payload(data, key, thresh):
    """
    Yield partitions of a payload

    e.g. with a threshold of 2:

    { "dataElements": [1, 2, 3] }
    -->
    { "dataElements": [1, 2] }
       and
    { "dataElements": [3] }

    :param data: the payload
    :param key: the key of the dict to partition
    :param thresh: the maximum value of a chunk
    :return: a generator where __next__ is a partition of the payload
    """
    data = data[key]
    for i in range(0, len(data), thresh):
        yield {key: data[i:i + thresh]}


def search_auth_file(filename='dish.json'):
    """
    Search filename in
    - A) DHIS_HOME (env variable)
    - B) current user's home folder
    :param filename: the filename to search for
    :return: full path of filename
    """
    if 'DHIS_HOME' in os.environ:
        return os.path.join(os.environ['DHIS_HOME'], filename)
    else:
        home_path = os.path.expanduser(os.path.join('~'))
        for root, dirs, files in os.walk(home_path):
            if filename in files:
                return os.path.join(root, filename)
    raise ClientException("'{}' not found - searched in $DHIS_HOME and in home folder".format(filename))


def version_to_int(value):
    """
    Convert version info to integer
    :param value: the version received from system/info, e.g. "2.28"
    :return: integer from version, e.g. 28, None if it couldn't be parsed
    """
    # remove '-SNAPSHOT'
    value = value.replace('-SNAPSHOT', '')
    # remove '-RCx'
    if '-RC' in value:
        value = value.split('-RC', 1)[0]
    try:
        return int(value.split('.')[1])
    except (ValueError, IndexError):
        return


def generate_uid():
    """
    Create DHIS2 UID matching to Regex
    ^[A-Za-z][A-Za-z0-9]{10}$
    :return: UID string
    """
    # first must be a letter
    first = random.choice(string.ascii_letters)
    # rest must be letters or numbers
    rest = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
    return first + rest


def is_valid_uid(uid):
    """
    :return: True if it is a valid DHIS2 UID, False if not
    """
    pattern = r'^[A-Za-z][A-Za-z0-9]{10}$'
    if not isinstance(uid, string_types):
        return False
    return bool(re.compile(pattern).match(uid))


def pretty_json(obj):
    """
    Print JSON with indentation and colours
    :param obj: the object to print - can be a dict or a string
    """
    if isinstance(obj, string_types):
        try:
            obj = json.loads(obj)
        except ValueError:
            raise ClientException("`obj` is not a json string")
    json_str = json.dumps(obj, sort_keys=True, indent=2)
    print(highlight(json_str, JsonLexer(), TerminalFormatter()))


def clean_obj(obj, remove):
    """
    Recursively remove keys from list/dict/dict-of-lists/list-of-keys/nested ...,
     e.g. remove all sharing keys or remove all 'user' fields
    This should result in the same as if running in bash: `jq del(.. | .publicAccess?, .userGroupAccesses?)`
    :param obj: the dict to remove keys from
    :param remove: keys to remove - can be a string or iterable
    """
    if isinstance(remove, string_types):
        remove = [remove]
    try:
        iter(remove)
    except TypeError:
        raise ClientException("`remove` could not be removed from object: {}".format(repr(remove)))
    else:
        if isinstance(obj, dict):
            obj = {
                key: clean_obj(value, remove)
                for key, value in iteritems(obj)
                if key not in remove
            }
        elif isinstance(obj, list):
            obj = [
                clean_obj(item, remove)
                for item in obj
                if item not in remove
            ]
        return obj
