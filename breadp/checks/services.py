################################################################################
# Copyright: Tobias Weber 2020
#
# Apache 2.0 License
#
# This file contains all code related for metadata checks
#
################################################################################
from breadp.checks import Check
from breadp.checks.result import ListResult

class CapacitiesSupportedCheck(Check):
    """ Checks the capacities the service component of the RDP supports

    Methods
    -------
    _do_check(self, rdp)
        returns a Listresult
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 38
        self.version = "0.0.1"

    def _do_check(self, rdp):
        rv = set()
        for service_name in rdp.services:
            service = rdp.services.get(service_name)
            for cap in service.serviceCapacities:
                rv.add(cap.__name__)
        return ListResult(list(rv), "", True)
