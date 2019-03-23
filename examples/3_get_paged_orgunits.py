from datetime import datetime

from dhis2 import Api, setup_logger, logger

"""
Log every orgunit but use paging instead of fetching the whole result at once.
Print a warning if the organisation unit was opened after January 1st 1990.
"""

# Create a Api object
api = Api('play.dhis2.org/dev', 'admin', 'district')

# setup the logger
setup_logger()


def check_opening_date(org_unit):
    ou_name = org_unit['name']
    ou_uid = org_unit['id']
    ou_opening_date = org_unit['openingDate'][:-13]

    # parse the opening date to a Python date
    opening_date = datetime.strptime(ou_opening_date, '%Y-%m-%d')

    msg = "Organisation Unit '{}' ({}) was opened {} 1990-01-01 on {}"

    # compare date and print message
    if opening_date > datetime(year=1990, month=1, day=1):
        logger.warn(msg.format(ou_name, ou_uid, 'AFTER', ou_opening_date))
    else:
        logger.debug(msg.format(ou_name, ou_uid, 'BEFORE', ou_opening_date))


def main():
    # get 50 organisation units per call to the API
    for page in api.get_paged('organisationUnits', params={'fields': 'id,name,openingDate'}):

        # loop through the organisation units received
        for ou in page['organisationUnits']:
            check_opening_date(ou)


if __name__ == '__main__':
    main()
