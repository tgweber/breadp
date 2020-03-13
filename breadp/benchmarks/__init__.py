################################################################################
# Copyright: Tobias Weber 2020
#
# Apache 2.0 License
#
# This file contains code related to benchmark objects
#
################################################################################

from datetime import datetime

class Benchmark(object):
    """ Base class and interface to benchmark RDPs

    Attributes
    ----------
    id: int
        Identifier for the benchmark
    version: str
        Version of the benchmark
    desc: str
        A short text describing the benchmark (in English)
    evaluations:
        A list of evaluations

    Methods
    -------
    run(self, rdp) -> None
        Runs the benchmark
    report(self, pid) -> dict
        Returns a dictionary of benchmark runs for the specified pid (incl.
        evaluations and checks)
    """
    def __init__(self):
        """
        Arguments
        ---------
        skip: function
            Determines whether an evaluation will be skipped for an RDP
            signature: skip(Evaluation: e, Rdp: rdp) -> bool
        """
        def skip_function(evaluation, rdp):
            return False
        self.evaluations = []
        self.checks = []
        self.skip = skip_function
        self.version = "Blank Benchmarks have no version"

    def add_evaluation(self, evaluation):
        """ interface to add an evaluation

        Arguments
        ---------
        evaluation: Evaluation
            Evaluation to add
        """
        self.evaluations.append(evaluation)
        self.checks.extend(evaluation.checks)

    def report(self, rdp):
        report = {
            "name": type(self).__name__,
            "version": self.version,
            "checks": [],
            "evaluations": []
        }
        for e in self.evaluations:
            if not self.skip(e, rdp):
                add_to_report = e.report()
                add_to_report["evaluation"] = round(e.evaluate(rdp), 10)
                report["evaluations"].append(add_to_report)
        for c in self.checks:
            report["checks"].append(c.report(rdp.pid))
        return report

    def check_all(self, rdp):
        for c in self.checks:
            c.check(rdp)

    def score(self, rdp):
        """ Returns the score for a given RDP (each evaluation has the same weight)

        """
        score = 0
        numberOfEvalutations = 0
        for e in self.evaluations:
            if self.skip(e, rdp):
                continue
            numberOfEvalutations+= 1
            score += e.evaluate(rdp)
        return round(score/numberOfEvalutations, 10)
