################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains code related to evaluation objects
#
################################################################################

from collections import OrderedDict
from datetime import datetime

from breadp.util.log import Log, EvaluationLogEntry
from breadp.checks.result import BooleanResult

class Evaluation(object):
    """ Base class and interface to evaluate RDPs

    Attributes
    ----------
    id: int
        Identifier for the evaluateion
    version: str
        Version of the evaluations
    desc: str
        A short text describing the criterion evaluated (in English)
    checks: list
        A list of checks
    log: list
        List of log entries of run evaluations
        (includes keys "start", "end", "evaluation", "version", "pid", "msg")

    Methods
    -------
    evaluate(self, rdp) -> None
        Runs the evaluation and updates log and state
    """

    def __init__(self):
        self.log = Log()
        self.checks = OrderedDict()

    def evaluate(self, rdp):
        """ Wrapper code around each evaluation
        Sets start and end time, handles state, and exceptions.

        Parameters
        ----------
        rdp: Rdp
            Research Data Product to be evaluated
        """
        start = datetime.utcnow().isoformat()
        (msg, success) = self._run_checks(rdp)
        end = datetime.utcnow().isoformat()
        self.log.add(EvaluationLogEntry(
            start,
            end,
            self.version,
            rdp.pid,
            msg,
            success,
            self._do_evaluate(rdp))
        )

    def _run_checks(self, rdp):
        raise NotImplementedError("_run_checks must be implemented by subclasses of Evaluation")

    def _do_evaluate(self, rdp):
        raise NotImplementedError("_do_evaluate must be implemented by subclasses of Evaluation")

class BatchEvaluation(Evaluation):
    def _run_checks(self, rdp):
        success = True
        for checkName, check in self.checks.items():
            check.check(rdp)
            if not check.success:
                success = False
        return ("", success)

class SimpleAndEvaluation(Evaluation):
    def _do_evaluate(self, rdp):
        for checkName, check in self.checks.items():
            if not isinstance(check.result, BooleanResult):
                return 0
            if not check.result.outcome:
                return 0
        return 1

class EvaluationPart(object):
    """ This class is the base interface for parts of evaluations

    Attributes
    ---------
    weight: int
        Indicates how this evaluation part should be weighted 1
        is the default and results in a weight 1/#EvaluationParts
    score: float
        Score of this part of the evaluation, value between 0 and 1
        Defaults to -1 before evaluate_part was called
    """
    def __init__(self, int: weight=1):
        self.weight = weight
        self.score = 0

    def evaluate_part(self):
        raise NotImplementedError("evaluate_part must be implemented by a subclass")

class SingleCheckEvaluationPart(EvaluationPart):
   """ This is an evaluation part which only consists of one check.

   Attributes
   ---------
   check: Check
        Check to be evaluated.
   """
   def __init__(self, Check: check, int: weight=1):
       EvaluationPart.__init__(self, weight)
       self.check = check

   def evaluate_part(self):
       if not self.check.success:
           return 0
       else:
           self._evaluate_part()

   def _evaluate_part(self):
       raise NotImplementedError("_evaluate_part must be implemented by a subclass")

class IsBetweenEvaluationPart(SingleCheckEvaluationPart):
    """ The more of the results are between the (included) bounds, the higher
        the score

    Attributes
    ----------
    low: float
        Lower bound of the comparison (the lower bound is included in the comparison)
    high: float
        Higher bound of the comparison (the higher bound is included in the comparison)
    """
    def __init__(self, Check: check, float: low, float: high, int: weight=1):
        SingleCheckEvaluationPart(self, check, weight)
        self.low = low
        self.high = high

    def _evaluate_part(self):
        if isinstance(self.check.result, MetricResult):
            if self.low <= self.check.result.outcome <= self.high:
                return 1
            else:
                return 0
        if isinstance(self.check.result, ListResult):
            w = 1/len(self.check.result.outcome)
            score = 0
            for r in self.check.result.outcome:
                if self.low <= r <= self.high:
                    score += w
            return score

class IsOrContainsEvaluationPart(SingleCheckEvaluationPart):
    """ evaluates to 1 if the given item is identical to the result of the checkor is
        contained in a ListResult, 0 otherwise.

    comparatum: div
        object to compare to
    """
    def __init__(self, Check: check, comparatum, int: weight=1):
        SingleCheckEvaluationPart(self, check, weight)
        self.comparatum = comparatum

    def _evaluate_part(self):
        if isinstance(self.check.result, ListResult):
            for r in self.check.result.outcome:
                if r == self.comparatum:
                    return 1
            return 0
        if self.comparatum == self.check.result.outcome:
            return 1
        return 0

class IsNotOrDoesNotContainEvaluationPart(SingleCheckEvaluationPart):
    """ evaluates to 0 if the given item is identical to the result of the check or is
        contained in a ListResult, 1 otherwise.
    """
    def __init__(self, Check: check, comparatum, int: weight=1):
        SingleCheckEvaluationPart(self, check, weight)
        self.complement = IsOrContainsEvaluationPart(check, comparatum, weight)

    def _evaluate_part(Self):
        return 1 - self.complement._evaluate_part()

class CompositeEvaluation(Evaluation, BatchEvaluation):
    """ Evaluation that is composed of EvaluationParts
    """
    def __init__(self):
        Evaluation.__init__(self)
        self.evaluation_parts = []
        self.total_weights = 0

    def add_evaluation_part(self, EvaluationPart: ep):
        # Checks are only added once, even if different evaluation parts
        # use the same check!
        self.checks[type(ep.check).__name__] = ep.check
        self.evaluation_parts.append(ep)
        self.total_weights += ep.weight

    def _do_evaluate(self, rdp):
        score = 0
        for ep in self.evaluation_parts:
            score += ep.evaluate_part() * (ep.weight/self.total_weights)
        return score
