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
from rdp import RdpFactory, Rdp
from rdp.exceptions import CannotCreateRDPException

from breadp.benchmarks import Benchmark
from breadp.benchmarks.example import BPGBenchmark
from breadp.checks.metadata import DescriptionsNumberCheck
from breadp.evaluations import IsBetweenEvaluation

from util import mocked_requests_get, mocked_requests_head, get_rdps

@mock.patch('requests.head', side_effect=mocked_requests_head)
@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_benchmark(mock_get, mock_head):
    b = Benchmark()
    c1 = DescriptionsNumberCheck()
    rdp1 = RdpFactory.create("10.5281/zenodo.3490396", "zenodo")
    rdp2 = RdpFactory.create("10.5281/zenodo.badex1", "zenodo")
    c1.check(rdp1)
    c1.check(rdp2)
    b.add_evaluation(IsBetweenEvaluation([c1], 1, 100))
    assert len(b.evaluations) == 1
    assert b.score(rdp1) == 1
    assert b.score(rdp2) == 0

@mock.patch('requests.head', side_effect=mocked_requests_head)
@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_full_benchmark(mock_get, mock_head):
    rdps = get_rdps()
    bb = BPGBenchmark()
    for rdp in rdps:
        bb.check_all(rdp)
    assert bb.score(rdps[0]) == 1
    assert bb.score(rdps[1]) == 0
    assert bb.score(rdps[2]) == round((487/30)/34, 10)
    assert bb.score(rdps[3]) == round(16.5/33, 10)
    assert bb.score(rdps[4]) == round(12.4/28, 10)
    assert bb.score(rdps[5]) == round(13/28, 10)
    assert bb.score(rdps[6]) == round((26+11/28)/34, 10)
    assert bb.score(rdps[7]) == round((28+22/48)/34, 10)
    assert bb.score(rdps[8]) == round((19+20/21)/31, 10)
    assert bb.score(rdps[9]) == round(26.5/34, 10)

@mock.patch('requests.head', side_effect=mocked_requests_head)
@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_benchmark(mock_get, mock_head):
    b = Benchmark()
    c1 = DescriptionsNumberCheck()
    b.add_evaluation(IsBetweenEvaluation([c1], 1, 100))
    rdp = RdpFactory.create("10.5281/zenodo.exception1", "zenodo")
    with pytest.raises(CannotCreateRDPException) as e:
        b.check_all(rdp)
        str(e).endswith("404")
    rdp = RdpFactory.create("10.5281/zenodo.exception2", "zenodo")
    with pytest.raises(CannotCreateRDPException) as e:
        b.check_all(rdp)
        str(e).endswith("429")

