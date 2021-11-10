import json

import pytest

import tap_mambu


def test_tap(capsys):
    # Test discover
    tap_mambu.parsed_args = tap_mambu.argparse.Namespace()
    tap_mambu.parsed_args.config = tap_mambu.singer.utils.load_json("./config.json")
    tap_mambu.parsed_args.catalog = None
    tap_mambu.parsed_args.state = {}
    tap_mambu.parsed_args.discover = True
    tap_mambu.parsed_args.properties = None
    tap_mambu.main()
    captured = capsys.readouterr()
    with open("./expected_catalog.json") as fd:
        expected_output = json.loads(fd.read())
    actual_output = json.loads(captured.out)
    assert expected_output == actual_output

    # Test run
    tap_mambu.parsed_args = tap_mambu.argparse.Namespace()
    tap_mambu.parsed_args.config = tap_mambu.singer.utils.load_json("./config.json")
    tap_mambu.parsed_args.catalog = tap_mambu.Catalog.load("./catalog.json")
    tap_mambu.parsed_args.state = tap_mambu.singer.utils.load_json("./state.json")
    tap_mambu.parsed_args.discover = None
    tap_mambu.parsed_args.properties = None
    tap_mambu.main()
    captured = capsys.readouterr()
    with open("./expected_output.json") as fd:
        expected_output = fd.read()
    actual_output = captured.out

    expected_output_lines = expected_output.split("\n")
    actual_output_lines = actual_output.split("\n")

    assert len(expected_output_lines) == len(actual_output_lines)

    for line_no in range(len(actual_output_lines)):
        # Assert blank line, if blank expected
        if (expected_output_lines[line_no] == actual_output_lines[line_no]) or \
           (expected_output_lines[line_no] and actual_output_lines[line_no]):
            continue
        expected_record = json.loads(expected_output_lines[line_no])
        actual_record = json.loads(actual_output_lines[line_no])
        expected_record.pop("time_extracted", None)
        actual_record.pop("time_extracted", None)
        # Assert record without 'time_extracted' attribute
        assert expected_record == actual_record
