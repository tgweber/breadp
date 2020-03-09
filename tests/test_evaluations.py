################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains all Evaluation-related tests
#
################################################################################

from unittest import mock

from breadp.checks.metadata import \
    DataCiteDescriptionsTypeCheck, \
    DescriptionsLengthCheck, \
    DescriptionsNumberCheck, \
    TitlesLanguageCheck, \
    TitlesTypeCheck
from breadp.evaluations import \
    AllFalseEvaluationPart, \
    BatchEvaluation, \
    CompositeEvaluation, \
    ContainsAllEvaluationPart, \
    ContainsItemExactlyNTimesEvaluationPart, \
    DoesNotContainEvaluationPart, \
    Evaluation, \
    IsBetweenEvaluationPart, \
    SimpleAndEvaluation
from breadp.evaluations.doi import DoiEvaluation
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
from breadp.rdp.rdp import RdpFactory, Rdp
from util import mocked_requests_get, mocked_requests_head

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_evaluation_parts(mock_get):
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
    check = DataCiteDescriptionsTypeCheck()
    check.check(rdp)
    assert ContainsAllEvaluationPart(check, ["Abstract"])._evaluate_part() == 1
    check = DescriptionsNumberCheck()
    check.check(rdp)
    assert IsBetweenEvaluationPart(check, 1.0, 100.0)._evaluate_part() == 1

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
    e = DescriptionEvaluation()
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
#    for c in e.checks.values():
#        print("{}: {} - {}".format(c.success,c.result.outcome, c.log.log[-1].msg))
    assert len(e.log) == 3
    assert e.log.log[-1].evaluation == round(11/14,10)

# Test the Title Evaluation
@mock.patch('requests.get', side_effect=mocked_requests_get)
@mock.patch('requests.head', side_effect=mocked_requests_head)
def test_title_evaluation(mock_get, mock_head):
    e = TitleEvaluation()
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
def test_format_evaluation(mock_get, mock_head):
    e = RightsEvaluation()
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
    assert e.log.log[-1].evaluation == round(7/30,10)

    rdp = RdpFactory.create("10.5281/zenodo.badex3", "zenodo", token="123")
    e.evaluate(rdp)
    assert len(e.log) == 4
    assert e.log.log[-1].evaluation == round(2/6,10)

@mock.patch('requests.get', side_effect=mocked_requests_get)
@mock.patch('requests.head', side_effect=mocked_requests_head)
def test_creator_evaluation(mock_get, mock_head):
    e = CreatorEvaluation()
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
    assert e.log.log[-1].evaluation == round(2/3, 10)

@mock.patch('requests.get', side_effect=mocked_requests_get)
@mock.patch('requests.head', side_effect=mocked_requests_head)
def test_related_resources_evaluation(mock_get, mock_head):
    e = RelatedResourcesEvaluation()
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
