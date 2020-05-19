################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains all code related to check objects
#
################################################################################

import sys

from rdp import Rdp

from breadp.checks import Check
from breadp.evaluations import Evaluation
from breadp.benchmarks import Benchmark

class Report(object):
    """ Base class and interface for checks, evaluations and benchmarks

    Attributes
    ----------
    id: int
        Identifier for the reported object
    name: str
        Class name of the reported object
    version:
        Version of the reported object
    description:
        Description of the reported object

    Methods
    -------
    json(self) -> str
        Returns a json representation of the report
    """
    def __init__(
        self,
        obj_id: str,
        name: str,
        version: str,
        description: str
    ):
        self.id = obj_id
        self.name = name
        self.version = version
        self.description = description

    def todict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description
        }

class CheckReport(Report):
    def __init__(self, pid: str, check: Check):
        Report.__init__(self, check.id, check.name, check.version, check.description)
        try:
            self.entry = check.log.get_by_pid(pid)[-1]
        except IndexError:
            self.entry = None
        self.type = check.type

    def todict(self) -> dict:
        rv = Report.todict(self)
        rv["type"] = self.type
        rv["start"] = self.entry.start
        rv["end"] = self.entry.end
        rv["success"] = self.entry.result.success
        rv["result"] = self.entry.result.outcome
        rv["msg"] = self.entry.result.msg
        return rv

class EvaluationReport(Report):
    def __init__(self, pid: str, ev: Evaluation):
        Report.__init__(self, ev.id, ev.name, ev.version, ev.description)
        self.checks = [str(c.id) for c in ev.checks]
        self.rounded = ev.rounded
        self.evaluation = ev.evaluate(pid)

    def todict(self) -> dict:
        rv = Report.todict(self)
        rv["checks"] = self.checks
        rv["rounded"] = self.rounded
        rv["evaluation"] = self.evaluation
        return rv

class BenchmarkReport(Report):
    def __init__(self, rdp: Rdp, b: Benchmark):
        Report.__init__(self, b.id, b.name, b.version, b.description)
        self.score = b.score(rdp)
        self.pid = rdp.pid
        self.aggregation_info = b.aggregation_info()
        # Attention!!!
        # Presupposes the benchmark ran on the same machine as the repost is
        # compiled on!
        self.precision = sys.float_info.mant_dig
        self.rounded = b.rounded
        self.evaluation_reports = []
        for ev in b.evaluations:
            if not b.skip(ev, rdp):
                self.evaluation_reports.append(EvaluationReport(rdp.pid, ev))
        self.check_reports = []
        for c in b.checks:
            self.check_reports.append(CheckReport(rdp.pid, c))


    def todict(self) -> dict:
        rv = Report.todict(self)
        rv["rounded"] = self.rounded
        rv["score"] = self.score
        rv["pid"] = self.pid
        rv["aggregation_info"] = self.aggregation_info
        rv["precision"] = self.precision
        rv["evaluation_reports"] = []
        for evrp in self.evaluation_reports:
            rv["evaluation_reports"].append(evrp.todict())
        rv["check_reports"] = []
        for chrp in self.check_reports:
            rv["check_reports"].append(chrp.todict())
        return rv

