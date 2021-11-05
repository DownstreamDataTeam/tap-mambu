import pytest

from tap_mambu import main


def test_radu_1():
    main()
    assert 1 == 1
