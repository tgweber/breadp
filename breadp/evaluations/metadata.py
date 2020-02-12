################################################################################
# Copyright: Tobias Weber 2020
#
# Apache 2.0 License
#
# This file contains all Evaluation-related tests
#
################################################################################
from breadp.evaluations import BatchEvaluation, \
        Evaluation, \
        MandatoryRecommendedEvaluation, \
        SimpleAndEvaluation
from breadp.rdp.metadata.datacite import DataCiteMetadata
from breadp.checks.metadata import     DataCiteDescriptionsTypeCheck, \
    DescriptionsLengthCheck, \
    DescriptionsLanguageCheck, \
    DescriptionsNumberCheck

class DescriptionEvaluation(BatchEvaluation, CompositeEvaluation):
    """ Evaluation for descriptions of the metadata of an RDP
    """
    def __init__(self, mandatory_check_weight):
        MandatoryRecommendedEvaluation.__init__(self, mandatory_check_weight)
        self.version = "0.0.1"
        self.id = 1
        self._add_evaluation_part(
            IsBetweenEvaluationPart(
                DescriptionsNumberCheck(),
                1.0,
                15.0,
                4)
        )
        self._add_evaluation_part(
            IsBetweenEvaluationPart(
                DescriptionsLengthCheck(),
                0.0,
                300.0,
                4)
        )
        self._add_evaluation_part(
            IsOrContainsEvaluationPart(
                DescriptionsLanguageCheck(),
                "en",
                4)
        )

    def _do_evaluate(self, rdp):
        if type(rdp.metadata) == DataCiteMetadata:
            self._add_evaluation_part(
                IsOrContainsEvaluationPart(
                    DataCiteDescriptionsTypeCheck(),
                    "Abstract",
                    1)
            )
            self._add_evaluation_part(
                IsNotOrDoesNotContainsEvaluationPart(
                    DataCiteDescriptionsTypeCheck(),
                    "Abstract",
                    1)
            )
        CompositeEvaluation._do_evaluate(self, rdp)


            for dt in self.checks["DataCiteDescriptionTypeCheck"].result.outcome:
                if dt not in ("Abstract", "Methods", "TechnicalInfo"):
                    add = 0
            evaluation += add
            if "Abstract" in self.checks["DataCiteDescriptionTypeCheck"].result.outcome:
                evaluation += self.evaluation_score_part

        return round(evaluation,10)

class TitleEvaluation(BatchEvaluation, MandatoryRecommendedEvaluation):
    """ Evaluation for the titles of the metadata of an RDP
    """
    def __init__(self, mandatory_check_weight):
        MandatoryRecommendedEvaluation.__init__(self, mandatory_check_weight)
        self.version = "0.0.1"
        self.id = 2
        self._add_mandatory_check(TitlesLanguageCheck())
        self._add_mandatory_check(TitlesJustAFileNameCheck())

    def _do_evaluate(self, rdp):
        evaluation = 0
        self._calculate_evaluation_weights()




        partial_factor_descriptionsLengthCheck = 0
