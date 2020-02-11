################################################################################
# Copyright: Tobias Weber 2020
#
# Apache 2.0 License
#
# This file contains all Evaluation-related tests
#
################################################################################
from breadp.evaluations import BatchEvaluation, SimpleAndEvaluation, Evaluation
from breadp.rdp.metadata import DataCiteMetadata
from breadp.checks.metadata import DescriptionsNumberCheck, \
    MainDescriptionLengthCheck, \
    MainDescriptionLanguageCheck, \
    DataCiteDescriptionsTypeCheck

class DescriptionEvaluation(BatchEvaluation):
    """ Evaluation for descriptions of the metadata of an RDP
    """

    def __init__(self):
        Evaluation.__init__(self)
        self.version = "0.0.1"
        self.id = 1

        self.checks["DescriptionsNumber"] = DescriptionsNumberCheck()
        self.checks["MainDescriptionLength"] = MainDescriptionLengthCheck()
        self.checks["MainDescriptionLanguage"] = MainDescriptionLanguageCheck()
        self.mandatory_checks = ("DescriptionsNumber",
                                 "MainDescriptionLength",
                                 "MainDescriptionLanguage")
        self.mandatory_check_weight = 4

    def _do_evaluate(self, rdp):
        if type(rdp.metadata) == DataCiteMetadata:
            c = DataCiteDescriptionsTypeCheck()
            c.check(rdp)
            self.checks["DataCiteDescriptionType"] = c

        weight_parts = len(self.checks) - len(self.mandatory_checks)  + \
            len(self.mandatory_checks) * self.mandatory_check_weight
        print(weight_parts)
        evaluation_score_part = 1 / weight_parts
        evaluation = 0

        if self.checks["DescriptionsNumber"].result.outcome > 0:
            evaluation += evaluation_score_part * self.mandatory_check_weight
        if self.checks["MainDescriptionLength"].result.outcome < 300:
            evaluation += evaluation_score_part * self.mandatory_check_weight
        if self.checks["MainDescriptionLanguage"].result.outcome == "en":
            evaluation += evaluation_score_part * self.mandatory_check_weight

        if type(rdp.metadata) == DataCiteMetadata:
            add = evaluation_score_part
            for dt in self.checks["DataCiteDescriptionType"].result.outcome:
                if dt not in ("Abstract", "Methods", "TechnicalInfo"):
                    add = 0
            evaluation += add

        return evaluation

