################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains all Check-related tests
#
################################################################################

import re
from unittest import mock

from util import mocked_requests_get, base_init_check_test
from breadp.checks import IsValidDOICheck
from breadp.rdp.rdp import RdpFactory, Rdp

# Tests the PID check
@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_is_valid_doi_check(mock_get):
    check = IsValidDOICheck()
    assert base_init_check_test(check, 0)

    # Successful
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    check.check(rdp)
    assert check.status == "success"
    assert len(check.log) == 1
    assert check.log[-1]["status"] == check.status

    # Uncheckeable
    pid = rdp.pid
    rdp.pid = ""
    check.check(rdp)
    assert check.status == "uncheckable"
    assert len(check.log) == 2
    assert check.log[-2]["status"] == "success"
    rdp.pid = pid

    # Failure
    rdp = RdpFactory.create("10.123/zenodo.3490396-failure", "zenodo", token="123")
    check.check(rdp)
    assert check.status == "failure"
    assert len(check.log) == 3
    assert check.log[-3]["status"] == "success"
    assert check.log[-2]["status"] == "uncheckable"

