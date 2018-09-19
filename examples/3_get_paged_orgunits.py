from datetime import datetime

from dhis2 import Dhis, setup_logger, logger

"""
Log every orgunit but use paging instead of fetching the whole result at once.
Print a warning if the organisation unit was opened after January 1st 1990.
"""

# Create a Dhis object
api = Dhis('play.dhis2.org/dev', 'admin', 'district')

# setup the logger
setup_logger()


def main():
    # get 50 organisation units per call to the API
    for page in api.get_paged('organisationUnits', params={'fields': 'id,name,openingDate'}):

        # loop through the organisation units received
        for ou in page['organisationUnits']:

            # parse the opening date to a Python date
            opening_date = datetime.strptime(ou['openingDate'], '%Y-%m-%dT00:00:00.000')

            # compare date and print message
            if opening_date > datetime(year=1990, month=1, day=1):
                logger.warn("OU '{}' ({}) was opened AFTER 1990-01-01 on {}".format(ou['name'], ou['id'], ou['openingDate'][:-13]))
            else:
                logger.debug("OU '{}' ({}) was opened BEFORE 1990-01-01 on {}".format(ou['id'], ou['name'], ou['openingDate'][:-13]))


if __name__ == '__main__':
    main()
