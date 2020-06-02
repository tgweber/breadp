################################################################################
# Copyright: Tobias Weber 2020
#
# Apache 2.0 License
#
# This file contains all code related for metadata checks
#
################################################################################
import json
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
import os
import pandas as pd
from rdp.services.capacities import RetrieveDataHttpHeaders
import re
import requests
import sys

DetectorFactory.seed = 0

from breadp.checks import Check
from breadp.checks.result import BooleanResult, \
        ListResult, \
        MetricResult

class DescriptionsNumberCheck(Check):
    """ Checks the number of descriptions in the metadata for an RDP

    Methods
    -------
    _do_check(self, rdp)
        returns a MetricResult
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 2
        self.version = "0.0.1"

    def _do_check(self, rdp):
        return MetricResult(len(rdp.metadata.descriptions), "", True)

class DescriptionsLengthCheck(Check):
    """ Checks the length of all description in words

    Methods
    -------
    _do_check(self, rdp)
        returns a ListResult (of length values in words)
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 3
        self.version = "0.0.1"

    def _do_check(self, rdp):
        lengths = []
        msg = "No descriptions retrievable"
        for d in rdp.metadata.descriptions:
            msg = ""
            lengths.append(len(d.text.split()))
        return ListResult(lengths, msg, True)

class DescriptionsLanguageCheck(Check):
    """ Checks the language of the descriptions

    Methods
    -------
    _do_check(self, rdp)
        returns a ListResult (of strings with ISO-639-1 codes)
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 4
        self.version = "0.0.1"

    def _do_check(self, rdp):
        languages = []
        msg = "No descriptions retrievable"
        for d in rdp.metadata.descriptions:
            msg = ""
            try:
                languages.append(detect(d.text))
            except LangDetectException:
                languages.append(None)
        return ListResult(languages, msg, True)

class DescriptionsTypeCheck(Check):
    """ Checks all description types of DataCite metadata

    Methods
    -------
    _do_check(self, rdp)
        returns a ListResult (for each description the type of the description,
        as specified in the DataCite standard)
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 5
        self.version = "0.0.1"

    def _do_check(self, rdp):
        types = []
        if len(rdp.metadata.descriptions) == 0:
            return ListResult(types, "No descriptions retrievable", True)
        for d in rdp.metadata.descriptions:
            if d.type:
                types.append(d.type)
        return ListResult(types, "", True)

class TitlesNumberCheck(Check):
    """ Checks the number of titles in the metadata of an RDP

    Methods
    -------
    _do_check(self, rdp)
        returns a MetricResult
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 6
        self.version = "0.0.1"

    def _do_check(self, rdp):
        if not rdp.metadata.titles:
            msg = "No titles could be retrieved"
            return MetricResult(float(0), msg, True)
        return MetricResult(len(rdp.metadata.titles), "", True)

class TitlesLengthCheck(Check):
    """ Checks the length of all titles (in words)

    Methods
    -------
    _do_check(self, rdp)
        returns a ListResult (of all title lengths in words as int)
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 7
        self.version = "0.0.1"

    def _do_check(self, rdp):
        lengths = []
        msg = "No titles retrievable"
        for t in rdp.metadata.titles:
            msg = ""
            lengths.append(len(t.text.split()))
        return ListResult(lengths, msg, True)

class TitlesLanguageCheck(Check):
    """ Checks the language of all titles title

    Methods
    -------
    _do_check(self, rdp)
        returns a ListResult (of str encoding ISO-639-1 codes)
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 8
        self.version = "0.0.1"

    def _do_check(self, rdp):
        languages = []
        msg = "No titles retrievable"
        for t in rdp.metadata.titles:
            msg = ""
            try:
                languages.append(detect(t.text))
            except LangDetectException:
                languages.append(None)
        return ListResult(languages, msg, True)

class TitlesJustAFileNameCheck(Check):
    """ Checks whether the titles are (probably) just a file names

    Methods
    -------
    _do_check(self, rdp)
        returns a ListResult (of bools indicating whether the title is probably
        just a file name)
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 9
        self.version = "0.0.1"

    def _do_check(self, rdp):
        bools = []
        msg = ""
        if len(rdp.metadata.titles) == 0:
            msg = "No titles retrievable"
        for t in rdp.metadata.titles:
            msg = ""
            if re.match(r"^\s*\S+\.\S+\s*$", t.text):
                msg += "{} is probably just a file name;".format(t.text)
                bools.append(True)
            else:
                bools.append(False)
        return ListResult(bools, msg, True)

class TitlesTypeCheck(Check):
    """ Checks the types of all titles (None if not given)

    Methods
    -------
    _do_check(self, rdp)
        returns a ListResult (of all types of titles as str)
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 10
        self.version = "0.0.1"

    def _do_check(self, rdp):
        types = []
        msg = "No titles retrievable"
        for t in rdp.metadata.titles:
            msg = ""
            types.append(t.type)
        return ListResult(types, msg, True)

class FormatsAreValidMediaTypeCheck(Check):
    """ Checks which formats are valid IANA MediaTypes
        Canonical source: https://www.iana.org/assignments/media-types/media-types.xhtml
        Retrieved 2020-02-19 for this version
    Methods
    -------
    _do_check(self, rdp)
        returns a ListResult (of bools indicating valid media types)
    """

    def __init__(self):
        Check.__init__(self)
        self.id = 12
        self.version = "0.0.1"

    def _do_check(self, rdp):
        valid = []
        iana_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'resources',
            'mediatypes.csv'
        )
        iana = pd.read_csv(iana_file_path)
        if len(rdp.metadata.formats) == 0:
            msg = "No formats found!"
        else:
            msg= ""
        for f in rdp.metadata.formats:
            if f not in iana.Template.tolist():
                msg += "{} is not a valid format ".format(f)
                valid.append(False)
            else:
                valid.append(True)
        return ListResult(valid, msg, True)

class RightsHaveValidSPDXIdentifierCheck(Check):
    """ Checks whether all rights have valid SPDX licenses identifiers
        Canonical source: https://github.com/spdx/license-list-data/blob/master/json/licenses.json
        Retrieved 2020-02-26 for this version

    Methods
    -------
    _do_check(self, rdp)
        returns a ListResult (indicating valid SPDX identifiers)
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 13
        self.version = "0.0.1"
        spdxFilePath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'resources',
            'licenses.json'
        )
        with open(spdxFilePath, "r") as f:
            licenses_dict = json.load(f)
        self.licenses = pd.DataFrame(licenses_dict["licenses"])

    def _do_check(self, rdp):
        valid = []
        msg = "No rights objects found!"
        for r in rdp.metadata.rights:
            msg = ""
            if r.spdx not in self.licenses.licenseId.tolist():
                msg += "{} is not a valid SPDX identifier".format(r.spdx)
                valid.append(False)
            else:
                valid.append(True)
        return ListResult(valid, msg, True)

class RightsHasAtLeastOneLicenseCheck(Check):
    """ Checks whether at least one license statement is among the rights
        of the metadata of the RDP

    Methods
    -------
    _do_check(self, rdp)
        returns a BooleanResult, indicating whether there is a license statement
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 14
        self.version = "0.0.1"

    def _do_check(self, rdp):
        msg = ""
        if len(rdp.metadata.rights) == 0:
            msg = "No rights specified"
        for ro in rdp.metadata.rights:
            if not ro.uri and not str(ro.uri).startswith("info:eu-repo"):
                continue
            try:
                response = requests.head(ro.uri)
                if response.status_code > 199 and response.status_code < 400:
                    return BooleanResult(True, "", True)
                else:
                    msg = "No license retrievable: {}".format(response.status_code)
                    continue
            except Exception as e:
                msg += "{}: {}".format(type(e), e)
                continue
        return BooleanResult(False, msg, True)

class RightsAreOpenCheck(Check):
    """ Checks whether rights are open, i.e. their usage is not restricted in a
        way that necessitates interaction with the rightsholder.

    Methods
    -------
    _do_check(self, rdp)
        returns a BooleanResult, indicating whether the rights are open
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 30
        self.version = "0.0.1"

    def _do_check(self, rdp):
        msg = ""
        if len(rdp.metadata.rights) == 0:
            msg = "No rights specified"
        for ro in rdp.metadata.rights:
            if rights_are_open(ro):
                return BooleanResult(True, "{} is open".format(ro.text), True)
        return BooleanResult(False, "Rights are not open (or not specified)", True)

class SubjectsAreQualifiedCheck(Check):
    """ Checks subjects have qualified subjects (subjects are either specified
        by a scheme name or a scheme URI)"

    Methods
    -------
    _do_check(self, rdp)
        returns a ListResult, indicating which subjects are qualified
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 15
        self.version = "0.0.1"

    def _do_check(self, rdp):
        qualified = []
        msg = ""
        if len(rdp.metadata.rights) == 0:
            msg = "No subjects retrievable"
        for so in rdp.metadata.subjects:
            if so.uri or so.scheme:
                qualified.append(True)
            else:
                qualified.append(False)
        return ListResult(qualified, msg, True)

class SubjectsNumberCheck(Check):
    """ Checks the number of subjects

    Methods
    -------
    _do_check(self, rdp)
        returns a MetricResult, indicating the number of subjects
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 16
        self.version = "0.0.1"

    def _do_check(self, rdp):
        return MetricResult(len(rdp.metadata.subjects), "", True)


class SubjectsHaveDdcCheck(Check):
    """ Checks whether the subjects contain a valid DDC field of study specification.

    Methods
    -------
    _do_check(self, rdp)
        returns a BooleanResult, indicating the existance of a valid DDC field
        of study specification
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 17
        self.version = "0.0.1"

    def _do_check(self, rdp):
        for so in rdp.metadata.subjects:
            if re.match("^(ddc|dewey)|ddc$", str(so.scheme), re.IGNORECASE) \
              or "dewey.info" in str(so.uri):
                if re.match(r"^\d\d\d", so.text):
                    return BooleanResult(
                        True,
                        "{} is a DDC field of study specificiation".format(so.text),
                        True
                    )
        return BooleanResult(False, "No DDC field of study specification found", True)

class SubjectsHaveWikidataKeywordsCheck(Check):
    """ Checks whether the subjects contain keynames for field of study specification.

    Methods
    -------
    _do_check(self, rdp)
        returns a BooleanResult, indicating the existance of a valid DDC field
        of study specification
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 18
        self.version = "0.0.1"

    def _do_check(self, rdp):
        for so in rdp.metadata.subjects:
            if str(so.uri).startswith("https://www.wikidata.org/wiki"):
                for value in (str(so.text), str(so.valueURI)):
                    if re.match(r"q\d+$", value.split("/")[-1], re.IGNORECASE):
                        return BooleanResult(
                            True,
                            "{} is a wikidata keyword ".format(so.text),
                            True
                        )
        return BooleanResult(False, "No wikidata keyword found", True)

class CreatorsOrcidCheck(Check):
    """ Checks whether the creators have valid orcids
        Documentation with regard to ORCiDs has been retrieved from
        https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
        (2020-03-04)

    Methods
    -------
    _do_check(self, rdp)
        returns a ListResult of bools, indicating the existence of valid orcids
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 19
        self.version = "0.0.1"

    def _do_check(self, rdp):
        valid = []
        for po in rdp.metadata.creators:
            if po.orcid is None:
                valid.append(False)
                continue
            # Test format
            valid.append(is_valid_orcid(po.orcid))
        return ListResult(valid, "", True)

class CreatorsFamilyAndGivenNameCheck(Check):
    """ Checks whether the creators have distinguishable family and given names

    Methods
    -------
    _do_check(self, rdp)
        returns a ListResult of bools, indicating the existence of distinguishable
        family and given names
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 20
        self.version = "0.0.1"

    def _do_check(self, rdp):
        valid = []
        for po in rdp.metadata.creators:
            valid.append(has_family_and_given_name(po))
        return ListResult(valid, "", True)

class CreatorsContainInstitutionsCheck(Check):
    """ Checks whether the creators contain institutions

    Methods
    -------
    _do_check(self, rdp)
        returns a ListResult, indicating whether the contributors are an institution.

    """
    def __init__(self):
        Check.__init__(self)
        self.id = 21
        self.version = "0.0.1"

    def _do_check(self, rdp):
        institutions = []
        success = False
        for po in rdp.metadata.creators:
            success = True
            if po.person:
                institutions.append(False)
            else:
                institutions.append(True)
        return ListResult(institutions, "", success)

class SizesNumberCheck(Check):
    """ Checks the number of size specifications

    Methods
    -------
    _do_check(self, rdp)
        returns a MetricResult, indicating the number of size specifications

    """
    def __init__(self):
        Check.__init__(self)
        self.id = 22
        self.version = "0.0.1"

    def _do_check(self, rdp):
            return MetricResult(len(rdp.metadata.sizes), "", True)

class SizesByteSizeCheck(Check):
    """ Checks which of the size specifications have a valid *byte-specification,
        i.e. a number followed by a (k|m|g|t|p|e|z|y)g unit (case-insensivite)

    Methods
    -------
    _do_check(self, rdp)
        returns a ListResult of Booleans, indicating which size specification
        has a valid *byte-specification

    """
    def __init__(self):
        Check.__init__(self)
        self.id = 23
        self.version = "0.0.1"

    def _do_check(self, rdp):
        valid = []
        msg = "no sizes specified"
        for s in rdp.metadata.sizes:
            msg = ""
            if re.match(r"^\d+\s*(k|m|g|t|p|e|z|y){0,1}i{0,1}b$", s, re.IGNORECASE):
                valid.append(True)
            else:
                valid.append(False)
        return ListResult(valid, msg, True)

class VersionSpecifiedCheck(Check):
    """ Checks whether the version of the RDP is specified in semantic versioning format.

    Methods
    -------
    _do_check(self, rdp)
        returns a BooleanResult, indicating whether the version of the RDP is specified
        in semantic versioning format.
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 24
        self.version = "0.0.1"

    def _do_check(self, rdp):
        if rdp.metadata.version is None:
            return BooleanResult(False, "no version specified", False)
        if re.match(r"^\d+\.\d+\.\d+(-\S+){0,1}$", rdp.metadata.version):
            return BooleanResult(True, "", True)
        return BooleanResult(
            False,
            "'{}' is not in semantic versioning format".format(rdp.metadata.version),
            True
        )

class LanguageSpecifiedCheck(Check):
    """ Checks whether the language of the RDP is specified as a ISO-639-1 code.
        Canonical source: https://pkgstore.datahub.io/core/language-codes/language-codes-full_json/data/573588525f24edb215c07bec3c309153/language-codes-full_json.json
        Retrieved 2020-03-06 for this version

    Methods
    -------
    _do_check(self, rdp)
        returns a BooleanResult, indicating whether the language of the RDP is
        specified as a ISO 639-1 code.
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 25
        self.version = "0.0.1"

        iso_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'resources',
            'iso-639.json'
        )
        self.iso_codes = pd.read_json(iso_file_path)

    def _do_check(self, rdp):
        if rdp.metadata.language is None:
            return BooleanResult(False, "no language specified", True)
        if rdp.metadata.language in self.iso_codes.alpha2.tolist():
            return BooleanResult(True, "", True)
        return BooleanResult(
            False,
            "'{}' is not a valid ISO-639-1 code".format(rdp.metadata.language),
            True
        )

class ContributorsOrcidCheck(Check):
    """ Checks whether the contributors have valid orcids
        Documentation with regard to ORCiDs has been retrieved from
        https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
        (2020-03-04)

    Methods
    -------
    _do_check(self, rdp)
        returns a ListResult of bools, indicating the existence of valid orcids
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 26
        self.version = "0.0.1"

    def _do_check(self, rdp):
        valid = []
        for po in rdp.metadata.contributors:
            if po.orcid is None:
                valid.append(False)
                continue
            valid.append(is_valid_orcid(po.orcid))
        return ListResult(valid, "", True)

class ContributorsFamilyAndGivenNameCheck(Check):
    """ Checks whether the contributors have distinguishable family and given names

    Methods
    -------
    _do_check(self, rdp)
        returns a ListResult of bools, indicating the existence of distinguishable
        family and given names
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 27
        self.version = "0.0.1"

    def _do_check(self, rdp):
        valid = []
        for po in rdp.metadata.contributors:
            valid.append(has_family_and_given_name(po))
        return ListResult(valid, "", True)

class ContributorsContainInstitutionsCheck(Check):
    """ Checks whether the contributors contain institutions

    Methods
    -------
    _do_check(self, rdp)
        returns a BooleanResult, indicating whether an institution is part of the contributors.

    """
    def __init__(self):
        Check.__init__(self)
        self.id = 28
        self.version = "0.0.1"

    def _do_check(self, rdp):
        institutions = []
        success = False
        for po in rdp.metadata.contributors:
            success = True
            if po.person:
                institutions.append(False)
            else:
                institutions.append(True)
        return ListResult(institutions, "", success)

class ContributorsTypeCheck(Check):
    """ Checks whether the type of the contributors

    Methods
    -------
    _do_check(self, rdp)
        returns a ListResult of str, indicating the type of each contributor.

    """
    def __init__(self):
        Check.__init__(self)
        self.id = 29
        self.version = "0.0.1"

    def _do_check(self, rdp):
        types = []
        for po in rdp.metadata.contributors:
            types.append(po.type)
        return ListResult(types, "", True)

class PublicationYearCheck(Check):
    """ Checks the year of the publication

    Methods
    -------
    _do_check(self, rdp)
        returns a MetricResult, indicating the year of publication

    """
    def __init__(self):
        Check.__init__(self)
        self.id = 31
        self.version = "0.0.1"

    def _do_check(self, rdp):
        if rdp.metadata.publicationYear is None:
            return MetricResult(
                sys.float_info.min,
                "No publicationYear retrievable",
                False
            )
        return MetricResult(rdp.metadata.publicationYear, "", True)

class DatesTypeCheck(Check):
    """ Checks the types of the dates of the publication

    Methods
    -------
    _do_check(self, rdp)
        returns a ListResult, indicating the types of the dates

    """
    def __init__(self):
        Check.__init__(self)
        self.id = 32
        self.version = "0.0.1"

    def _do_check(self, rdp):
        types = []
        msg = "No dates retrievable"
        for d in rdp.metadata.dates:
            msg = ""
            types.append(d.type)
        return ListResult(types, msg, True)

class DatesIssuedYearCheck(Check):
    """ Checks whether the year of issuance is specified (in the date fields)

    Methods
    -------
    _do_check(self, rdp)
        returns a MetricResult, indicating the year of issuance (in the date fields)

    """
    def __init__(self):
        Check.__init__(self)
        self.id = 33
        self.version = "0.0.1"

    def _do_check(self, rdp):
        for d in rdp.metadata.dates:
            if d.type == "Issued":
                return MetricResult(d.date.year, "", True)
        return MetricResult(sys.float_info.min, "No IssueDate retrievable", False)

class DatesInformationCheck(Check):
    """ Checks the date information field of the dates of the publication

    Methods
    -------
    _do_check(self, rdp)
        returns a ListResult, indicating the date information fields

    """
    def __init__(self):
        Check.__init__(self)
        self.id = 34
        self.version = "0.0.1"

    def _do_check(self, rdp):
        information = []
        msg = "No dates retrievable"
        for d in rdp.metadata.dates:
            msg = ""
            information.append(d.information)
        return ListResult(information, msg, True)

class RelatedResourceTypeCheck(Check):
    """ Checks the type of related resources to the RDP

    Methods
    -------
    _do_check(self, rdp)
        returns a ListResult of str, indicating the types of relation of the RDP to
        other resources

    """
    def __init__(self):
        Check.__init__(self)
        self.id = 35
        self.version = "0.0.1"

    def _do_check(self, rdp):
        relationTypes = []
        msg = "No related resources retrievable"
        for r in rdp.metadata.relatedResources:
            msg = ""
            relationTypes.append(r.relationType)
        return ListResult(relationTypes, msg, True)

class RelatedResourceMetadataCheck(Check):
    """ Checks if a resource is not of type HasMetadata or if it is,
        it has a resolvable schemeURI and schemeType

    Methods
    -------
    _do_check(self, rdp)
        returns a ListResult of bools, indicating whether metadata are linked properly

    """
    def __init__(self):
        Check.__init__(self)
        self.id = 36
        self.version = "0.0.1"

    def _do_check(self, rdp):
        linkedProperly = []
        msg = "No related resources retrievable"
        for r in rdp.metadata.relatedResources:
            msg = ""
            if r.relationType == "HasMetadata":
                if r.schemeURI is None or r.schemeType is None:
                    linkedProperly.append(False)
                    continue
            linkedProperly.append(True)
        return ListResult(linkedProperly, msg, True)

class DataSizeCheck(Check):
    """ Checks the size of the data set, returns it in bytes

    Methods
    -------
    _do_check(self, rdp)
        returns a ListResult of bools, indicating whether metadata are linked properly

    """
    def __init__(self):
        Check.__init__(self)
        self.id = 37
        self.version = "0.0.1"

    def _do_check(self, rdp):
        factors = {
            "k": 2 ** 10,
            "m": 2 ** 20,
            "g": 2 ** 30,
            "t": 2 ** 40,
            "p": 2 ** 50,
            "e": 2 ** 60,
            "z": 2 ** 70,
            "y": 2 ** 80
        }
        size = 0

        # Try metadata fields
        for s in rdp.metadata.sizes:
            m = re.match(r"(^\d+)\s*(k|m|g|t|p|e|z|y){0,1}i{0,1}b$", s, re.IGNORECASE)
            # groups() allows to set a default value, but the index of the
            # returned tuple is 0-based!
            if m:
                size += int(m.group(1)) * factors.get(m.groups("")[1].lower(), 1)
        if size > 0:
            return MetricResult(size, "Used metadata", True)

        # Try headers
        try:
            for service_name in rdp.services:
                service  = rdp.services.get(service_name)
                if service.can(RetrieveDataHttpHeaders()):
                    for headers in service.get_headers(rdp.pid):
                        size += int(headers["Content-Length"])
                if size > 0:
                    return MetricResult(size, "Used headers", True)
        except ValueError as e:
            return MetricResult(-1, str(e), False)

        return MetricResult(sys.float_info.min, "Could not determine size", False)

def is_valid_orcid(orcid):
    """ returns True when the given str is a valid orcid and the checksum test succeeds
    """
    # Test format
    if not re.match(r"^\d\d\d\d-\d\d\d\d-\d\d\d\d-\d\d\d(\d|X)", orcid):
        return False
    # Test checksum
    total = 0
    digitsRead = 0
    for char in orcid:
        if char == "-":
            continue
        if char == "X":
            digit = 10
        else:
            digit = int(char)
        digitsRead += 1
        if digitsRead <= 15:
            total = (total + digit) * 2
        else:
            checksum = digit
    if ((12 - (total % 11)) %11) != checksum:
        return False
    return True

def has_family_and_given_name(po):
    """ returns True when a Person object has both family and given name
    """
    if isinstance(po.familyName, str) and len(po.familyName) > 0:
        if isinstance(po.givenName, str) and len(po.givenName) > 0:
            return True
    return False

def rights_are_open(ro):
    """ returns True if the given right object is open, i.e. its usage
        not restricted in a way that necessitates interation with the rights
        holder. False otherwise (also if rights object is unknown).
    """
    if ro.spdx is not None and re.match(r"CC-(0|BY-\d\.\d|BY-SA-\d\-\d)", ro.spdx):
        return True
    if ro.uri is not None and \
       re.match(r"https{0,1}://creativecommons.org/(publicdomain.*|licenses/(by|by-sa)/\d\.\d)/{0,1}", ro.uri):
        return True
    return False
