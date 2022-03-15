import inspect
import os

from mock import MagicMock

from ..constants import config_json
from ..helpers import GeneratorMock

FIXTURES_PATH = f"{os.path.dirname(os.path.abspath(inspect.stack()[0][1]))}/Fixtures"


def test_centres_processor():
    from singer.catalog import Catalog
    catalog = Catalog.load(f"{FIXTURES_PATH}/processor_catalog.json")
    client_mock = MagicMock()

    from tap_mambu.tap_mambu_refactor.tap_processors.centres_processor import CentresProcessor
    processor = CentresProcessor(catalog=catalog,
                                 stream_name="centres",
                                 client=client_mock,
                                 config=config_json,
                                 state={'currently_syncing': 'centres'},
                                 sub_type="self",
                                 generators=[GeneratorMock([])])

    assert processor.endpoint_deduplication_key == "id"