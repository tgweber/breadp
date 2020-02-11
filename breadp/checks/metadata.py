################################################################################
# Copyright: Tobias Weber 2020
#
# Apache 2.0 License
#
# This file contains all code related for metadata checks
#
################################################################################
from langdetect import detect
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

class MainDescriptionLengthCheck(Check):
    """ Checks the length of the main description in words

    Methods
    -------
    _do_check(self, rdp)
        returns a MetricResult
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 3
        self.version = "0.0.1"
        self.desc = "checks how long the main description"

    def _do_check(self, rdp):
        md = rdp.metadata.getMainDescription()
        if md is None:
            msg = "No main description was identifyable"
            return(False, MetricResult(float("nan"), msg))
        return(True, MetricResult(len(rdp.metadata.getMainDescription().split()), ""))

class MainDescriptionLanguageCheck(Check):
    """ Checks the language of the main description

    Methods
    -------
    _do_check(self, rdp)
        returns a CategoricalResult (ISO-639-1 code)
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 4
        self.version = "0.0.1"
        self.desc = "checks the language of the main description"

    def _do_check(self, rdp):
        md = rdp.metadata.getMainDescription()
        if md is None:
            msg = "No main description was identifyable"
            return(True, CategoricalResult("", msg))
        return(True, CategoricalResult(detect(md), ""))

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
        for d in rdp.metadata.descriptions:
            types.append(d["@descriptionType"])
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

class MainTitleLengthCheck(Check):
    """ Checks the length of the main title in words

    Methods
    -------
    _do_check(self, rdp)
        returns a MetricResult
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 7
        self.version = "0.0.1"
        self.desc = "checks how many words the main title has"

    def _do_check(self, rdp):
        mt = rdp.metadata.getMainTitle()
        if mt is None:
            msg = "No main title was identifyable"
            return(True, MetricResult(float("nan"), msg))
        return(True, MetricResult(len(rdp.metadata.getMainTitle().split()), ""))

class MainTitleLanguageCheck(Check):
    """ Checks the language of the main title

    Methods
    -------
    _do_check(self, rdp)
        returns a CategoricalResult (ISO-639-1 code)
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 8
        self.version = "0.0.1"
        self.desc = "checks the language of the main title"

    def _do_check(self, rdp):
        mt = rdp.metadata.getMainTitle()
        if mt is None:
            msg = "No main title was identifyable"
            return(True, CategoricalResult("", msg))
        return(True, CategoricalResult(detect(mt), ""))

class MainTitleProbablyJustAFileNameCheck(Check):
    """ Checks whether the main title is (probably) just a file name

    Methods
    -------
    _do_check(self, rdp)
        returns a BooleanResult
    """
    def __init__(self):
        Check.__init__(self)
        self.id = 9
        self.version = "0.0.1"
        self.desc = "checks whether the main title is probably just a file name"

    def _do_check(self, rdp):
        mt = rdp.metadata.getMainTitle()
        if mt is None:
            msg = "No main title was identifyable"
            return(True, BooleanResult(False, msg))
        if re.match("^\s*\S+\.\S+\s*$", mt):
            msg = "{} is probably just a file name".format(mt)
            return(True, BooleanResult(True, msg))
        return (True, BooleanResult(False, ""))
