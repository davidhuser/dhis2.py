from dhis2 import Dhis, APIException, setup_logger, logger, load_json

"""
Import a metadata JSON file from your computer.
"""

# Create a Dhis object
api = Dhis('play.dhis2.org/dev', 'admin', 'district')

# setup the logger
setup_logger(include_caller=False)


def main():
    # load the JSON file that sits next to the script
    data = load_json('2_import_metadata.json')

    try:
        # import metadata
        api.post('metadata.json', params={'preheatCache': False, 'strategy': 'CREATE'}, json=data)
    except APIException as e:
        logger.error("Import failed: {}".format(e))
    else:
        logger.info("Import successful!")


if __name__ == '__main__':
    main()
