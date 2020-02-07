################################################################################
# Copyright: Tobias Weber 2020
#
# Apache 2.0 License
#
# This file contains all code related to check objects
#
################################################################################

class CheckResult(object):
    """ Base class and interface for results of checks for RDPs

    Attributes
    ----------
    context: str
        Message giving more context to the outcome of the check.
    """

    def __init__(self):
        self.context = "No context provided"

class BooleanResult(CheckResult):
    """ A result with a boolean outcome

    Attributes
    ----------
    outcome: bool
        Indicates whether the rdp fulfills the criterion checked
    """

    def __init__(self, outcome: bool, msg: str):
        super(BooleanResult, self).__init__()
        self.outcome = outcome
        self.context = msg
