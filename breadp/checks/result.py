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
    msg: str
        Message giving more msg to the outcome of the check
    success: bool
        Flag indicating whether the check was successful
    """

    def __init__(self, msg, success):
        self.msg = msg
        self.success = success

class BooleanResult(CheckResult):
    """ A result with a boolean outcome

    Attributes
    ----------
    outcome: bool
        Indicates whether the rdp fulfills the criterion checked
    """

    def __init__(self, outcome: bool, msg: str, success: bool):
        CheckResult.__init__(self, msg, success)
        self.outcome = outcome

class MetricResult(CheckResult):
    """ A result with a metric outcome

    Attributes
    ----------
    outcome: float
        The number the check resulted in (can be a float("nan")).
    """
    def __init__(self, outcome: float, msg: str, success: bool):
        CheckResult.__init__(self, msg, success)
        self.outcome = outcome

class ListResult(CheckResult):
    """ A result with a list as an outcome

    Attributes
    ----------
    outcome: list
        The list the check resuled in.
    """
    def __init__(self, outcome: list, msg: str, success: bool):
        CheckResult.__init__(self, msg, success)
        self.outcome = outcome

class CardinalResult(CheckResult):
    """ A result with a controlled list of strings as possible outcomes

    Attributes
    ----------
    outcome: list
        The list the check resuled in.
    """
    def __init__(self, outcome: str, msg: str, success: bool):
        CheckResult.__init__(self, msg, success)
        self.outcome = outcome
