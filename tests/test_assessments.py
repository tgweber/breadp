################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains all Assessment-related tests
#
################################################################################

from unittest import mock

from util import mocked_requests_get
from breadp.assessments.doi import DoiAssessment
from breadp.rdp.rdp import RdpFactory, Rdp

# Tests the PID check
@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_pid_assessment(mock_get):
    a = DoiAssessment()
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    a.assess(rdp)
    assert len(a.log) == 1
    assert a.log.log[-1].assessment == 1
