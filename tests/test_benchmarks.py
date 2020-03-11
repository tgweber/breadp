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
from util import mocked_requests_get, mocked_requests_head

def test_blank_benchmark():
    def skip_function(evaluation, rdp):
        return False
    b = Benchmark(skip_function)
    b.add_evaluation(CreatorEvaluation(), 1)
    b.add_evaluation(CreatorEvaluation(), 1)
    assert len(b.evaluations) == 1
    b.add_evaluation(ContributorEvaluation(), 1)
    assert len(b.evaluations) == 2
    weights = b._calculate_weights(Rdp("123"))
    for w_key, w in weights.items():
        assert w == 1/len(b.evaluations)
    with pytest.raises(AttributeError) as ae:
        b.run(Rdp("123"))

