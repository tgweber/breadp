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
from breadp.checks.metadata import     DataCiteDescriptionsTypeCheck, \
    DescriptionsLengthCheck, \
    DescriptionsLanguageCheck, \
    DescriptionsNumberCheck

class DescriptionEvaluation(BatchEvaluation, MandatoryRecommendedEvaluation):
    """ Evaluation for descriptions of the metadata of an RDP
    """

    def __init__(self, mandatory_check_weight):
        MandatoryRecommendedEvaluation.__init__(self, mandatory_check_weight)
        self.version = "0.0.1"
        self.id = 1
        self._add_mandatory_check(DescriptionsNumberCheck())
        self._add_mandatory_check(DescriptionsLengthCheck())
        self._add_mandatory_check(DescriptionsLanguageCheck())

    def _do_evaluate(self, rdp):
        evaluation = 0

        if type(rdp.metadata) == DataCiteMetadata:
            c = DataCiteDescriptionsTypeCheck()
            c.check(rdp)
            self.checks["DataCiteDescriptionTypeCheck"] = c

        self._calculate_evaluation_weights(1)

        num_of_descriptions = self.checks["DescriptionsNumberCheck"].result.outcome
        if num_of_descriptions > 0:
            evaluation += self.evaluation_score_part * self.mandatory_check_weight
        else:
            return 0

        partial_factor_descriptionsLengthCheck = 0
        partial_factor_descriptionsLanguageCheck = 0
        for i in range(0, num_of_descriptions):
            if self.checks["DescriptionsLengthCheck"].result.outcome[i] < 300:
                partial_factor_descriptionsLengthCheck += 1 / num_of_descriptions
            if self.checks["DescriptionsLanguageCheck"].result.outcome[i] == "en":
                partial_factor_descriptionsLanguageCheck += 1 / num_of_descriptions

        evaluation += partial_factor_descriptionsLengthCheck \
                * self.evaluation_score_part \
                * self.mandatory_check_weight

        evaluation += partial_factor_descriptionsLanguageCheck \
                * self.evaluation_score_part \
                * self.mandatory_check_weight

        if type(rdp.metadata) == DataCiteMetadata:
            add = self.evaluation_score_part
            for dt in self.checks["DataCiteDescriptionTypeCheck"].result.outcome:
                if dt not in ("Abstract", "Methods", "TechnicalInfo"):
                    add = 0
            evaluation += add
            if "Abstract" in self.checks["DataCiteDescriptionTypeCheck"].result.outcome:
                evaluation += self.evaluation_score_part

        return round(evaluation,10)
