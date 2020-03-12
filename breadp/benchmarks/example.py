################################################################################
# Copyright: Tobias Weber 2020
#
# Apache 2.0 License
#
# This file contains code related to the DataCite best practice guide benchmark
#
# Basis for this benchmark: 10.5281/zenodo.3559800
#
################################################################################

from breadp.benchmarks import Benchmark
from breadp.checks.pid import IsValidDoiCheck, DoiResolvesCheck
from breadp.evaluations import \
        Evaluation, \
        TrueEvaluation
from breadp.rdp import Rdp

def skip(e: Evaluation, rdp: Rdp) -> bool:
    # Evaluating language make no sense for these types
    if type in ("Image", "PhysicalObject") and type(e) == LanguageEvaluation:
        return True
    # Version is optional
    if rdp.metadata.version is None and type(e) == VersionEvaluation:
        return True
    # Contributors are optional
    if len(rdp.metadata.contributors) == 0 and type(e) == ContributorEvaluation:
        return True
    # Related Resources are optional
    if len(rdp.metadata.relatedResources) == 0 and type(e) == RelatedResourcesEvaluation:
        return True
    return False

BPGBenchmark = Benchmark()
BPGBenchmark.skip = skip
BPGBenchmark.version = "0.0.1"

isValidDoiCheck = IsValidDoiCheck()
doiResolvesCheck = DoiResolvesCheck()

BPGBenchmark.add_evaluation(TrueEvaluation([isValidDoiCheck]))
BPGBenchmark.add_evaluation(TrueEvaluation([doiResolvesCheck]))
