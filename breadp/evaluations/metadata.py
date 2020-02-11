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
from breadp.rdp.metadata import DataCiteMetadata
from breadp.checks.metadata import DescriptionsNumberCheck, \
    MainDescriptionLengthCheck, \
    MainDescriptionLanguageCheck, \
    DataCiteDescriptionsTypeCheck

class DescriptionEvaluation(BatchEvaluation, MandatoryRecommendedEvaluation):
    """ Evaluation for descriptions of the metadata of an RDP
    """

    def __init__(self, mandatory_check_weight):
        MandatoryRecommendedEvaluation.__init__(self, mandatory_check_weight)
        self.version = "0.0.1"
        self.id = 1

        self._add_mandatory_check(DescriptionsNumberCheck())
        self._add_mandatory_check(MainDescriptionLengthCheck())
        self._add_mandatory_check(MainDescriptionLanguageCheck())

    def _do_evaluate(self, rdp):
        evaluation = 0

        if type(rdp.metadata) == DataCiteMetadata:
            c = DataCiteDescriptionsTypeCheck()
            c.check(rdp)
            self.checks["DataCiteDescriptionTypeCheck"] = c

        self._calculate_evaluation_weights()

        if self.checks["DescriptionsNumberCheck"].result.outcome > 0:
            evaluation += self.evaluation_score_part * self.mandatory_check_weight
        if self.checks["MainDescriptionLengthCheck"].result.outcome < 300:
            evaluation += self.evaluation_score_part * self.mandatory_check_weight
        if self.checks["MainDescriptionLanguageCheck"].result.outcome == "en":
            evaluation += self.evaluation_score_part * self.mandatory_check_weight

        if type(rdp.metadata) == DataCiteMetadata:
            add = self.evaluation_score_part
            for dt in self.checks["DataCiteDescriptionTypeCheck"].result.outcome:
                if dt not in ("Abstract", "Methods", "TechnicalInfo"):
                    add = 0
            evaluation += add

        return evaluation
