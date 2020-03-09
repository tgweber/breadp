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
import requests

from breadp.util.log import Log, CheckLogEntry
from breadp.checks.result import BooleanResult

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
    """

    def __init__(self):
        self.success = False
        self.result = None
        self.log = Log()

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

    def _do_check(self, rdp):
        raise NotImplementedError("_do_check must be implemented by subclasses of Check")

class IsValidDoiCheck(Check):
    """ Checks whether an RDP is a valid DOI

    Methods
    -------
    _do_check(self, rdp)
        returns a BooleanResult
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 0
        self.version = "0.0.1"
        self.desc = "checks whether an RDP has a valid DOI as PID"

    def _do_check(self, rdp):
        if not rdp.pid:
            msg = "RDP has no PID"
            return(False, BooleanResult(False, msg))
        if re.match("^10\.\d{4}\d*/.*", rdp.pid):
            return (True, BooleanResult(True, ""))
        msg = "{} is not a valid DOI".format(rdp.pid)
        return (True, BooleanResult(False, msg))

class DoiResolvesCheck(Check):
    """ Checks whether the DOI of an RDP resolves

    Methods
    -------
    _do_check(self, rdp)
        returns a BooleanResult
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 1
        self.version = "0.0.1"
        self.desc = "checks whether the DOI of an RDP resolves"

    def _do_check(self, rdp):
        if not rdp.pid:
            msg = "RDP has no PID"
            return(False, BooleanResult(False, msg))
        try:
            response = requests.head('https://doi.org/' + rdp.pid)
        except Exception as e:
            msg = "{}: {}".format(type(e), e)
            return(False, BooleanResult(False, msg))

        if response.status_code != 302:
            msg = "Could not resolve {}, status code: {}".format(
                rdp.pid, response.status_code)
            return (True, BooleanResult(False, msg))

        msg = "Location of resolved doi: {}".format(
            response.headers.get('Location'))
        return (True, BooleanResult(True, msg))
