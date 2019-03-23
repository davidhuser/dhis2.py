from dhis2 import Api, RequestException, setup_logger, logger

"""
Add "(updated)" to all Data Elements that contain "ANC" in its name.
Uses the method PUT.
Print errors if it failed.
"""

# Create a Api object
api = Api('play.dhis2.org/dev', 'admin', 'district')

# setup the logger
setup_logger()


def main():
    # Print DHIS2 Info
    logger.warn("You are running on DHIS2 version {} revision {} - "
                "Last Analytics generation was at: {}".format(api.version,
                                                              api.revision,
                                                              api.info.get('lastAnalyticsTableSuccess')))

    # GET dataElements that contain ANC in its name
    params = {
        'filter': 'name:like:ANC',
        'paging': False,
        'fields': ':owner'
    }
    data_elements = api.get('dataElements', params=params).json()

    # Loop through each dataElement
    for de in data_elements['dataElements']:
        # Add (updated) to the name
        de['name'] = '{} (updated)'.format(de['name'])

        try:
            # Replace the dataElement on the server
            api.put('dataElements/{}'.format(de['id']), params={'mergeMode': 'REPLACE'}, json=de)
        except RequestException as e:
            # Print errors returned from DHIS2
            logger.error("Updating DE '{}' ({}) failed: {}".format(de['name'], de['id'], e))
        else:
            # Print success message
            logger.info("Updated DE '{}' ({}) successful".format(de['name'], de['id']))


if __name__ == '__main__':
    main()
