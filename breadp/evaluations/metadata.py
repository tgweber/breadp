################################################################################
# Copyright: Tobias Weber 2020
#
# Apache 2.0 License
#
# This file contains all Evaluation-related tests
#
################################################################################
import sys

from breadp.evaluations import \
    AllFalseEvaluationPart, \
    BatchEvaluation, \
    CompositeEvaluation, \
    ContainsAllEvaluationPart, \
    ContainsAtLeastOneEvaluationPart, \
    ContainsItemExactlyNTimesEvaluationPart, \
    DoesNotContainEvaluationPart, \
    Evaluation, \
    FunctionEvaluationPart, \
    InListEvaluationPart, \
    IsBetweenEvaluationPart, \
    IsFalseEvaluationPart, \
    IsIdenticalToEvaluationPart, \
    IsTrueEvaluationPart, \
    SimpleAndEvaluation, \
    TheMoreTrueTheBetterEvaluationPart
from breadp.rdp.metadata.datacite import DataCiteMetadata
from breadp.checks.metadata import \
    CreatorsOrcidCheck, \
    CreatorsFamilyAndGivenNameCheck, \
    CreatorsContainInstitutionsCheck, \
    ContributorsOrcidCheck, \
    ContributorsFamilyAndGivenNameCheck, \
    ContributorsContainInstitutionsCheck, \
    ContributorsTypeCheck, \
    DataCiteDescriptionsTypeCheck, \
    DatesInformationCheck, \
    DatesIssuedYearCheck, \
    DatesTypeCheck, \
    DescriptionsLanguageCheck, \
    DescriptionsLengthCheck, \
    DescriptionsNumberCheck, \
    FormatsAreValidMediaTypeCheck, \
    LanguageSpecifiedCheck, \
    PublicationYearCheck, \
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

class DescriptionEvaluation(CompositeEvaluation):
    """ Evaluation for descriptions of the metadata of an RDP
    """
    def __init__(self):

        CompositeEvaluation.__init__(self)
        self.version = "0.0.1"
        self.id = 1
        self.add_evaluation_part(
            IsBetweenEvaluationPart(
                DescriptionsNumberCheck(),
                1.0,
                sys.float_info.max,
                4)
        )
        self.add_evaluation_part(
            IsBetweenEvaluationPart(
                DescriptionsLengthCheck(),
                3.0,
                300.0,
                4)
        )
        self.add_evaluation_part(
            ContainsAllEvaluationPart(
                DescriptionsLanguageCheck(),
                ["en"],
                4)
        )
        ddtc = DataCiteDescriptionsTypeCheck()
        self.add_evaluation_part(ContainsAllEvaluationPart(ddtc, ["Abstract"]))
        self.add_evaluation_part(
            DoesNotContainEvaluationPart(
                ddtc,
                ["SeriesInformation", "TableOfContents", "Other"])
        )

class TitleEvaluation(CompositeEvaluation):
    """ Evaluation for the titles of the metadata of an RDP
    """
    def __init__(self):
        CompositeEvaluation.__init__(self)
        self.version = "0.0.1"
        self.id = 2
        self.add_evaluation_part(AllFalseEvaluationPart(TitlesJustAFileNameCheck()))
        self.add_evaluation_part(
            ContainsItemExactlyNTimesEvaluationPart(TitlesTypeCheck(), None, 1)
        )
        self.add_evaluation_part(ContainsAllEvaluationPart(TitlesLanguageCheck(), ["en"]))

class FormatEvaluation(CompositeEvaluation):
    """ Evaluation for the format specification of the metadata of an RDP
    """
    def __init__(self):
        CompositeEvaluation.__init__(self)
        self.version = "0.0.1"
        self.id = 3
        self.add_evaluation_part(
            TheMoreTrueTheBetterEvaluationPart(FormatsAreValidMediaTypeCheck())
        )

class RightsEvaluation(CompositeEvaluation):
    """ Evaluation for the rights specification of the metadata of an RDP
    """
    def __init__(self):
        CompositeEvaluation.__init__(self)
        self.version = "0.0.1"
        self.id = 4
        self.add_evaluation_part(IsTrueEvaluationPart(RightsHasAtLeastOneLicenseCheck(),2))
        self.add_evaluation_part(
            TheMoreTrueTheBetterEvaluationPart(RightsHaveValidSPDXIdentifierCheck())
        )

class SubjectEvaluation(CompositeEvaluation):
    """ Evaluation for the subject specification of the metadata of an RDP
    """
    def __init__(self):
        CompositeEvaluation.__init__(self)
        self.version = "0.0.1"
        self.id = 5
        self.add_evaluation_part(
            TheMoreTrueTheBetterEvaluationPart(SubjectsAreQualifiedCheck())
        )
        self.add_evaluation_part(
            IsBetweenEvaluationPart(
                SubjectsNumberCheck(),
                1.0,
                sys.float_info.max,)
        )
        self.add_evaluation_part(IsTrueEvaluationPart(SubjectsHaveDdcCheck(),2))
        self.add_evaluation_part(IsTrueEvaluationPart(SubjectsHaveWikidataKeywordsCheck(),2))

class CreatorEvaluation(CompositeEvaluation):
    """ Evaluation for the creator specification of the metadata of an RDP
    """
    def __init__(self):
        CompositeEvaluation.__init__(self)
        self.version = "0.0.1"
        self.id = 6
        self.add_evaluation_part(TheMoreTrueTheBetterEvaluationPart(CreatorsOrcidCheck(),10))
        self.add_evaluation_part(
            TheMoreTrueTheBetterEvaluationPart(CreatorsFamilyAndGivenNameCheck())
        )
        self.add_evaluation_part(IsFalseEvaluationPart(CreatorsContainInstitutionsCheck()))

class SizeEvaluation(CompositeEvaluation):
    """ Evaluation for the size specification of the metadata of an RDP
    """
    def __init__(self):
        CompositeEvaluation.__init__(self)
        self.version = "0.0.1"
        self.id = 7
        self.add_evaluation_part(IsIdenticalToEvaluationPart(SizesNumberCheck(),1))
        self.add_evaluation_part(ContainsItemExactlyNTimesEvaluationPart(
            SizesByteSizeCheck(),
            True,
            1
        ))

class LanguageEvaluation(CompositeEvaluation):
    """ Evaluation for the language specification of the metadata of an RDP
    """
    def __init__(self):
        CompositeEvaluation.__init__(self)
        self.version = "0.0.1"
        self.id = 8
        self.add_evaluation_part(IsTrueEvaluationPart(LanguageSpecifiedCheck()))

class VersionEvaluation(CompositeEvaluation):
    """ Evaluation for the version specification of the metadata of an RDP
    """
    def __init__(self):
        CompositeEvaluation.__init__(self)
        self.version = "0.0.1"
        self.id = 9
        self.add_evaluation_part(IsTrueEvaluationPart(VersionSpecifiedCheck()))

class ContributorEvaluation(CompositeEvaluation):
    """ Evaluation for the contributor specification of the metadata of an RDP
    """
    def __init__(self):
        CompositeEvaluation.__init__(self)
        self.version = "0.0.1"
        self.id = 10
        self.add_evaluation_part(
            TheMoreTrueTheBetterEvaluationPart(ContributorsOrcidCheck(),10)
        )
        self.add_evaluation_part(
            TheMoreTrueTheBetterEvaluationPart(ContributorsFamilyAndGivenNameCheck())
        )
        self.add_evaluation_part(
            IsFalseEvaluationPart(ContributorsContainInstitutionsCheck())
        )
        self.add_evaluation_part(
            InListEvaluationPart(ContributorsTypeCheck(),
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
                3
        )
        )

class ContributorRightsEvaluation(CompositeEvaluation):
    """ Evaluation for the combination of contributor and rights specification
        of the metadata of an RDP.
    """
    def __init__(self):
        CompositeEvaluation.__init__(self)
        self.version = "0.0.1"
        self.id = 11

        def rightsHolderIfRightsClosed(checks):
            rightsAreOpenCheck = checks[0]
            contributorsTypeCheck = checks[1]
            if rightsAreOpenCheck.result.outcome:
                return 1
            elif "RightsHolder" in contributorsTypeCheck.result.outcome:
                return 1
            else:
                return 0

        self.add_evaluation_part(
            FunctionEvaluationPart(
                [
                    RightsAreOpenCheck(),
                    ContributorsTypeCheck()
                ],
                rightsHolderIfRightsClosed
            )
        )

class DatesEvaluation(CompositeEvaluation):
    """ Evaluation for the dates and publicationYear specification
        of the metadata of an RDP.
    """
    def __init__(self):
        CompositeEvaluation.__init__(self)
        self.version = "0.0.1"
        self.id = 12

        dtc = DatesTypeCheck()

        self.add_evaluation_part(
            ContainsAtLeastOneEvaluationPart(
                dtc,
                ["Created", "Collected"],
            )
        )

        def publishedEqualsIssued(checks):
            if checks[0].result.outcome == checks[1].result.outcome:
                return 1
            return 0

        self.add_evaluation_part(
            FunctionEvaluationPart(
                [
                    PublicationYearCheck(),
                    DatesIssuedYearCheck()
                ],
                publishedEqualsIssued,
            )
        )

        def duplicatesHaveInformation(checks):
            if 0 in (len(checks[0].result.outcome), len(checks[1].result.outcome)):
                return 0
            dups = 0
            dupsWithInfo = 0
            dateTypesHasInformation = {}
            for idx, t in enumerate(checks[0].result.outcome):
                if dateTypesHasInformation.get(t) is not None:
                    dups += 1
                    if dateTypesHasInformation[t] and checks[1].result.outcome[idx] is not None:
                        dupsWithInfo += 1
                dateTypesHasInformation[t] = checks[1].result.outcome[idx] is not None
            if dups == 0:
                return 1
            else:
                return dupsWithInfo/dups

        self.add_evaluation_part(
            FunctionEvaluationPart(
                [
                    dtc,
                    DatesInformationCheck()
                ],
                duplicatesHaveInformation
            )
        )

