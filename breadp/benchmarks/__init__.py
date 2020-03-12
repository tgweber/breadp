################################################################################
# Copyright: Tobias Weber 2020
#
# Apache 2.0 License
#
# This file contains code related to benchmark objects
#
################################################################################

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
        self.log = Log()
        self.evaluations = []
        self.skip = skip_function
        self.version = "Blank Benchmarks have no version"

    def run(self, rdp):
        """ Runs the benchmark

        Parameters
        ----------
        rdp: Rdp
            Research Data Product to be benchmarked
        """
        start = datetime.utcnow().isoformat()
        msg = "Run of benchmark {} in version {} for rdp {}".format(
            type(self).__name__,
            self.version,
            rdp.pid
        )
        success = True
        for e in self.evaluations:
            if self.skip(e, rdp):
                continue
            evaluation_success = e.evaluate(rdp)
            if not evaluation_success:
                success == False
        end = datetime.utcnow().isoformat()
        self.log.add(BenchmarkLogEntry(
            start,
            end,
            self.version,
            rdp.pid,
            msg,
            success)
        )

    def add_evaluation(self, evaluation):
        """ interface to add an evaluation

        Arguments
        ---------
        evaluation: Evaluation
            Evaluation to add
        """
        self.evaluations.append(evaluation)

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
        return score/numberOfEvalutations
