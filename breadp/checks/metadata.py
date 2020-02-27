################################################################################
# Copyright: Tobias Weber 2020
#
# Apache 2.0 License
#
# This file contains all code related for metadata checks
#
################################################################################
import json
from langdetect import detect
import os
import pandas as pd
import re

from breadp.checks import Check
from breadp.checks.result import BooleanResult, \
        CategoricalResult, \
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
        self.desc = "checks how many descriptions are part of the metadata of the RDP"

    def _do_check(self, rdp):
        return(True, MetricResult(len(rdp.metadata.descriptions), ""))

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
        self.desc = "checks how many words are in each description"

    def _do_check(self, rdp):
        lengths = []
        success = False
        msg = "No descriptions retrievable"
        for d in rdp.metadata.descriptions:
            success = True
            msg = ""
            lengths.append(len(d.text.split()))
        return(success, ListResult(lengths, msg))

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
        self.desc = "checks the language of the descriptions"

    def _do_check(self, rdp):
        languages = []
        success = False
        msg = "No descriptions retrievable"
        for d in rdp.metadata.descriptions:
            success = True
            msg = ""
            languages.append(detect(d.text))
        return(success, ListResult(languages, msg))

class DataCiteDescriptionsTypeCheck(Check):
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
        self.desc = "checks the types of the descriptions"

    def _do_check(self, rdp):
        types = []
        if len(rdp.metadata.descriptions) == 0:
            return(False, ListResult(types, "No descriptions retrievable"))
        for d in rdp.metadata.descriptions:
            if d.type:
                types.append(d.type)
        return (True, ListResult(types, ""))

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
        self.desc = "checks how many titles are part of the metadata of the RDP"

    def _do_check(self, rdp):
        if not rdp.metadata.titles:
            msg = "No titles could be retrieved"
            return(False, MetricResult(float(0), msg))
        return(True, MetricResult(len(rdp.metadata.titles), ""))

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
        self.desc = "checks how many words the main title has"

    def _do_check(self, rdp):
        lengths = []
        success = False
        msg = "No titles retrievable"
        for t in rdp.metadata.titles:
            success = True
            msg = ""
            lengths.append(len(t.text.split()))
        return(success, ListResult(lengths, msg))

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
        self.desc = "checks the language of the main title"

    def _do_check(self, rdp):
        languages = []
        success = False
        msg = "No titles retrievable"
        for t in rdp.metadata.titles:
            success = True
            msg = ""
            languages.append(detect(t.text))
        return(success, ListResult(languages, msg))

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
        self.desc = "checks whether the main title is probably just a file name"

    def _do_check(self, rdp):
        bools = []
        success = False
        msg = ""
        if len(rdp.metadata.titles) == 0:
            msg = "No titles retrievable"
        for t in rdp.metadata.titles:
            success = True
            msg = ""
            if re.match("^\s*\S+\.\S+\s*$", t.text):
                msg += "{} is probably just a file name;".format(t.text)
                bools.append(True)
            else:
                bools.append(False)
        return(success, ListResult(bools, msg))

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
        self.desc = "checks what types the titles have"

    def _do_check(self, rdp):
        types = []
        success = False
        msg = "No titles retrievable"
        for t in rdp.metadata.titles:
            success = True
            msg = ""
            types.append(t.type)
        return(success, ListResult(types, msg))

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
        self.desc = "checks if all formats are valid IANA media types"

    def _do_check(self, rdp):
        valid = []
        iana_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'mediatypes.csv'
        )
        iana = pd.read_csv(iana_file_path)
        msg = "No formats found!"
        for f in rdp.metadata.formats:
            msg = ""
            if f not in iana.Template.tolist():
                msg += "{} is not a valid format ".format(f)
                valid.append(False)
            else:
                valid.append(True)
        return(True, ListResult(valid, msg))

class RightsHaveValidSPDXIdentifier(Check):
    """ CHecks wheter all rights have valid SPDX licenses identifiers
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
        self.desc = "checks whether rights have valid SPDX identifiers"

    def _do_check(self, rdp):
        valid = []
        spdx_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'licenses.json'
        )
        with open(spdx_file_path, "r") as f:
            licenses_dict = json.load(f)
        licenses = pd.DataFrame(licenses_dict["licenses"])
        msg = "No rights objects found!"
        for r in rdp.metadata.rights:
            msg = ""
            if r.spdx not in licenses.licenseId.tolist():
                msg += "{} is not a valid SPDX identifier".format(r.spdx)
                valid.append(False)
            else:
                valid.append(True)
        return(True, ListResult(valid, msg))
