################################################################################
# Copyright: Tobias Weber 2020
#
# Apache 2.0 License
#
# This file contains all Evaluation-related tests
#
################################################################################

import inspect
from unittest import mock
import pytest

from breadp import ChecksNotRunException
from breadp.checks.metadata import DescriptionsNumberCheck
from breadp.evaluations import \
    ContainsAllEvaluation, \
    ContainsAtLeastOneEvaluation, \
    ContainsItemExactlyNTimesEvaluation, \
    DoesNotContainEvaluation, \
    Evaluation, \
    FalseEvaluation, \
    FunctionEvaluation, \
    InListEvaluation, \
    IsBetweenEvaluation, \
    IsIdenticalToEvaluation, \
    TheMoreFalseTheBetterEvaluation, \
    TheMoreTrueTheBetterEvaluation, \
    TrueEvaluation

from util import \
    get_checks, \
    get_rdps, \
    mocked_requests_get, \
    mocked_requests_head

def test_evaluation():
    rdps  = get_rdps()
    e = Evaluation([])
    with pytest.raises(NotImplementedError) as nie:
        e._evaluate(rdps[0])
        assert str(nie).startswith("must be implemented")
    report = e.report()
    for field in ("name", "description", "checks"):
        assert field in report.keys()
    assert report["name"] == "Evaluation"
    assert len(report["checks"]) == 0
    assert report["description"].startswith("Base class and interface")
    assert '\n' not in report["description"]

    e = IsBetweenEvaluation([], 1.0, 1.0)

    with pytest.raises(ValueError) as ve:
        e.evaluate(rdps[0])
        assert str(ve).startswith("No checks in")

@mock.patch('requests.get', side_effect=mocked_requests_get)
@mock.patch('requests.head', side_effect=mocked_requests_head)
def test_is_between_evaluation(mock_get, mock_head):
    rdps = get_rdps()
    checks = get_checks(rdps)
    # empty check
    e = IsBetweenEvaluation([DescriptionsNumberCheck()], 1.0, 2.0)
    assert e.description.endswith("The lower bound is 1.0 the upper bound is 2.0.")
    with pytest.raises(ChecksNotRunException) as cnre:
        e.evaluate(rdps[0])
        assert " has no result for " in str(cnre)
    # one check
    e.checks = [checks["metric"]]
    assert e.evaluate(rdps[0]) == 1
    assert e.evaluate(rdps[1]) == 0
    assert e.evaluate(rdps[3]) == 0

    # multiple checks
    e = IsBetweenEvaluation(checks.values(), 1, 100)
    assert e.evaluate(rdps[0]) == round(2/5, 10)
    assert e.evaluate(rdps[1]) == 0
    assert e.evaluate(rdps[3]) == round(2/5, 10)

@mock.patch('requests.get', side_effect=mocked_requests_get)
@mock.patch('requests.head', side_effect=mocked_requests_head)
def test_is_identical_to_evaluation(mock_get, mock_head):
    rdps = get_rdps()
    checks = get_checks(rdps)
    e = IsIdenticalToEvaluation([checks["metric"]], 2)
    assert e.description.endswith("The comparatum is 2.")
    # one check
    assert e.evaluate(rdps[0]) == 1
    assert e.evaluate(rdps[1]) == 0
    assert e.evaluate(rdps[3]) == 0
    # multiple checks
    e = IsIdenticalToEvaluation(checks.values(), [69,3])
    assert e.evaluate(rdps[0]) == round(1/5, 10)
    assert e.evaluate(rdps[1]) == 0
    assert e.evaluate(rdps[3]) == 0

@mock.patch('requests.get', side_effect=mocked_requests_get)
@mock.patch('requests.head', side_effect=mocked_requests_head)
def test_contains_all_evaluation(mock_get, mock_head):
    rdps = get_rdps()
    checks = get_checks(rdps)
    e = ContainsAllEvaluation([checks["lom"]], [69,3])
    assert e.description.endswith("The items are [69, 3].")
    # one check
    assert e.evaluate(rdps[0]) == 1
    assert e.evaluate(rdps[1]) == 0
    assert e.evaluate(rdps[3]) == 0
    # multiple checks
    e = ContainsAllEvaluation(checks.values(), [3,69])
    assert e.evaluate(rdps[0]) == round(1/5, 10)
    assert e.evaluate(rdps[1]) == 0
    assert e.evaluate(rdps[3]) == 0

@mock.patch('requests.get', side_effect=mocked_requests_get)
@mock.patch('requests.head', side_effect=mocked_requests_head)
def test_contains_at_least_one_evaluation(mock_get, mock_head):
    rdps = get_rdps()
    checks = get_checks(rdps)
    e = ContainsAtLeastOneEvaluation([checks["lob"]], [False])
    assert e.description.endswith("The items are [False].")
    # one check
    assert e.evaluate(rdps[0]) == 1
    assert e.evaluate(rdps[1]) == 0
    assert e.evaluate(rdps[3]) == 1
    # multiple checks
    e = ContainsAtLeastOneEvaluation(checks.values(), [3,69])
    assert e.evaluate(rdps[0]) == round(1/5, 10)
    assert e.evaluate(rdps[1]) == 0
    assert e.evaluate(rdps[3]) == round(1/5, 10)

@mock.patch('requests.get', side_effect=mocked_requests_get)
@mock.patch('requests.head', side_effect=mocked_requests_head)
def test_does_not_contain_evaluation(mock_get, mock_head):
    rdps = get_rdps()
    checks = get_checks(rdps)
    e = DoesNotContainEvaluation([checks["string"]], ["Other"])
    assert e.description.endswith("The items are ['Other'].")
    # one check
    assert e.evaluate(rdps[0]) == 1
    assert e.evaluate(rdps[1]) == 0
    assert e.evaluate(rdps[3]) == 0
    # multiple checks
    e = DoesNotContainEvaluation(checks.values(), [3,69])
    assert e.evaluate(rdps[0]) == round(2/5, 10)
    assert e.evaluate(rdps[1]) == 0
    assert e.evaluate(rdps[3]) == round(1/5, 10)

@mock.patch('requests.get', side_effect=mocked_requests_get)
@mock.patch('requests.head', side_effect=mocked_requests_head)
def test_true_evaluation(mock_get, mock_head):
    rdps = get_rdps()
    checks = get_checks(rdps)
    e = TrueEvaluation([checks["boolean"]])
    # one check
    assert e.evaluate(rdps[0]) == 1
    assert e.evaluate(rdps[1]) == 0
    assert e.evaluate(rdps[3]) == 0
    # multiple checks
    e = TrueEvaluation(checks.values())
    assert e.evaluate(rdps[0]) == 4/5
    assert e.evaluate(rdps[1]) == 0
    assert e.evaluate(rdps[3]) == round(2/5, 10)

@mock.patch('requests.get', side_effect=mocked_requests_get)
@mock.patch('requests.head', side_effect=mocked_requests_head)
def test_false_evaluation(mock_get, mock_head):
    rdps = get_rdps()
    checks = get_checks(rdps)
    e = FalseEvaluation([checks["boolean"]])
    # one check
    assert e.evaluate(rdps[0]) == 0
    assert e.evaluate(rdps[1]) == 1
    assert e.evaluate(rdps[3]) == 1
    # multiple checks
    e = FalseEvaluation(checks.values())
    assert e.evaluate(rdps[0]) == round(3/5, 10)
    assert e.evaluate(rdps[1]) == round(1/5, 10)
    assert e.evaluate(rdps[3]) == round(3/5, 10)

@mock.patch('requests.get', side_effect=mocked_requests_get)
@mock.patch('requests.head', side_effect=mocked_requests_head)
def test_the_more_true_the_better_evaluation(mock_get, mock_head):
    rdps = get_rdps()
    checks = get_checks(rdps)
    e = TheMoreTrueTheBetterEvaluation([checks["lob"]])
    # one check
    assert e.evaluate(rdps[0]) == 0
    assert e.evaluate(rdps[1]) == 0
    assert e.evaluate(rdps[2]) == 1
    # multiple checks
    e = TheMoreTrueTheBetterEvaluation(checks.values())
    assert e.evaluate(rdps[0]) == 0
    assert e.evaluate(rdps[1]) == 0
    assert e.evaluate(rdps[2]) == round(1/5, 10)

@mock.patch('requests.get', side_effect=mocked_requests_get)
@mock.patch('requests.head', side_effect=mocked_requests_head)
def test_the_more_false_the_better_evaluation(mock_get, mock_head):
    rdps = get_rdps()
    checks = get_checks(rdps)
    e = TheMoreFalseTheBetterEvaluation([checks["lob"]])
    # one check
    assert e.evaluate(rdps[0]) == 1
    assert e.evaluate(rdps[1]) == 0
    assert e.evaluate(rdps[2]) == 0
    # multiple checks
    e = TheMoreFalseTheBetterEvaluation(checks.values())
    assert e.evaluate(rdps[0]) == 0.2
    assert e.evaluate(rdps[1]) == 0
    assert e.evaluate(rdps[2]) == 0

@mock.patch('requests.get', side_effect=mocked_requests_get)
@mock.patch('requests.head', side_effect=mocked_requests_head)
def test_contains_item_exactly_n_times_evaluation(mock_get, mock_head):
    rdps = get_rdps()
    checks = get_checks(rdps)
    e = ContainsItemExactlyNTimesEvaluation([checks["string"]], "Abstract", 1)
    # one check
    assert e.evaluate(rdps[0]) == 1
    assert e.evaluate(rdps[1]) == 0
    assert e.evaluate(rdps[2]) == 1
    # multiple checks
    e = ContainsItemExactlyNTimesEvaluation(checks.values(), "Abstract", 1)
    assert e.evaluate(rdps[0]) == round(1/5, 10)
    assert e.evaluate(rdps[1]) == 0
    assert e.evaluate(rdps[2]) == round(1/5, 10)

@mock.patch('requests.get', side_effect=mocked_requests_get)
@mock.patch('requests.head', side_effect=mocked_requests_head)
def test_in_list_evaluation(mock_get, mock_head):
    rdps = get_rdps()
    checks = get_checks(rdps)
    with pytest.raises(ValueError):
        e = InListEvaluation([checks["string"]], "Abstract")
        assert str(e) == "comparata is not a list but a str"

    e = InListEvaluation([checks["string"]], ["Abstract", "TechnicalInfo"])
    # one check
    assert e.evaluate(rdps[0]) == 1
    assert e.evaluate(rdps[1]) == 0
    assert e.evaluate(rdps[2]) == 0.5
    # multiple checks
    e = InListEvaluation(checks.values(), ["Abstract", "TechnicalInfo"])
    assert e.evaluate(rdps[0]) == round(1/5, 10)
    assert e.evaluate(rdps[1]) == 0
    assert e.evaluate(rdps[2]) == round(1/10, 10)

@mock.patch('requests.get', side_effect=mocked_requests_get)
@mock.patch('requests.head', side_effect=mocked_requests_head)
def test_function_evaluation(mock_get, mock_head):
    rdps = get_rdps()
    checks = get_checks(rdps)
    def test_function(checks, pid):
        evaluation = 0
        r1 = checks[0].get_last_result(pid).outcome
        r2 = checks[1].get_last_result(pid).outcome
        for idx, r in enumerate(r1):
            if len(r) <= r2[idx]:
                evaluation += 1/len(r1)
        return evaluation
    e = FunctionEvaluation([checks["string"], checks["lom"]], test_function)
    assert e.description.endswith("The function's name is 'test_function'.")
    # one check
    assert e.evaluate(rdps[0]) == 0.5
    assert e.evaluate(rdps[1]) == 0
    assert e.evaluate(rdps[2]) == 1
