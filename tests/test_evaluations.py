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

from breadp.checks import Check
from breadp.checks.metadata import \
    DescriptionsLengthCheck, \
    DescriptionsNumberCheck, \
    DescriptionsTypeCheck, \
    TitlesLanguageCheck, \
    TitlesTypeCheck
from breadp.evaluations import \
    AllFalseEvaluationPart, \
    AllTrueEvaluationPart, \
    BatchEvaluation, \
    CompositeEvaluation, \
    ContainsAllEvaluationPart, \
    ContainsAtLeastOneEvaluationPart, \
    ContainsItemExactlyNTimesEvaluationPart, \
    DoesNotContainEvaluationPart, \
    Evaluation, \
    EvaluationPart, \
    InListEvaluationPart, \
    IsBetweenEvaluationPart, \
    IsIdenticalToEvaluationPart, \
    MultipleCheckEvaluationPart, \
    SimpleAndEvaluation, \
    SingleCheckEvaluationPart, \
    TheMoreTrueTheBetterEvaluationPart
from breadp.evaluations.pid import DoiEvaluation
from breadp.evaluations.metadata import \
    CreatorEvaluation, \
    ContributorEvaluation, \
    ContributorRightsEvaluation, \
    DatesEvaluation, \
    DescriptionEvaluation, \
    FormatEvaluation, \
    LanguageEvaluation, \
    RelatedResourcesEvaluation, \
    RightsEvaluation, \
    SizeEvaluation, \
    SubjectEvaluation, \
    TitleEvaluation, \
    VersionEvaluation
from breadp.rdp import RdpFactory, Rdp
from util import base_evaluation_test, mocked_requests_get, mocked_requests_head

def test_blank_evaluation():
    e = Evaluation()
    with pytest.raises(NotImplementedError) as nie:
        e._run_checks(Rdp("123"))
        assert str(nie).startswith("_run_checks")
    with pytest.raises(NotImplementedError) as nie:
        e._do_evaluate(Rdp("123"))
        assert str(nie).startswith("_do_evaluate")

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_simpleAndEvaluation(mock_get):
    class TestEvaluation(BatchEvaluation, SimpleAndEvaluation):
        def __init__(self):
            Evaluation.__init__(self)
            self.checks["test"] = DescriptionsNumberCheck()
            self.version = "abc"
            self.id = "abc"
    e = TestEvaluation()
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    e.evaluate(rdp)
    assert e.log.log[-1].evaluation == 0

def test_blank_evaluationParts():
    ep = EvaluationPart()
    with pytest.raises(NotImplementedError) as nie:
        ep.evaluate_part()
        assert str(nie).startswith("evaluate_part()")
    with pytest.raises(NotImplementedError) as nie:
        ep.get_checks()
        assert str(nie).startswith("get_checks()")
    sep = SingleCheckEvaluationPart(Check())
    with pytest.raises(NotImplementedError) as nie:
        sep._evaluate_part()
        assert str(nie).startswith("_evaluate_part()")
    mep = MultipleCheckEvaluationPart([Check()])
    with pytest.raises(NotImplementedError) as nie:
        mep._evaluate_part()
        assert str(nie).startswith("_evaluate_part()")
    checks = mep.get_checks()
    assert checks[0] == Check.__name__


@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_evaluationParts(mock_get):
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    check = DescriptionsLengthCheck()
    check.check(rdp)
    assert ContainsItemExactlyNTimesEvaluationPart(check, 69, 1)._evaluate_part() == 1
    check = TitlesLanguageCheck()
    check.check(rdp)
    assert ContainsItemExactlyNTimesEvaluationPart(check, "en", 1)._evaluate_part() == 1
    assert ContainsAllEvaluationPart(check, ["en"])._evaluate_part() == 1
    check = TitlesTypeCheck()
    check.check(rdp)
    assert ContainsItemExactlyNTimesEvaluationPart(check, None, 1)._evaluate_part() == 1
    assert ContainsAllEvaluationPart(check, [None])._evaluate_part() == 1
    check = DescriptionsTypeCheck()
    check.check(rdp)
    assert ContainsAllEvaluationPart(check, ["Abstract"])._evaluate_part() == 1
    with pytest.raises(ValueError) as ve:
        InListEvaluationPart(check, 1)._evaluate_part()
        assert str(ve) == "int is not iterable"
    check = DescriptionsNumberCheck()
    check.check(rdp)
    assert IsBetweenEvaluationPart(check, 1.0, 100.0)._evaluate_part() == 1
    assert AllTrueEvaluationPart(check)._evaluate_part() == 0
    assert AllFalseEvaluationPart(check)._evaluate_part() == 0
    assert ContainsItemExactlyNTimesEvaluationPart(check, check, 1)._evaluate_part() == 0
    assert TheMoreTrueTheBetterEvaluationPart(check)._evaluate_part() == 0
    assert InListEvaluationPart(check, [])._evaluate_part() == 0
    assert ContainsAllEvaluationPart(check, [])._evaluate_part() == 0
    assert ContainsAtLeastOneEvaluationPart(check, [])._evaluate_part() == 0
    assert DoesNotContainEvaluationPart(check, [])._evaluate_part() == 0

    class TestEvaluation(CompositeEvaluation):
        def __init__(self):
            CompositeEvaluation.__init__(self)
            self.version = "a.b.c"
            self.id = 0
            self.add_evaluation_part(
                IsIdenticalToEvaluationPart(
                    DescriptionsLengthCheck(),
                    [69, 3]
                )
            )
    e = TestEvaluation()
    e.evaluate(rdp)
    assert e.log.log[-1].evaluation == 1
    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    e.evaluate(rdp)
    assert e.log.log[-1].evaluation == 0

# Tests the PID check
@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_pid_evaluation(mock_get):
    e = DoiEvaluation()
    assert base_evaluation_test(e, 0)
    assert e.desc == "Evaluation of an DOI as a PID of a RDP"
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 1
    assert e.log.log[-1].evaluation == 1

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    e.evaluate(rdp)
    assert e.log.log[-1].evaluation == 0

# Test the Description Evaluation
@mock.patch('requests.get', side_effect=mocked_requests_get)
@mock.patch('requests.head', side_effect=mocked_requests_head)
def test_description_evaluation(mock_get, mock_head):
    e = DescriptionEvaluation()
    assert base_evaluation_test(e, 1)

    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    report = e.report("10.5281/zenodo.3490396")
    assert report["name"] == "DescriptionEvaluation"
    assert report["version"] == e.version
    assert report["desc"] == e.desc
    assert len(report["evaluationParts"]) == 5
    assert report["evaluationParts"][0]["desc"] == e.evaluationParts[0].desc
    assert len(report["checks"]) == 4
    assert len(report["log"]) == 0

    e.evaluate(rdp)
    assert len(e.log) == 1
    assert e.log.log[-1].evaluation == 1

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 2
    assert e.log.log[-1].evaluation == 0


    report = e.report("10.5281/zenodo.3490396")
    assert report["name"] == "DescriptionEvaluation"
    assert report["version"] == e.version
    assert len(report["evaluationParts"]) == 5
    assert len(report["checks"]) == 4
    assert len(report["log"]) == 1
    assert report["log"][0]["evaluation"] == 1

    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 3
    assert e.log.log[-1].evaluation == round(31/42,10)

    rdp = RdpFactory.create("10.5281/zenodo.badex3", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 4
    assert e.log.log[-1].evaluation == round(12/14,10)

# Test the Title Evaluation
@mock.patch('requests.get', side_effect=mocked_requests_get)
@mock.patch('requests.head', side_effect=mocked_requests_head)
def test_title_evaluation(mock_get, mock_head):
    e = TitleEvaluation()
    assert base_evaluation_test(e, 2)

    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 1
    assert e.log.log[-1].evaluation == 1

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 2
    assert e.log.log[-1].evaluation == 0

    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 3
    assert e.log.log[-1].evaluation == round(1/3,10)

@mock.patch('requests.get', side_effect=mocked_requests_get)
@mock.patch('requests.head', side_effect=mocked_requests_head)
def test_format_evaluation(mock_get, mock_head):
    e = FormatEvaluation()
    assert base_evaluation_test(e, 3)

    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 1
    assert e.log.log[-1].evaluation == 1

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 2
    assert e.log.log[-1].evaluation == 0

    rdp = RdpFactory.create("10.5281/zenodo.badex4", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 3
    assert e.log.log[-1].evaluation == 0.5

    rdp = RdpFactory.create("10.5281/zenodo.badex5", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 4
    assert e.log.log[-1].evaluation == 0

@mock.patch('requests.get', side_effect=mocked_requests_get)
@mock.patch('requests.head', side_effect=mocked_requests_head)
def test_rights_evaluation(mock_get, mock_head):
    e = RightsEvaluation()
    assert base_evaluation_test(e, 4)

    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 1
    assert e.log.log[-1].evaluation == 1

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 2
    assert e.log.log[-1].evaluation == 0

    rdp = RdpFactory.create("10.5281/zenodo.badex5", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 3
    assert e.log.log[-1].evaluation == round(2/3,10)

@mock.patch('requests.get', side_effect=mocked_requests_get)
@mock.patch('requests.head', side_effect=mocked_requests_head)
def test_subject_evaluation(mock_get, mock_head):
    e = SubjectEvaluation()
    assert base_evaluation_test(e, 5)

    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 1
    assert e.log.log[-1].evaluation == 1

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 2
    assert e.log.log[-1].evaluation == 0

    rdp = RdpFactory.create("10.5281/zenodo.badex3", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 3
    assert e.log.log[-1].evaluation == round(2/6,10)

    rdp = RdpFactory.create("10.5281/zenodo.badex5", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 4
    assert e.log.log[-1].evaluation == round(1/6,10)

@mock.patch('requests.get', side_effect=mocked_requests_get)
@mock.patch('requests.head', side_effect=mocked_requests_head)
def test_creator_evaluation(mock_get, mock_head):
    e = CreatorEvaluation()
    assert base_evaluation_test(e, 6)

    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 1
    assert e.log.log[-1].evaluation == 1

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 2
    assert e.log.log[-1].evaluation == 0

    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 3
    assert e.log.log[-1].evaluation == round(3/24,10)

    rdp = RdpFactory.create("10.5281/zenodo.badex3", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 4
    assert e.log.log[-1].evaluation == 0

@mock.patch('requests.get', side_effect=mocked_requests_get)
@mock.patch('requests.head', side_effect=mocked_requests_head)
def test_size_evaluation(mock_get, mock_head):
    e = SizeEvaluation()
    assert base_evaluation_test(e, 7)

    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 1
    assert e.log.log[-1].evaluation == 1

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 2
    assert e.log.log[-1].evaluation == 0

    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 3
    assert e.log.log[-1].evaluation == round(1/2,10)

@mock.patch('requests.get', side_effect=mocked_requests_get)
@mock.patch('requests.head', side_effect=mocked_requests_head)
def test_language_evaluation(mock_get, mock_head):
    e = LanguageEvaluation()
    assert base_evaluation_test(e, 8)

    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 1
    assert e.log.log[-1].evaluation == 1

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 2
    assert e.log.log[-1].evaluation == 0

    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 3
    assert e.log.log[-1].evaluation == 0

@mock.patch('requests.get', side_effect=mocked_requests_get)
@mock.patch('requests.head', side_effect=mocked_requests_head)
def test_version_evaluation(mock_get, mock_head):
    e = VersionEvaluation()
    assert base_evaluation_test(e, 9)

    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 1
    assert e.log.log[-1].evaluation == 1

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 2
    assert e.log.log[-1].evaluation == 0

    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 3
    assert e.log.log[-1].evaluation == 0

@mock.patch('requests.get', side_effect=mocked_requests_get)
@mock.patch('requests.head', side_effect=mocked_requests_head)
def test_contributor_evaluation(mock_get, mock_head):
    e = ContributorEvaluation()
    assert base_evaluation_test(e, 10)

    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 1
    assert e.log.log[-1].evaluation == 1

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 2
    assert e.log.log[-1].evaluation == 0

    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 3
    assert e.log.log[-1].evaluation == round(12/15,10)

@mock.patch('requests.get', side_effect=mocked_requests_get)
@mock.patch('requests.head', side_effect=mocked_requests_head)
def test_contributor_rights_evaluation(mock_get, mock_head):
    e = ContributorRightsEvaluation()
    assert base_evaluation_test(e, 11)

    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 1
    assert e.log.log[-1].evaluation == 1

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 2
    assert e.log.log[-1].evaluation == 0

    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 3
    assert e.log.log[-1].evaluation == 0

    rdp = RdpFactory.create("10.5281/zenodo.badex3", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 4
    assert e.log.log[-1].evaluation == 1

@mock.patch('requests.get', side_effect=mocked_requests_get)
@mock.patch('requests.head', side_effect=mocked_requests_head)
def test_dates_evaluation(mock_get, mock_head):
    e = DatesEvaluation()
    assert base_evaluation_test(e, 12)

    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 1
    assert e.log.log[-1].evaluation == 1

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 2
    assert e.log.log[-1].evaluation == 0

    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 3
    assert e.log.log[-1].evaluation == round(1/3, 10)

    rdp = RdpFactory.create("10.5281/zenodo.badex3", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 4
    assert e.log.log[-1].evaluation == round(1/3, 10)

    rdp = RdpFactory.create("10.5281/zenodo.badex4", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 5
    assert e.log.log[-1].evaluation == 0

    rdp = RdpFactory.create("10.5281/zenodo.badex5", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 6
    assert e.log.log[-1].evaluation == round(1/3, 10)

@mock.patch('requests.get', side_effect=mocked_requests_get)
@mock.patch('requests.head', side_effect=mocked_requests_head)
def test_related_resources_evaluation(mock_get, mock_head):
    e = RelatedResourcesEvaluation()
    assert base_evaluation_test(e, 13)

    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 1
    assert e.log.log[-1].evaluation == 1

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 2
    assert e.log.log[-1].evaluation == 0

    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 3
    assert e.log.log[-1].evaluation == round(2/6, 10)
