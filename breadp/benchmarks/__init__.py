################################################################################
# Copyright: Tobias Weber 2020
#
# Apache 2.0 License
#
# This file contains code related to benchmark objects
#
################################################################################

from datetime import datetime
import inspect

class Benchmark(object):
    """ Base class and interface to benchmark RDPs

    Attributes
    ----------
    id: int
        Identifier for the benchmark
    version: str
        Version of the benchmark
    description: str
        A short text describing the benchmark (in English)
    evaluations:
        A list of evaluations

    Methods
    -------
    run(self, rdp) -> None
        Runs the benchmark
    """
    def __init__(self, name=None):
        def skip_function(evaluation, rdp):
            return False
        self.evaluations = []
        self.checks = []
        self.skip = skip_function
        self.version = "Blank benchmarks have no version"
        self.id = "Blank benchmarks have no id"
        self.rounded = 10
        self.name = name
        if self.name is None:
            self.name = type(self).__name__

    @property
    def description(self):
        return ' '.join(inspect.getdoc(self).split("\n\n")[0].split())

    def aggregation_info(self):
        """ specifies the aggregation mechanism in human readable format.
        """
        return "Artithmetic mean of evaluations with static and equal weights."

    def add_evaluation(self, evaluation):
        """ interface to add an evaluation

        Arguments
        ---------
        evaluation: Evaluation
            Evaluation to add
        """
        self.evaluations.append(evaluation)
        self.checks.extend(evaluation.checks)

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
            score += e.evaluate(rdp.pid)
        return round(score/numberOfEvalutations, self.rounded)
