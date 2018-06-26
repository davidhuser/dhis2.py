import json

from .common import *
from .exceptions import ClientException


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


def chunk(num, thresh=10000):
    """
    Chunk a number into a list of numbers
    :param num: the number to chunk
    :param thresh: the maximum value of a chunk
    """
    while num:
        to_yield = min(num, thresh)
        yield to_yield
        num -= to_yield
