################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains code related to evaluation objects
#
################################################################################

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
        self.checks = []
        self.evaluations = []

    def evaluate(self, rdp):
        """ Wrapper code around each evaluation
        Sets start and end time, handles state, and exceptions.

        Parameters
        ----------
        rdp: Rdp
            Research Data Product to be evaluated
        """
        start = datetime.utcnow().isoformat()
        msg = self._run_checks(rdp)
        end = datetime.utcnow().isoformat()
        self.log.add(EvaluationLogEntry(
            start,
            end,
            self.version,
            rdp.pid,
            msg,
            self._do_evaluate(rdp))
        )


    def _run_checks(self, rdp):
        raise NotImplementedError("_run_checks must be implemented by subclasses of Evaluation")

    def _do_evaluate(self, rdp):
        raise NotImplementedError("_do_evaluate must be implemented by subclasses of Evaluation")

class BatchEvaluation(Evaluation):
    def _run_checks(self, rdp):
        import pprint
        for c in self.checks:
            c.check(rdp)
        return "Success"

class SimpleAndEvaluation(Evaluation):
    def _do_evaluate(self, rdp):
        for c in self.checks:
            if not isinstance(c.result, BooleanResult):
                return 0
            if not c.result.outcome:
                print(c.result.context)
                return 0
        return 1

class SimpleOrEvaluation(Evaluation):
    def _do_evaluate(self, rdp):
        for c in self.checks:
            if not isinstance(c.result, BooleanResult):
                return 0
            if c.result.outcome:
                return 1
        return 0
