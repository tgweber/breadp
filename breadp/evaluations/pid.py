################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains all code related to DOI evaluation objects
#
################################################################################

from breadp.evaluations import BatchEvaluation, SimpleAndEvaluation, Evaluation
from breadp.checks.pid import IsValidDoiCheck, DoiResolvesCheck

class DoiEvaluation(BatchEvaluation, SimpleAndEvaluation):
    """ Evaluation of an DOI as a PID of a RDP

    """
    def __init__(self):
        Evaluation.__init__(self)
        self.checks["IsValidDoi"] = IsValidDoiCheck()
        self.checks["DoiResolves"] = DoiResolvesCheck()
        self.version = "0.0.1"
        self.id = 0
