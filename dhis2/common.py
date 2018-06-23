import sys

# unicode support is already ok for Py3
if sys.version_info < (3,):
    import unicodecsv as csv  # py2
else:
    import csv  # py3

try:
    FileNotFoundError  # py3
except NameError:
    FileNotFoundError = IOError  # py2
