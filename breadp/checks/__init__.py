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
        (success, result) = (self._do_check(rdp))
        end = datetime.utcnow().isoformat()
        msg = result.msg
        self.log.add(
            CheckLogEntry(
                start,
                end,
                self.version,
                rdp.pid,
                result.msg,
                success,
                result
            )
        )

    def get_last_result(self, pid):
        """ Returns the last result of the check for the given pid.
            Returns None if no check did run yet.
        """
        try:
            return self.log.get_by_pid(pid)[-1].result
        except IndexError:
            return None

    def report(self, pid):
        report = {
            "name": type(self).__name__,
            "version": self.version,
            "desc": self.desc,
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
