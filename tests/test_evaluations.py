################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains all Evaluation-related tests
#
################################################################################

from unittest import mock

from util import mocked_requests_get, mocked_requests_head
from breadp.evaluations.doi import DoiEvaluation
from breadp.evaluations.metadata import DescriptionEvaluation
from breadp.rdp.rdp import RdpFactory, Rdp

# Tests the PID check
@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_pid_evaluation(mock_get):
    e = DoiEvaluation()
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 1
    assert e.log.log[-1].evaluation == 1

# Test the Description Evaluation
@mock.patch('requests.get', side_effect=mocked_requests_get)
@mock.patch('requests.head', side_effect=mocked_requests_head)
def test_description_evaluation(mock_get, mock_head):
    e = DescriptionEvaluation(4)
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 1
    assert e.log.log[-1].evaluation == 1

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 2
    assert e.log.log[-1].evaluation == 1/13

    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    e.evaluate(rdp)

    for c in e.checks.values():
        print("{}: {} - {}".format(c.success,c.result.outcome, c.log.log[-1].msg))
    assert len(e.log) == 3
    assert e.log.log[-1].evaluation == 4/13
