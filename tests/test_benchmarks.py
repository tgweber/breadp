################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains all Benchmark-related tests
#
################################################################################

from unittest import mock
import pytest

from breadp.benchmarks import Benchmark
from breadp.checks.metadata import DescriptionsNumberCheck
from breadp.evaluations import IsBetweenEvaluation
from breadp.rdp import RdpFactory, Rdp
from util import mocked_requests_get, mocked_requests_head


@mock.patch('requests.head', side_effect=mocked_requests_head)
@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_benchmark(mock_get, mock_head):
    b = Benchmark()
    c1 = DescriptionsNumberCheck()
    rdp1 = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    rdp2 = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    c1.check(rdp1)
    c1.check(rdp2)
    b.add_evaluation(IsBetweenEvaluation([c1], 1, 100))
    assert len(b.evaluations) == 1
    assert b.score(rdp1) == 1
    assert b.score(rdp2) == 0
