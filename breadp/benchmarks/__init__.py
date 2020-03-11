################################################################################
# Copyright: Tobias Weber 2020
#
# Apache 2.0 License
#
# This file contains code related to benchmark objects
#
################################################################################

from collections import Counter, OrderedDict
from datetime import datetime

from breadp.util.log import Log, BenchmarkLogEntry

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
    log: list <BenchmarkLogEntry>
        List of log entries of benchmark runs

    Methods
    -------
    run(self, rdp) -> None
        Runs the benchmark
    report(self, pid) -> dict
        Returns a dictionary of benchmark runs for the specified pid (incl.
        evaluations and checks)
    """
    def __init__(self, skip):
        """
        Arguments
        ---------
        skip: function
            Determines whether an evaluation will be skipped for an RDP
            signature: skip(Evaluation: e, Rdp: rdp) -> bool
        """
        self.log = Log()
        self.evaluations = OrderedDict()
        self.score = 0
        self.skip = skip

    def run(self, rdp):
        """ Runs the benchmark

        Parameters
        ----------
        rdp: Rdp
            Research Data Product to be benchmarked
        """
        start = datetime.utcnow().isoformat()
        weights = self._calculate_weights(rdp)
        for e_key, e in self.evaluations.items():
            if self.skip(e, rdp):
                continue
            self.score += e["evaluation"].evaluate(rdp) * weights[e_key]
        end = datetime.utcnow().isoformat()
        self.log.add(EvaluationLogEntry(
            start,
            end,
            self.version,
            rdp.pid,
            msg,
            success,
            self.score)
        )

    def add_evaluation(self, evaluation, weight):
        """ interface to add an evaluation

        Arguments
        ---------
        evaluation: Evaluation
            Evaluation to add
        weight: int
            Weight of the evaluation (the result of the evaluation will be
            multiplied with weight/sum(weights)
        """
        self.evaluations[type(evaluation).__name__] = {
            "evaluation": evaluation,
            "weight": weight
        }

    def _calculate_weights(self, rdp):
        """ Calculate the weight for the given RDP

        Arguments
        ---------
        rdp: Rdp
            Research data product (necessary to determine whether an evaluation
            has to be skipped)
        """
        total = 0
        for e in self.evaluations.values():
            if self.skip(e, rdp):
                continue
            total += e["weight"]
        return dict([(e_key, e["weight"]/total) for e_key, e in self.evaluations.items()])
