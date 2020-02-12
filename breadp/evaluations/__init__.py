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
                print(check.result.context)
                return 0
        return 1

class MandatoryRecommendedEvaluation(Evaluation):
    def __init__(self, mandatory_check_weight = 2):
        Evaluation.__init__(self)
        self.mandatory_checks = []
        self.mandatory_check_weight = mandatory_check_weight
        self.evaluation_score_part = 1

    def _calculate_evaluation_weights(self, additional_score_parts=0):
        """ This function sets self.evaluation_score_part, i.e.
        the weight a part of the evaluation has (typically identical
        with test of one non-mandatory check). Mandatory checks get an
        additional weight of mandatory_check_weight times higher than
        the evaluation_score_part (defaults to 2).

        Arguments
        ---------
        additional_score_parts: int
            Determines the number of non-mandatory checks which have one
            additional evaluation_score_part (i.e. the check's result is used
            twice). Each additional usage increases this value.
        """
        evaluation_part_with_single_weight = len(self.checks) \
                + additional_score_parts \
                - len(self.mandatory_checks)
        total_evaluation_parts = evaluation_part_with_single_weight \
               + len(self.mandatory_checks) * self.mandatory_check_weight

        self.evaluation_score_part = 1 / total_evaluation_parts

    def _add_mandatory_check(self, check):
        self.checks[type(check).__name__] = check
        self.mandatory_checks.append(type(check).__name__)
