################################################################################
# Copyright: Tobias Weber 2020
#
# Apache 2.0 License
#
# This file contains all code related for metadata checks
#
################################################################################
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

class FormatsContainValidMediaTypeCheck(Check):
    """ Checks the formats whether some of them are valid IANA MediaTypes
        Canonical source: https://www.iana.org/assignments/media-types/media-types.xhtml
        Retrieved 2020-02-19 for this version

    Methods
    -------
    _do_check(self, rdp)
        returns a BooleanResult (indicating the existence of valid media types)
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 11
        self.version = "0.0.1"
        self.desc = "checks if valid IANA media types are part of the formats"

    def _do_check(self, rdp):
        iana_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mediatypes.csv')
        iana = pd.read_csv(iana_file_path)
        for isin in iana.Template.isin(rdp.metadata.formats):
            if isin:
                return(True, BooleanResult(True, ""))
        return(True, BooleanResult(False, "No valid media types found"))

class FormatsAreValidMediaTypeCheck(Check):
    """ Checks whether all formats are valid IANA MediaTypes
        Canonical source: https://www.iana.org/assignments/media-types/media-types.xhtml
        Retrieved 2020-02-19 for this version
    Methods
    -------
    _do_check(self, rdp)
        returns a BooleanResult (indicating the existence of valid media types)
    """

    def __init__(self):
        Check.__init__(self)
        self.id = 12
        self.version = "0.0.1"
        self.desc = "checks if all formats are valid IANA media types"

    def _do_check(self, rdp):
        iana_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mediatypes.csv')
        iana = pd.read_csv(iana_file_path)
        if len(rdp.metadata.formats) < 1:
            return(True, BooleanResult(False, "No formates found!"))
        for f in rdp.metadata.formats:
            if f not in iana.Template.tolist():
                return(True, BooleanResult(False, "{} is not a valid format".format(f)))
        return(True, BooleanResult(True, ""))
