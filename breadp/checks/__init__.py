################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains all code related to check objects
#
################################################################################

import inspect
from datetime import datetime

from breadp.util.log import Log, CheckLogEntry

class Check(object):
    """ Base class and interface for checks for RDPs

    Attributes
    ----------
    id: int
        Identifier for the check
    version: str
        Version of the check
    desc: str
        A short text describing the criterion checked (in English)
    success: bool
        Success of the last run check (false on initialization)
    log: Log
        List of log entries of run checks
        (includes keys "start", "end", "state", "version", "pid", "msg")


    Methods
    -------
    check(self, rdp) -> None
        Runs the check and updates log and state
    report(self, pid) -> dict
        Returns a dicationary of checks run for the specified pid
    """

    def __init__(self):
        self.success = False
        self.result = None
        self.log = Log()

    @property
    def desc(self):
        return inspect.getdoc(self).split("\n\n")[0]

    def check(self, rdp):
        """ Wrapper code around each check
        Sets start and end time, handles, success, and exceptions.

        Parameters
        ----------
        rdp: Rdp
            Research Data Product to be checked
        """
        start = datetime.utcnow().isoformat()
        (self.success, self.result) = (self._do_check(rdp))
        msg = self.result.msg
        end = datetime.utcnow().isoformat()
        self.set_check(start, end, self.success, self.result, rdp.pid, msg)

    def set_check(self, start, end, success, result, pid, msg):
        """ Allows to set the results of a check (even from outside).
        Use this from outside the check object,
        if another check already failed on which this check is depending.
        If so, indicate the necessary parameters in msg.

        Parameters
        ----------
        start: str
            Start of check in ISO 8601 format and UTC time
        end: str
            End of check in ISO 8601 format and UTC time
        success: bool
            Indicates whether the check was successful or failed
        result: CheckResult
            A object indicating the resul of the check
        pid: str
            Identifier of the RDP to-be-checked
        msg: str
            Log message of the check
        """
        self.success = success
        self.result = result
        self.log.add(CheckLogEntry(start, end, self.version, pid, msg, success, result))

    def report(self, pid):
        report = {
            "name": type(self).__name__,
            "version": self.version,
            "id": self.id,
            "log": []
        }
        for entry in self.log.get_by_pid(pid):
            report["log"].append(
                {
                    "start": entry.start,
                    "success": entry.success,
                    "result": entry.result.outcome,
                    "msg": entry.msg,
                    "end": entry.end
                }
            )
        return report

    def _do_check(self, rdp):
        raise NotImplementedError("_do_check must be implemented by subclasses of Check")
