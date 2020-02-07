################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains code related to assessment objects
#
################################################################################

from datetime import datetime

from breadp.util.log import Log, AssessmentLogEntry

class Assessment(object):
    """ Base class and interface for assesss for RDPs

    Attributes
    ----------
    id: int
        Identifier for the assess
    version: str
        Version of the assess
    desc: str
        A short text describing the criterion assessed (in English)
    checks: list
        A list of checks
    log: list
        List of log entries of run assessments
        (includes keys "start", "end", "assessment", "version", "pid", "msg")

    Methods
    -------
    assess(self, rdp) -> None
        Runs the assess and updates log and state
    """

    def __init__(self):
        self.log = Log()
        self.checks = []
        self.assessments = []

    def assess(self, rdp):
        """ Wrapper code around each assess
        Sets start and end time, handles state, and exceptions.

        Parameters
        ----------
        rdp: Rdp
            Research Data Product to be assessed
        """
        start = datetime.utcnow().isoformat()
        msg = self._run_checks(rdp)
        end = datetime.utcnow().isoformat()
        self.log.add(AssessmentLogEntry(
            start,
            end,
            self.version,
            rdp.pid,
            msg,
            self._do_assess(rdp))
        )


    def _run_checks(self, rdp):
        raise NotImplementedError("_run_checks must be implemented by subclasses of Assessment")

    def _do_assess(self, rdp):
        raise NotImplementedError("_do_assess must be implemented by subclasses of Assessment")

class BatchAssessment(Assessment):
    def _run_checks(self, rdp):
        for c in self.checks:
            c.check(rdp)
        return "Success"

class SimpleAndAssessment(Assessment):
    def _do_assess(self, rdp):
        for c in self.checks:
            if not c.log.get_by_pid(rdp.pid)[-1].state == "success":
                return 0
        return 1

class SimpleOrAssessment(Assessment):
    def _do_assess(self, rdp):
        for c in self.checks:
            if c.log.get_by_pid(rdp.pid)[-1].state == "success":
                return 1
        return 0
