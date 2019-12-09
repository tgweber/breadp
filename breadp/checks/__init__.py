################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains all code related to check objects
#
################################################################################

from datetime import datetime
import re

from breadp.util.exceptions import NotCheckeableError

class Check(object):
    """ Base class and interface for checks for RDPs

    Attributes
    ----------
    id: int
        Identifier for the check
    version: str
        Version of the check
    status: str
        Status of the last run check ("unchecked", "success", "uncheckable", "failure")
    log: list
        List of log entries of run checks
        (includes keys "start", "end", "status", "version", "pid", "msg")

    Methods
    -------
    check(self, rdp) -> None
        Runs the check and updates log and status
    """

    def __init__(self):
        self.status = "unchecked"
        self.log = []

    def check(self, rdp):
        """ Wrapper code around each check
        Sets start and end time, handles state, and exceptions.

        Parameters
        ----------
        rdp: Rdp
            Research Data Product to be checked
        """
        start = datetime.utcnow().isoformat()
        try:
            (self.status, msg) = (self._do_check(rdp))
        except NotCheckeableError as e:
            self.status = "uncheckable"
            msg = str(e)
        end = datetime.utcnow().isoformat()
        self.set_check(start, end, self.status, rdp.pid, msg)

    def set_check(self, start, end, status, pid, msg):
        """ Allows to set the results of a check (even from outside).
        Use this from outside the check object,
        if another check already failed on which this check is depending.
        If so, indicate the necessary parameters in msg.

        Parameters
        ----------
        start: str
            Start of check in ISO 8601 format and UTC time.
        end: str
            End of check in ISO 8601 format and UTC time.
        status: str
            One out of "success", "uncheckable", "failure"
        pid: str
            Identifier of the RDP to-be-checked
        msg: str
            Log message of the check
        """
        if status not in ("success", "uncheckable", "failure"):
            raise ValueError(
                "status must be 'success', 'uncheckable, or 'failure', given: {}".format(
                    status
                )
            )
        self.status = status
        self.log.append(
            {
                "start": start,
                "end": end,
                "status": status,
                "version": self.version,
                "pid": pid,
                "msg": msg
            }
        )


    def _do_check(self, rdp):
        raise NotImplementedError("_do_check must be implemented by subclasses of Check")

class IsValidDoiCheck(Check):
    """ Checks whether an RDP is a valid DOI
    """

    def __init__(self):
        super(IsValidDOICheck, self).__init__()
        self.id = 0
        self.version = "0.0.1"
        self.desc = "IsValidDoiCheck checks whether an RDP has a valid DOI as PID."
        self.description = self.desc

    def _do_check(self, rdp):
        if not rdp.pid:
            raise NotCheckeableError("RDP has no PID!")
        if re.match("^10\.\d{4}\d*/.*", rdp.pid):
            return ("success", "")
        return ("failure", "{} is not a valid DOI".format(rdp.pid))

class DoiResolvesCheck(Check):
    """ Checks whether the DOI of an RDP resolves
    """

    def __init__(self):
        super(IsValidDOICheck, self).__init__()
        self.id = 1
        self.version = "0.0.1"
        self.desc = "PidChecks checks whether an RDP has a valid DOI as PID."
        self.description = self.desc

    def _do_check(self, rdp):
        if not rdp.pid:
            raise NotCheckeableError("RDP has no PID!")
        if re.match("^10\.\d{4}\d*/.*", rdp.pid):
            return ("success", "")
        return ("failure", "{} is not a valid DOI".format(rdp.pid))
