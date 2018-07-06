import sys

# unicode support is already ok for Py3
if sys.version_info < (3,):
    import unicodecsv as csv  # py2
    string_types = basestring
else:
    import csv  # py3
    string_types = str


try:
    FileNotFoundError  # py3
except NameError:
    FileNotFoundError = IOError  # py2
