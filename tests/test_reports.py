################################################################################
# Copyright: Tobias Weber 2020
#
# Apache 2.0 License
#
# This file contains all Check-related tests
#
################################################################################

from unittest import mock
import pytest
import sys

from rdp import RdpFactory

from util import \
    base_init_check_test, \
    get_rdps, \
    mocked_requests_get, \
    mocked_requests_head

from breadp.benchmarks.example import BPGBenchmark
from breadp.checks.metadata import DescriptionsLengthCheck
from breadp.evaluations import Evaluation, IsBetweenEvaluation
from breadp.reports import BenchmarkReport, CheckReport, EvaluationReport

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_check_report(mock_get):
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo")
    check = DescriptionsLengthCheck()
    report = CheckReport(rdp.pid, check)
    assert report.name == "DescriptionsLengthCheck"
    assert report.version == check.version
    assert report.id == check.id
    assert report.description == check.description
    assert report.entry is None

    check.check(rdp)
    report = CheckReport(rdp.pid, check)
    r = report.todict()
    assert r["name"] == "DescriptionsLengthCheck"
    assert r["version"] == check.version
    assert r["success"]
    import pprint
    pprint.pprint(r)
    assert r["result"][0] == 69
    assert r["result"][1] == 3
    assert r["msg"] == ""
    assert r["type"] == "deterministic"

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_evaluation_report(mock_get):
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo")
    check = DescriptionsLengthCheck()
    check.check(rdp)
    ev = Evaluation([])
    with pytest.raises(ValueError):
        report = EvaluationReport(rdp.pid, ev)
    ev = IsBetweenEvaluation([check], 1.0, 10.0)
    report = EvaluationReport(rdp.pid, ev)
    assert len(report.checks) == len(ev.checks)
    r = report.todict()
    for field in ("name", "description", "checks", "version", "id",
                  "rounded", "evaluation"):
        assert field in r.keys()
    assert '\n' not in r["description"]
    assert r["evaluation"] == ev.evaluate(rdp.pid)
    assert r["rounded"] == ev.rounded

@mock.patch('requests.head', side_effect=mocked_requests_head)
@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_benchmark_reporting(mock_get, mock_head):
    rdps = get_rdps()
    bb = BPGBenchmark()
    bb.check_all(rdps[8])
    report = BenchmarkReport(rdps[8],  bb)
    r = report.todict()
    assert r["pid"] == rdps[8].pid
    for field in ("name", "description", "check_reports", "version", "id",
                  "rounded", "score", "evaluation_reports", "aggregation_info", "precision",
                 "rounded"):
        assert field in r.keys()
    assert len(r["evaluation_reports"]) == 31

    assert report.check_reports[0].name == "IsValidDoiCheck"
    assert report.evaluation_reports[0].evaluation == 0
    assert report.evaluation_reports[2].evaluation == round(2/3, 10)
    assert report.evaluation_reports[5].evaluation == 1

    assert report.rounded == bb.rounded
    assert report.score == bb.score(rdps[8])
    assert report.aggregation_info == bb.aggregation_info()
    assert report.precision == sys.float_info.mant_dig
    assert len(report.check_reports) == 40
