#!/usr/bin/env python3

import sys
import json
import singer
import coverage
import time
import os.path

LOGGER = singer.get_logger()

REQUIRED_CONFIG_KEYS = [
    'subdomain',
    'start_date',
    'user_agent'
]

DEFAULT_PAGE_SIZE = 500


def get_test_coverage(func):
    def wrapper():
        if os.environ.get('GET_TEST_COVERAGE', False):
            cov = coverage.Coverage(auto_data=True, data_suffix=time.perf_counter(), cover_pylib=True, branch=True,
                                    check_preimported=True,
                                    omit=[__file__],
                                    source=[os.path.dirname(__file__)])
            cov.start()
            func()
            cov.stop()
            cov.save()
        else:
            func()
    return wrapper


@get_test_coverage
@singer.utils.handle_top_exception(LOGGER)
def main():
    from tap_mambu.client import MambuClient
    from tap_mambu.sync import sync
    from tap_mambu.discover import discover

    parsed_args = singer.utils.parse_args(REQUIRED_CONFIG_KEYS)

    with MambuClient(parsed_args.config.get('username'),
                     parsed_args.config.get('password'),
                     parsed_args.config.get('apikey'),
                     parsed_args.config['subdomain'],
                     parsed_args.config.get('apikey_audit'),
                     int(parsed_args.config.get('page_size', DEFAULT_PAGE_SIZE)),
                     user_agent=parsed_args.config['user_agent']) as client:

        state = {}
        if parsed_args.state:
            state = parsed_args.state

        if parsed_args.discover:
            LOGGER.info('Starting discover')
            json.dump(discover().to_dict(), sys.stdout, indent=2)
            LOGGER.info('Finished discover')
        elif parsed_args.catalog:
            sync(client=client,
                 config=parsed_args.config,
                 catalog=parsed_args.catalog,
                 state=state)

if __name__ == '__main__':
    main()
