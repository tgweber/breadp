################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains all Evaluation-related tests
#
################################################################################

from unittest import mock

from util import mocked_requests_get
from breadp.evaluations.doi import DoiEvaluation
from breadp.evaluations.metadata import DescriptionEvaluation
from breadp.rdp.rdp import RdpFactory, Rdp

# Tests the PID check
@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_pid_evaluation(mock_get):
    a = DoiEvaluation()
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    a.evaluate(rdp)
    assert len(a.log) == 1
    assert a.log.log[-1].evaluation == 1

# Test the Description Evaluation
@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_description_evaluation(mock_get):
    a = DescriptionEvaluation()
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    a.evaluate(rdp)
    assert len(a.log) == 1
    assert a.log.log[-1].evaluation == 1
