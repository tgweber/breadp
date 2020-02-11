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

    def __init__(self, context):
        self.context = context

class BooleanResult(CheckResult):
    """ A result with a boolean outcome

    Attributes
    ----------
    outcome: bool
        Indicates whether the rdp fulfills the criterion checked
    """

    def __init__(self, outcome: bool, context: str):
        super(BooleanResult, self).__init__(context)
        self.outcome = outcome

class MetricResult(CheckResult):
    """ A result with a metric outcome

    Attributes
    ----------
    outcome: float
        The number the check resulted in (can be a float("nan")).
    """
    def __init__(self, outcome: float, context: str):
        super(MetricResult, self).__init__(context)
        self.outcome = outcome

class CategoricalResult(CheckResult):
    """ A result with a categorical outcome

    Attributes
    ----------
    outcome: str
        The categorical value the check resulted in.
    """
    def __init__(self, outcome: str, context: str):
        super(CategoricalResult, self).__init__(context)
        self.outcome = outcome

class ListResult(CheckResult):
    """ A result with a list as an outcome

    Attributes
    ----------
    outcome: list
        The list the check resuled in.
    """
    def __init__(self, outcome: list, context: str):
        super(ListResult, self).__init__(context)
        self.outcome = outcome
