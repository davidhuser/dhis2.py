from dhis2 import Api, RequestException, setup_logger, logger, load_json, import_response_ok

"""
Import a metadata JSON file from your computer.
"""

# Create a Api object
api = Api("play.dhis2.org/dev", "admin", "district")

# setup the logger
setup_logger(include_caller=False)


def main():
    # load the JSON file that sits next to the script
    data = load_json("2_import_metadata.json")

    try:
        # import metadata
        r = api.post(
            "metadata.json",
            params={"preheatCache": False, "strategy": "CREATE"},
            json=data,
            timeout=(3, 30)
        )
    except RequestException as e:
        logger.error("Import failed: {}".format(e))
    else:
        if import_response_ok(r.json()):
            logger.info("Import successful!")
        else:
            logger.error("Import not successful: {}".format(r.text))


if __name__ == "__main__":
    main()
