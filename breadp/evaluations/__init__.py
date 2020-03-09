################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains code related to evaluation objects
#
################################################################################

from collections import Counter, OrderedDict
from datetime import datetime

from breadp.util.log import Log, EvaluationLogEntry
from breadp.checks.result import BooleanResult, ListResult, MetricResult

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
    """ This evaluation aggregates several checks with a BooleanResult and
        Returns 1 if all are True, 0 otherwise
    """
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
    def __init__(self, weight=1):
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
   def __init__(self, check, weight=1):
       EvaluationPart.__init__(self, weight)
       self.check = check
   def evaluate_part(self):
       if not self.check.success:
           return 0
       else:
           return self._evaluate_part()

   def _evaluate_part(self):
       raise NotImplementedError("_evaluate_part must be implemented by a subclass")

class MultipleCheckEvaluationPart(EvaluationPart):
   """ This is an evaluation part which consists of sevaral checks
   Attribute
   ---------
   checks: list<Check>
       Checks to be evaluated
   """
   def __init__(self, checks, weight=1):
       EvaluationPart.__init__(self, weight)
       self.checks = checks

   def evaluate_part(self):
       for c in self.checks:
           if not c.success:
               return 0
       return self._evaluate_part()

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
    def __init__(self, check, low, high, weight=1):
        SingleCheckEvaluationPart.__init__(self, check, weight)
        self.low = low
        self.high = high

    def _evaluate_part(self):
        if isinstance(self.check.result, MetricResult):
            if self.low <= self.check.result.outcome <= self.high:
                return 1
            else:
                return 0
        if isinstance(self.check.result, ListResult):
            if len(self.check.result.outcome) == 0:
                return 0
            w = 1/len(self.check.result.outcome)
            score = 0
            for r in self.check.result.outcome:
                if self.low <= r <= self.high:
                    score += w
            return score

class IsIdenticalToEvaluationPart(SingleCheckEvaluationPart):
    """ evaluates to 1 if the given comparatum is identical to the result of the
        check, 0 otherwise

    comparatum: div
        object to compare to
    """
    def __init__(self, check, comparatum, weight=1):
        SingleCheckEvaluationPart.__init__(self, check, weight)
        self.comparatum = comparatum

    def _evaluate_part(self):
        if isinstance(self.check.result, ListResult) \
           and isinstance(self.comparatum, list):
            if Counter(self.check.result.outcome) == Counter(comparatum):
                return 1
            return 0
        if self.comparatum == self.check.result.outcome:
            return 1
        return 0

class ContainsAllEvaluationPart(SingleCheckEvaluationPart):
    """ The score is 1 if all items are contained in the ListResult.
        Is 0 when the result is not of type ListResult

    items: div
        object to look for in ListResult
    """
    def __init__(self, check, items, weight=1):
        SingleCheckEvaluationPart.__init__(self, check, weight)
        self.items = items

    def _evaluate_part(self):
        if not isinstance(self.check.result, ListResult):
            return 0
        for i in self.items:
            if i not in self.check.result.outcome:
                return 0
        return 1

class ContainsAtLeastOneEvaluationPart(SingleCheckEvaluationPart):
    """ The score is 1 if at least one of the items is contained in the ListResult.
        Is 0 when the result is not of type ListResult

    items: div
        object to look for in ListResult
    """
    def __init__(self, check, items, weight=1):
        SingleCheckEvaluationPart.__init__(self, check, weight)
        self.items = items

    def _evaluate_part(self):
        if not isinstance(self.check.result, ListResult):
            return 0
        for i in self.items:
            if i in self.check.result.outcome:
                return 1
        return 0

class DoesNotContainEvaluationPart(SingleCheckEvaluationPart):
    """ The score is 1 if all items are not contained in the ListResult.
        Is 0 when the result is not of type ListResult

    items: div
        object to look for in ListResult
    """
    def __init__(self, check, items, weight=1):
        SingleCheckEvaluationPart.__init__(self, check, weight)
        self.items = items

    def _evaluate_part(self):
        if not isinstance(self.check.result, ListResult):
            return 0
        if len(self.check.result.outcome) == 0:
            return 0
        for i in self.items:
            if i in self.check.result.outcome:
                return 0
        return 1

class AllTrueEvaluationPart(SingleCheckEvaluationPart):
    """ The score is 1 if all list items of ListResult are True.
        0 otherwise, or if the result is not of type ListResult.
    """
    def _evaluate_part(self):
        if not isinstance(self.check.result, ListResult):
            return 0
        if len(self.check.result.outcome) == 0:
            return 0

        for r in self.check.result.outcome:
            if not r:
               return 0
        return 1

class IsTrueEvaluationPart(SingleCheckEvaluationPart):
    """ If the check's outcome is true this part returns 1, else 0
    """
    def _evaluate_part(self):
        if self.check.result.outcome:
            return 1
        else:
            return 0

class IsFalseEvaluationPart(SingleCheckEvaluationPart):
    """ If the check's outcome is false this part returns 1, else 0
    """
    def _evaluate_part(self):
        if self.check.result.outcome:
            return 0
        else:
            return 1

class AllFalseEvaluationPart(SingleCheckEvaluationPart):
    """ The score is 1 if all list items of ListResult are False.
        0 otherwise, or if the result is not of type ListResult.
    """
    def __init__(self, check, weight=1):
        SingleCheckEvaluationPart.__init__(self, check, weight)
        self.reverse = AllTrueEvaluationPart(check, weight)

    def _evaluate_part(self):
        if not isinstance(self.check.result, ListResult):
            return 0
        if len(self.check.result.outcome) == 0:
            return 0
        for r in self.check.result.outcome:
            if r:
               return 0
        return 1

class ContainsItemExactlyNTimesEvaluationPart(SingleCheckEvaluationPart):
    """ The score is 1 if item is exactly n times in ListResult of check.
        0 otherwise, or if the result is not of type ListResult
    """
    def __init__(self, check, item, n, weight=1):
        SingleCheckEvaluationPart.__init__(self, check, weight)
        self.item = item
        self.n = n

    def _evaluate_part(self):
        if not isinstance(self.check.result, ListResult):
            return 0
        if self.n == self.check.result.outcome.count(self.item):
            return 1
        return 0

class TheMoreTrueTheBetterEvaluationPart(SingleCheckEvaluationPart):
    """ The score is the ratio of all items in the ListResult which are bools and True
        over all items in the list. 0 if the list is empty or not of type ListResult
    """
    def _evaluate_part(self):
        if not isinstance(self.check.result, ListResult):
            return 0
        if len(self.check.result.outcome) == 0:
            return 0
        trueAndBool = 0
        for item in self.check.result.outcome:
            if isinstance(item, bool) and item:
                trueAndBool += 1
        return trueAndBool/len(self.check.result.outcome)

class InListEvaluationPart(SingleCheckEvaluationPart):
    """ The score is the ratio of all items in the ListResult which are also member
        of the specified comparata list. 0 if the list is empty or not of type ListResult
    """
    def __init__(self, check, comparata, weight=1):
        SingleCheckEvaluationPart.__init__(self, check, weight)
        self.comparata = comparata

    def _evaluate_part(self):
        if not isinstance(self.check.result, ListResult):
            return 0
        if len(self.check.result.outcome) == 0:
            return 0
        inList = 0
        for item in self.check.result.outcome:
            if item in self.comparata:
                inList += 1
        return inList/len(self.check.result.outcome)

class FunctionEvaluationPart(MultipleCheckEvaluationPart):
    """ The evalution part is carried out by a function that takes checks
        and returns the value
    """
    def __init__(self, checks, callback, weight=1):
        MultipleCheckEvaluationPart.__init__(self, checks, weight)
        self.callback = callback

    def _evaluate_part(self):
        return self.callback(self.checks)

class CompositeEvaluation(BatchEvaluation):
    """ Evaluation that is composed of EvaluationParts
    """
    def __init__(self):
        Evaluation.__init__(self)
        self.evaluation_parts = []
        self.total_weights = 0

    def add_evaluation_part(self, ep):

        if isinstance(ep, SingleCheckEvaluationPart):
            checks = [ep.check]
        else:
            checks = ep.checks

        # There are problems when we add different checks of the same type!
        # initialize in Evaluation before calling add_evaluation_part
        for c in checks:
            self.checks[type(c).__name__] = c

        self.evaluation_parts.append(ep)
        self.total_weights += ep.weight

    def _do_evaluate(self, rdp):
        score = 0
        for ep in self.evaluation_parts:
            epep = ep.evaluate_part()
            score += epep * (ep.weight/self.total_weights)
            print("{}: {}".format(ep, epep))
        return round(score, 10)
