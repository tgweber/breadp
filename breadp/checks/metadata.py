################################################################################
# Copyright: Tobias Weber 2020
#
# Apache 2.0 License
#
# This file contains all code related for metadata checks
#
################################################################################
from langdetect import detect

from breadp.checks import Check
from breadp.checks.result import CategoricalResult, \
        ListResult, \
        MetricResult

class DescriptionsNumberCheck(Check):
    """ Checks the number of description for an RDP

    Methods
    -------
    _do_check(self, rdp)
        returns a MetricResult
    """
    def __init__(self):
        super(DescriptionsNumberCheck, self).__init__()
        self.id = 2
        self.version = "0.0.1"
        self.desc = "checks how many descriptions are part of the metadata of the RDP"

    def _do_check(self, rdp):
        return("success", MetricResult(len(rdp.metadata.descriptions), ""), "")

class MainDescriptionLengthCheck(Check):
    """ Checks the length of the main description

    Methods
    -------
    _do_check(self, rdp)
        returns a MetricResult
    """
    def __init__(self):
        super(MainDescriptionLengthCheck, self).__init__()
        self.id = 3
        self.version = "0.0.1"
        self.desc = "checks how long the main description"

    def _do_check(self, rdp):
        md = rdp.metadata.getMainDescription()
        if md is None:
            msg = "No main description was identifyable"
            return("failure", MetricResult(float("nan"), msg), msg)
        return("success",
               MetricResult(len(rdp.metadata.getMainDescription().split()), ""),
               "")

class MainDescriptionLanguageCheck(Check):
    """ Checks the language of the main description

    Methods
    -------
    _do_check(self, rdp)
        returns a CategoricalResult (ISO-639-1 code)
    """
    def __init__(self):
        super(MainDescriptionLanguageCheck, self).__init__()
        self.id = 4
        self.version = "0.0.1"
        self.desc = "checks the language of the main descriptions"

    def _do_check(self, rdp):
        md = rdp.metadata.getMainDescription()
        if md is None:
            msg = "No main description was identifyable"
            return("failure", CategoricalResult("", msg), msg)
        return("success", CategoricalResult(detect(md), ""), "")

class DataCiteDescriptionsTypeCheck(Check):
    """ Checks all description types of DataCite metadata

    Methods
    -------
    _do_check(self, rdp)
        returns a ListResult (for each description the type of the description,
        as specified in the DataCite standard)
    """
    def __init__(self):
        super(DataCiteDescriptionsTypeCheck, self).__init__()
        self.id = 5
        self.version = "0.0.1"
        self.desc = "checks the types of the descriptions"

    def _do_check(self, rdp):
        types = []
        for d in rdp.metadata.descriptions:
            types.append(d["@descriptionType"])
        return ("success", ListResult(types, ""), "")
