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
    ContainsEvaluationPart, \
    ContainsItemExactlyNTimesEvaluationPart, \
    DoesNotContainEvaluationPart, \
    Evaluation, \
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
    DescriptionsLanguageCheck, \
    DescriptionsLengthCheck, \
    DescriptionsNumberCheck, \
    LanguageSpecifiedCheck, \
    FormatsAreValidMediaTypeCheck, \
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
            ContainsEvaluationPart(
                DescriptionsLanguageCheck(),
                ["en"],
                4)
        )
        ddtc = DataCiteDescriptionsTypeCheck()
        self.add_evaluation_part(ContainsEvaluationPart(ddtc, ["Abstract"]))
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
        self.add_evaluation_part(ContainsEvaluationPart(TitlesLanguageCheck(), ["en"]))

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

