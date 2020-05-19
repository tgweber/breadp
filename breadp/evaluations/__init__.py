################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains code related to evaluation objects
#
################################################################################

from collections import Counter
from datetime import datetime
import hashlib
import inspect
from pprint import pformat
import uuid

from breadp import ChecksNotRunException
from breadp.checks.result import BooleanResult, ListResult, MetricResult

class Evaluation(object):
    """ Base class and interface for Evaluation of checks of
        RDPs

    Attributes
    ----------
    id: int
        Identifier for the evaluation
    version: str
        Version of the evaluation
    descrption: str
        A short text describing the criterion evaluated (in English)
    checks: list
        A list of checks

    Methods
    -------
    evaluate(self, pid) -> None
        Runs the evaluation
    """

    def __init__(self, checks):
        self.checks = checks
        self.rounded = 10
        self.id = str(uuid.uuid4())
        self.version = "Blank evaluations have no version"

    @property
    def description(self):
        return ' '.join(inspect.getdoc(self).split("\n\n")[0].split())

    @property
    def name(self):
        return type(self).__name__

    def evaluate(self, pid):
        """ Wrapper code around each evaluation
        Sets start and end time, handles state, and exceptions.

        Parameters
        ----------
        pid: pid
            PID of the Research Data Product to be evaluated
        """
        if len(self.checks) == 0:
            raise ValueError("No checks in {}".format(type(self).__name__))
        for c in self.checks:
            if c.get_last_result(pid) == None:
                raise ChecksNotRunException(
                    "{} has no result for {}".format(
                        type(c).__name__,
                        pid
                    )
                )
            if not c.log.get_by_pid(pid)[-1].result.success:
                return 0
        return round(self._evaluate(pid)/len(self.checks), self.rounded)

    def _evaluate(self, pid):
        raise NotImplementedError("must be implemented by subclasses of Evaluation")

class IsBetweenEvaluation(Evaluation):
    """ Each check's result's item between the (included) bounds adds
        (1/#items)*1/#checks to the score.

        Note: Adds 0 if the check's result is not of type MetricResult, or not of type
        ListResult or the list is empty.

    Attributes
    ----------
    low: float
        Lower bound of the comparison (the lower bound is included in the comparison)
    high: float
        Higher bound of the comparison (the higher bound is included in the comparison)
    """
    def __init__(self, checks, low, high):
        Evaluation.__init__(self, checks)
        self.low = low
        self.high = high
        self.version = "0.0.1"

    @property
    def description(self):
        description = ' '.join(inspect.getdoc(self).split("\n\n")[0].split())
        description += " The lower bound is {} the upper bound is {}.".format(self.low,
                                                                      self.high)
        return description

    def _evaluate(self, pid):
        evaluation = 0
        for c in self.checks:
            result = c.get_last_result(pid)
            if isinstance(result, MetricResult):
                if self.low <= result.outcome <= self.high:
                    evaluation += 1
            if isinstance(result, ListResult):
                if len(result.outcome) == 0:
                    continue
                for i in result.outcome:
                    try:
                        if self.low <= i <= self.high:
                            evaluation += 1/len(result.outcome)
                    except TypeError:
                        pass
        return evaluation

class IsIdenticalToEvaluation(Evaluation):
    """ Each check's result identical to the comparatum adds 1/#checks to the score.

        Note: if the comparatum and the result are lists, their order is NOT evaluated.

    comparatum: div
        object to compare to
    """
    def __init__(self, checks, comparatum):
        Evaluation.__init__(self, checks)
        self.comparatum = comparatum
        self.version = "0.0.1"

    @property
    def description(self):
        description = ' '.join(inspect.getdoc(self).split("\n\n")[0].split())
        description += " The comparatum is {}.".format(pformat(self.comparatum))
        return description

    def _evaluate(self, pid):
        evaluation = 0
        for c in self.checks:
            result = c.get_last_result(pid)
            if isinstance(result, ListResult) and isinstance(self.comparatum, list):
                if Counter(result.outcome) == Counter(self.comparatum):
                    evaluation += 1
            elif self.comparatum == result.outcome:
                evaluation += 1
        return evaluation


class ContainsAllEvaluation(Evaluation):
    """ Each check's result containing all items adds 1/#checks to the score.

        Note: Adds 0 when the check's result is not of type ListResult.

    items: div
        object to look for in ListResult
    """
    def __init__(self, checks, items):
        Evaluation.__init__(self, checks)
        self.items = items
        self.version = "0.0.1"

    @property
    def description(self):
        description = ' '.join(inspect.getdoc(self).split("\n\n")[0].split())
        description += " The items are {}.".format(pformat(self.items))
        return description

    def _evaluate(self, pid):
        evaluation = 0
        for c in self.checks:
            result = c.get_last_result(pid)
            if isinstance(result, ListResult) and set(self.items) <= set(result.outcome):
                evaluation += 1
        return evaluation

class ContainsAtLeastOneEvaluation(Evaluation):
    """ Each check's result containing at least one of the items adds 1/#checks to the score.

        Note: Adds 0 when the check's result is not of type ListResult.

    items: div
        object to look for in ListResult
    """
    def __init__(self, checks, items):
        Evaluation.__init__(self, checks)
        self.items = items
        self.version = "0.0.1"

    @property
    def description(self):
        description = ' '.join(inspect.getdoc(self).split("\n\n")[0].split())
        description += " The items are {}.".format(pformat(self.items))
        return description

    def _evaluate(self, pid):
        evaluation = 0
        for c in self.checks:
            result = c.get_last_result(pid)
            if isinstance(result, ListResult):
                for i in self.items:
                    if i in result.outcome:
                        evaluation += 1
                        # only count once per check!
                        break
        return evaluation

class DoesNotContainEvaluation(Evaluation):
    """ Each check's result NOT containing one of the items adds 1/#checks to the score.

        Note: Adds 0 when the check's result is not of type ListResult.

    items: div
        object to look for in ListResult
    """
    def __init__(self, checks, items):
        Evaluation.__init__(self, checks)
        self.items = items
        self.version = "0.0.1"

    @property
    def description(self):
        description = ' '.join(inspect.getdoc(self).split("\n\n")[0].split())
        description += " The items are {}.".format(pformat(self.items))
        return description

    def _evaluate(self, pid):
        evaluation = 0
        for c in self.checks:
            result = c.get_last_result(pid)
            if isinstance(result, ListResult) and len(result.outcome) > 0:
                add = True
                for i in self.items:
                    if i in result.outcome:
                        add = False
                if add:
                    evaluation += 1
        return evaluation

class TrueEvaluation(Evaluation):
    """ Each check's result with only True values adds 1/#checks to the score.

        Note: Adds 0 when the check's result is not of type ListResult (or empty)
        or not of BooleanResult.
    """
    def __init__(self, checks):
        Evaluation.__init__(self, checks)
        self.version = "0.0.1"

    def _evaluate(self, pid):
        evaluation = 0
        for c in self.checks:
            result = c.get_last_result(pid)
            if isinstance(result, BooleanResult):
                if result.outcome:
                    evaluation += 1
                    continue
            if isinstance(result, ListResult) and len(result.outcome) > 0:
                for r in result.outcome:
                    if not r:
                        break
                evaluation += 1
        return evaluation

class FalseEvaluation(Evaluation):
    """ Each check's result with only False values adds 1/#checks to the score.

        Note: Adds 0 when the check's result is not of type ListResult (or empty)
        or not of BooleanResult.
    """
    def __init__(self, checks):
        Evaluation.__init__(self, checks)
        self.version = "0.0.1"

    def _evaluate(self, pid):
        evaluation = 0
        for c in self.checks:
            result = c.get_last_result(pid)
            if isinstance(result, BooleanResult):
                if not result.outcome:
                    evaluation += 1
                    continue
            if isinstance(result, ListResult) and len(result.outcome) > 0:
                for r in result.outcome:
                    if r:
                        break
                evaluation += 1
        return evaluation

class TheMoreTrueTheBetterEvaluation(Evaluation):
    """ Each check's result adds (#True/len(result))*1/#checks to the score.

        Note: Adds 0 when the check's result is not of type ListResult (or empty)
    """
    def __init__(self, checks):
        Evaluation.__init__(self, checks)
        self.version = "0.0.1"

    def _evaluate(self, pid):
        evaluation = 0
        for c in self.checks:
            result = c.get_last_result(pid)
            if isinstance(result, ListResult) and len(result.outcome) > 0:
                for item in result.outcome:
                    if isinstance(item, bool) and item:
                        evaluation += 1/len(result.outcome)
        return evaluation

class TheMoreFalseTheBetterEvaluation(Evaluation):
    """ Each check's result adds (#False/len(result))*1/#checks to the score.

        Note: Adds 0 when the check's result is not of type ListResult (or empty)
    """
    def __init__(self, checks):
        Evaluation.__init__(self, checks)
        self.version = "0.0.1"

    def _evaluate(self, pid):
        evaluation = 0
        for c in self.checks:
            result = c.get_last_result(pid)
            if isinstance(result, ListResult) and len(result.outcome) > 0:
                for item in result.outcome:
                    if isinstance(item, bool) and not item:
                        evaluation += 1/len(result.outcome)
        return evaluation

class ContainsItemExactlyNTimesEvaluation(Evaluation):
    """ Each check's result in which the item occurrs exactly n times
        adds 1/#checks to the score.

        Note: Adds 0 when the check's result is not of type ListResult (or empty).
    """
    def __init__(self, checks, item, n):
        Evaluation.__init__(self, checks)
        self.item = item
        self.n = n
        self.version = "0.0.1"

    def _evaluate(self, pid):
        evaluation = 0
        for c in self.checks:
            result = c.get_last_result(pid)
            if isinstance(result, ListResult) and len(result.outcome) > 0:
                if self.n == result.outcome.count(self.item):
                    evaluation += 1
        return evaluation

class InListEvaluation(Evaluation):
    """ Each check's result's item in comparata adds (1/len(result))*1/#checks to the score.

        Note: Adds 0 when the check's result is not of type ListResult (or empty).
    """
    def __init__(self, checks, comparata):
        Evaluation.__init__(self, checks)
        if not isinstance(comparata, list):
            raise ValueError("comparata is not a list but a {}".format(type(comparata).__name__))
        self.comparata = comparata
        self.version = "0.0.1"

    def _evaluate(self, pid):
        evaluation = 0
        for c in self.checks:
            result = c.get_last_result(pid)
            if isinstance(result, ListResult) and len(result.outcome) > 0:
                for item in result.outcome:
                    if item in self.comparata:
                        evaluation += 1/len(result.outcome)
        return evaluation

class FunctionEvaluation(Evaluation):
    """ The given function determines the score.

        Note: This Evaluation allows to evaluate the relation of results of different checks.
              There is no need to normalize the output of the function against the number
              of checks involved (the return value of the function will be the result of the
              evaluation).
    """
    def __init__(self, checks, callback):
        Evaluation.__init__(self, checks)
        self.callback = callback
        self.version = "0.0.1"

    @property
    def description(self):
        description = ' '.join(inspect.getdoc(self).split("\n\n")[0].split())
        description += " The function's name is '{}'.\n\n".format(self.callback.__name__)
        description += " The function's code is '{}'.".format(inspect.getsource(self.callback))
        return description

    @property
    def name(self):
        return "{}-{}".format(type(self).__name__, self.callback.__name__)

    def _evaluate(self, pid):
        return self.callback(self.checks, pid) * len(self.checks)
