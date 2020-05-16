################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains all code related to pid check objects
#
################################################################################

import re
import requests

from breadp.checks import Check
from breadp.checks.result import BooleanResult

class IsValidDoiCheck(Check):
    """ Checks whether an RDP has a valid DOI as PID

    Methods
    -------
    _do_check(self, rdp)
        returns a BooleanResult
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 0
        self.version = "0.0.1"

    def _do_check(self, rdp):
        if not rdp.pid:
            msg = "RDP has no PID"
            return BooleanResult(False, msg, False)
        if re.match(r"^10\.\d{4}\d*/.*", rdp.pid):
            return BooleanResult(True, "", True)
        msg = "{} is not a valid DOI".format(rdp.pid)
        return BooleanResult(False, msg, True)

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

    def _do_check(self, rdp):
        if not rdp.pid:
            msg = "RDP has no PID"
            return BooleanResult(False, msg, False)
        try:
            response = requests.head('https://doi.org/' + rdp.pid)
        except Exception as e:
            msg = "{}: {}".format(type(e).__name__, e)
            return BooleanResult(False, msg, False)

        if response.status_code != 302:
            msg = "Could not resolve {}, status code: {}".format(
                rdp.pid, response.status_code)
            return BooleanResult(False, msg, True)

        msg = "Location of resolved doi: {}".format(
            response.headers.get('Location'))
        return BooleanResult(True, msg, True)
