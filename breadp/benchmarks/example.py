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
import sys

from breadp.benchmarks import Benchmark
from breadp.checks.pid import IsValidDoiCheck, DoiResolvesCheck
from breadp.checks.metadata import \
    CreatorsOrcidCheck, \
    CreatorsFamilyAndGivenNameCheck, \
    CreatorsContainInstitutionsCheck, \
    ContributorsOrcidCheck, \
    ContributorsFamilyAndGivenNameCheck, \
    ContributorsContainInstitutionsCheck, \
    ContributorsTypeCheck, \
    DatesInformationCheck, \
    DatesIssuedYearCheck, \
    DatesTypeCheck, \
    DescriptionsTypeCheck, \
    DescriptionsLanguageCheck, \
    DescriptionsLengthCheck, \
    DescriptionsNumberCheck, \
    FormatsAreValidMediaTypeCheck, \
    LanguageSpecifiedCheck, \
    PublicationYearCheck, \
    RelatedResourceMetadataCheck, \
    RelatedResourceTypeCheck, \
    RightsAreOpenCheck, \
    RightsHaveValidSPDXIdentifierCheck, \
    RightsHasAtLeastOneLicenseCheck, \
    SizesNumberCheck, \
    SizesByteSizeCheck, \
    SubjectsNumberCheck, \
    SubjectsHaveDdcCheck, \
    SubjectsAreQualifiedCheck, \
    SubjectsHaveWikidataKeywordsCheck, \
    TitlesJustAFileNameCheck, \
    TitlesLanguageCheck, \
    TitlesTypeCheck, \
    VersionSpecifiedCheck
from breadp.evaluations import \
    ContainsAllEvaluation, \
    ContainsAtLeastOneEvaluation, \
    ContainsItemExactlyNTimesEvaluation, \
    DoesNotContainEvaluation, \
    Evaluation, \
    FalseEvaluation, \
    FunctionEvaluation, \
    InListEvaluation, \
    IsBetweenEvaluation, \
    IsIdenticalToEvaluation, \
    TheMoreTrueTheBetterEvaluation, \
    TheMoreFalseTheBetterEvaluation, \
    TrueEvaluation
from rdp import Rdp

def skip(e: Evaluation, rdp: Rdp) -> bool:
    # Evaluating language make no sense for these types
    if rdp.metadata.type in ("Image", "PhysicalObject"):
        for c in e.checks:
            if type(c).__name__ == "LanguageSpecifiedCheck":
                return True
    # Version is optional
    if rdp.metadata.version is None:
        for c in e.checks:
            if type(c).__name__ == "VersionSpecifiedCheck":
                return True
    # Contributors are optional
    if len(rdp.metadata.contributors) == 0:
        # if the license is non-open, we need to check Rightsholder!
        if [c.name for c in e.checks] == ["RightsAreOpenCheck",
                                    "ContributorsTypeCheck"]:
            return False
        for c in e.checks:
            if c.name.startswith("Contributors"):
                return True
    # Related Resources are optional
    if len(rdp.metadata.relatedResources) == 0:
        for c in e.checks:
            if type(c).__name__.startswith("RelatedResource"):
                return True
    return False

class BPGBenchmark(Benchmark):
    """ This benchmark is inspired by the DataCite best practice guide
        (DOI: 10.5281/zenodo.3559799)
    """
    def __init__(self, name=None):
        Benchmark.__init__(self, "Best Practice Benchmark")
        self.skip = skip
        self.version = "0.0.1"
        self.id = "BPG"

        # PID
        isValidDoiCheck = IsValidDoiCheck()
        doiResolvesCheck = DoiResolvesCheck()
        self.add_evaluation(TrueEvaluation([isValidDoiCheck]))
        self.add_evaluation(TrueEvaluation([doiResolvesCheck]))

        # CREATOR
        creatorsOrcidCheck = CreatorsOrcidCheck()
        creatorsFamilyAndGivenNameCheck = CreatorsFamilyAndGivenNameCheck()
        creatorsContainInstitutionsCheck = CreatorsContainInstitutionsCheck()
        self.add_evaluation(
            TheMoreTrueTheBetterEvaluation([creatorsOrcidCheck])
        )
        self.add_evaluation(
            TheMoreTrueTheBetterEvaluation([creatorsFamilyAndGivenNameCheck])
        )
        self.add_evaluation(
            TheMoreFalseTheBetterEvaluation([creatorsContainInstitutionsCheck])
        )

        # TITLE
        titlesJustAFileNameCheck = TitlesJustAFileNameCheck()
        titlesTypeCheck = TitlesTypeCheck()
        titlesLanguageCheck = TitlesLanguageCheck()
        self.add_evaluation(FalseEvaluation([titlesJustAFileNameCheck]))
        self.add_evaluation(
            ContainsItemExactlyNTimesEvaluation(
                [titlesTypeCheck], None, 1
            )
        )
        self.add_evaluation(
            ContainsAllEvaluation(
                [titlesLanguageCheck], ["en"]
            )
        )

        # SUBJECT
        subjectsAreQualifiedCheck = SubjectsAreQualifiedCheck()
        subjectsNumberCheck = SubjectsNumberCheck()
        subjectsHaveDdcCheck = SubjectsHaveDdcCheck()
        subjectsHaveWikidataKeywordsCheck = SubjectsHaveWikidataKeywordsCheck()
        self.add_evaluation(
            TheMoreTrueTheBetterEvaluation([subjectsAreQualifiedCheck])
        )
        self.add_evaluation(
            IsBetweenEvaluation([subjectsNumberCheck], 1, sys.float_info.max)
        )
        self.add_evaluation(TrueEvaluation([subjectsHaveDdcCheck]))
        self.add_evaluation(TrueEvaluation([subjectsHaveWikidataKeywordsCheck]))

        # CONTRIBUTOR
        contributorsOrcidCheck = ContributorsOrcidCheck()
        contributorsFamilyAndGivenNameCheck = ContributorsFamilyAndGivenNameCheck()
        contributorsContainInstitutionsCheck = ContributorsContainInstitutionsCheck()
        contributorsTypeCheck = ContributorsTypeCheck()
        def allow_person_related_tests_to_be_skipped(checks, pid):
            evaluation = 0
            isInstitution = checks[0].get_last_result(pid).outcome
            booleanCheckResult = checks[1].get_last_result(pid).outcome
            newTotal = isInstitution.count(False)
            for idx, inst in enumerate(isInstitution):
                if inst:
                    continue
                if booleanCheckResult[idx]:
                    evaluation += 1/newTotal
            return evaluation
        self.add_evaluation(
            FunctionEvaluation(
                [
                    contributorsContainInstitutionsCheck,
                    contributorsOrcidCheck
                ],
                allow_person_related_tests_to_be_skipped
            )
        )
        self.add_evaluation(
            FunctionEvaluation(
                [
                    contributorsContainInstitutionsCheck,
                    contributorsFamilyAndGivenNameCheck
                ],
                allow_person_related_tests_to_be_skipped
            )
        )
        def allow_type_to_enforce_institution(checks, pid):
            evaluation = 0
            isInstitution = checks[0].get_last_result(pid).outcome
            contributorTypes  = checks[1].get_last_result(pid).outcome
            for idx, inst in enumerate(isInstitution):
                if inst:
                    if contributorTypes[idx] == "HostingInstitution":
                        evaluation += 1/len(isInstitution)
                else:
                    evaluation += 1/len(isInstitution)
            return evaluation
        self.add_evaluation(
            FunctionEvaluation(
                [
                    contributorsContainInstitutionsCheck,
                    contributorsTypeCheck
                ],
                allow_type_to_enforce_institution
            )
        )
        self.add_evaluation(
            InListEvaluation(
                [contributorsTypeCheck],
                ["ContactPerson",
                 "DataCollector",
                 "DataCurator",
                 "HostingInstitution",
                 "ProjectLeader",
                 "ProjectManager",
                 "ProjectMember",
                 "Researcher",
                 "RightsHolder",
                 "WorkPackageLeader"
                ],
            )
        )

        # DATES
        datesTypeCheck = DatesTypeCheck()
        publicationYearCheck = PublicationYearCheck()
        datesIssuedYearCheck = DatesIssuedYearCheck()
        datesInformationCheck = DatesInformationCheck()
        self.add_evaluation(
            ContainsAtLeastOneEvaluation([datesTypeCheck], ["Created", "Collected"])
        )
        def publishedEqualsIssued(checks, pid):
            return checks[0].get_last_result(pid).outcome \
                == checks[1].get_last_result(pid).outcome
        self.add_evaluation(
            FunctionEvaluation(
                [publicationYearCheck, datesIssuedYearCheck],
                publishedEqualsIssued,
            )
        )
        def duplicatesHaveInformation(checks, pid):
            r1 = checks[0].get_last_result(pid)
            r2 = checks[1].get_last_result(pid)
            if 0 in (len(r1.outcome), len(r2.outcome)):
                return 0
            dups = 0
            dupsWithInfo = 0
            dateTypesHasInformation = {}
            for idx, t in enumerate(r1.outcome):
                if dateTypesHasInformation.get(t) is not None:
                    dups += 1
                    if dateTypesHasInformation[t] and r2.outcome[idx] is not None:
                        dupsWithInfo += 1
                dateTypesHasInformation[t] = r2.outcome[idx] is not None
            if dups == 0:
                return 1
            else:
                return dupsWithInfo/dups
        self.add_evaluation(
            FunctionEvaluation(
                [datesTypeCheck, datesInformationCheck],
                duplicatesHaveInformation
            )
        )

        # LANGUAGE
        languageSpecifiedCheck = LanguageSpecifiedCheck()
        self.add_evaluation(TrueEvaluation([languageSpecifiedCheck]))

        # RELATED RESOURCES
        relatedResourceMetadataCheck = RelatedResourceMetadataCheck()
        relatedResourceTypeCheck = RelatedResourceTypeCheck()
        self.add_evaluation(TrueEvaluation([relatedResourceMetadataCheck]))
        self.add_evaluation(
            InListEvaluation(
                [relatedResourceTypeCheck],
                [
                    "Describes",
                    "IsDescribedBy",
                    "HasPart",
                    "IsPartOf",
                    "HasMetadata",
                    "IsMetadataFor",
                    "HasVersion",
                    "IsVersionOf",
                    "IsNewVersionOf",
                    "IsPreviousVersionOf",
                    "IsSourceOf",
                    "IsDerivedFrom",
                    "References",
                    "IsReferencedBy",
                    "IsVariantFormOf",
                    "IsIdenticalTo",
                    "IsSupplementTo",
                    "IsSupplementedBy",
                    "Documents",
                    "IsDocumentedBy"
                ]
            )
        )

        # SIZE
        sizesNumberCheck = SizesNumberCheck()
        sizesByteSizeCheck = SizesByteSizeCheck()
        self.add_evaluation(
            IsIdenticalToEvaluation([sizesNumberCheck], 1)
        )
        self.add_evaluation(
            ContainsItemExactlyNTimesEvaluation(
                [sizesByteSizeCheck],
                True,
                1
            )
        )

        # FORMAT
        formatsAreValidMediaTypeCheck = FormatsAreValidMediaTypeCheck()
        self.add_evaluation(
            TheMoreTrueTheBetterEvaluation([formatsAreValidMediaTypeCheck])
        )

        # VERSION
        versionSpecifiedCheck = VersionSpecifiedCheck()
        self.add_evaluation(TrueEvaluation([versionSpecifiedCheck]))

        # RIGHTS
        rightsHasAtLeastOneLicenseCheck = RightsHasAtLeastOneLicenseCheck()
        rightsHaveValidSPDXIdentifierCheck = RightsHaveValidSPDXIdentifierCheck()
        rightsAreOpenCheck = RightsAreOpenCheck()
        self.add_evaluation(TrueEvaluation([rightsHasAtLeastOneLicenseCheck]))
        self.add_evaluation(
            TheMoreTrueTheBetterEvaluation([rightsHaveValidSPDXIdentifierCheck])
        )

        # DESCRIPTIONS
        descriptionsNumberCheck = DescriptionsNumberCheck()
        descriptionsLengthCheck = DescriptionsLengthCheck()
        descriptionsLanguageCheck = DescriptionsLanguageCheck()
        descriptionsTypeCheck = DescriptionsTypeCheck()
        self.add_evaluation(
            IsBetweenEvaluation(
                [descriptionsNumberCheck], 1, sys.float_info.max
            )
        )
        self.add_evaluation(
            IsBetweenEvaluation(
                [descriptionsLengthCheck], 1, 300
            )
        )
        self.add_evaluation(
            ContainsAllEvaluation(
                [descriptionsLanguageCheck], ["en"]
            )
        )
        self.add_evaluation(
            ContainsAllEvaluation(
                [descriptionsTypeCheck], ["Abstract"]
            )
        )
        self.add_evaluation(
            DoesNotContainEvaluation(
                [descriptionsTypeCheck],
                ["SeriesInformation", "TableOfContents", "Other", None]
            )
        )

        # MIXED
        def rightsHolderIfRightsClosed(checks, pid):
            rightsAreOpen = checks[0].get_last_result(pid).outcome
            contributorsType = checks[1].get_last_result(pid).outcome
            if rightsAreOpen:
                return 1
            elif "RightsHolder" in contributorsType:
                return 1
            else:
                return 0
        self.add_evaluation(
            FunctionEvaluation(
                [rightsAreOpenCheck, contributorsTypeCheck],
                rightsHolderIfRightsClosed
            )
        )
