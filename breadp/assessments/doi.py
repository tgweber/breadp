################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains all code related to DOI assessment objects
#
################################################################################

from breadp.assessments import BatchAssessment, SimpleAndAssessment, Assessment
from breadp.checks import IsValidDoiCheck, DoiResolvesCheck

class DoiAssessment(BatchAssessment, SimpleAndAssessment):

    def __init__(self):
        Assessment.__init__(self)
        self.checks.append(IsValidDoiCheck())
        self.checks.append(DoiResolvesCheck())
        self.version = "0.0.1"
        self.id = 0
