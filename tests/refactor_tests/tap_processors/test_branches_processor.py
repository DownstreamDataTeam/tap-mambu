import inspect
import os

from mock import MagicMock

from ..constants import config_json
from ..helpers import GeneratorMock

FIXTURES_PATH = f"{os.path.dirname(os.path.abspath(inspect.stack()[0][1]))}/fixtures"


def test_branches_accounts_processor():
    from singer.catalog import Catalog
    catalog = Catalog.load(f"{FIXTURES_PATH}/catalog.json")
    client_mock = MagicMock()

    from tap_mambu.tap_mambu_refactor.tap_processors.branches_processor import BranchesProcessor
    processor = BranchesProcessor(catalog=catalog,
                                  stream_name="branches",
                                  client=client_mock,
                                  config=config_json,
                                  state={'currently_syncing': 'branches'},
                                  sub_type="self",
                                  generators=[GeneratorMock([])])

    assert processor.endpoint_deduplication_key == "id"
