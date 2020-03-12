################################################################################
# Copyright: Tobias Weber 2019
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
from breadp.checks import Check
from breadp.checks.pid import IsValidDoiCheck as BooleanResultCheck
from breadp.checks.metadata import \
    DescriptionsNumberCheck as MetricResultCheck, \
    DescriptionsLengthCheck as ListOfMetricResultsCheck, \
    DescriptionsTypeCheck as ListOfStringResultsCheck, \
    TitlesJustAFileNameCheck as ListOfBooleanResultsCheck
from breadp.evaluations import \
    ContainsAllEvaluation, \
    ContainsAtLeastOneEvaluation, \
    ContainsItemExactlyNTimesEvaluation, \
    DoesNotContainEvaluation, \
    Evaluation, \
    FalseEvaluation, \
    InListEvaluation, \
    IsBetweenEvaluation, \
    IsIdenticalToEvaluation, \
    TheMoreTrueTheBetterEvaluation, \
    TrueEvaluation
from breadp.rdp import RdpFactory, Rdp
from util import base_evaluation_test, mocked_requests_get, mocked_requests_head


def test_blank_evaluation():
    e = Evaluation([MetricResultCheck()])
    with pytest.raises(NotImplementedError) as nie:
        e._evaluate(Rdp("123"))
        assert str(nie).startswith("must be implemented")

# Tests the PID check
@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_is_between_evaluation(mock_get):
    rdp1 = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    rdp2 = RdpFactory.create("10.123/zenodo.badex1", "zenodo", token="123")
    mrc  = MetricResultCheck()
    mrc.check(rdp1)
    mrc.check(rdp2)
    # test no run
    e = IsBetweenEvaluation([MetricResultCheck()], 1.0, 5.0)
    assert base_evaluation_test(e)
    with pytest.raises(ChecksNotRunException) as cnre:
        e.evaluate(rdp1)
        assert " has no result for " in str(cnre)
    e.checks = [mrc]
    assert e.evaluate(rdp1) == 1
    assert e.evaluate(rdp2) == 0
