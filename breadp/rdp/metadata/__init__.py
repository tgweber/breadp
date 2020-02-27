################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains all generic code related to metadata as a component of RDPs
#
################################################################################

import json
from collections import OrderedDict
import xmltodict

from breadp.util.util import Bundle

class Metadata(object):
    """ Base class and interface for Metadata as components of RDPs

    Attributes
    ----------
    descriptions: list<Description>
        Descriptions of the RDP
    pid: str
        Identifier for the RDP
    titles: list<Title>
        Titles of the RDP
    """
    @property
    def descriptions(self):
        raise NotImplementedError("Must be implemented by subclasses of Metadata.")
    @property
    def pid(self):
        raise NotImplementedError("Must be implemented by subclasses of Metadata.")
    @property
    def titles(self):
        raise NotImplementedError("Must be implemented by subclasses of Metadata.")
    @property
    def formats(self):
        raise NotImplementedError("Must be implemented by subclasses of Metadata.")
    @property
    def rightss(self):
        raise NotImplementedError("Must be implemented by subclasses of Metadata.")

class Description(object):
    """ Base class and interface for descriptions as a metadata field of RDPs

    Attributes
    ----------
    text: str
        The text of the description
    type: str
        The type of the description, might be None
    """
    def __init__(self, text, dtype=None):
        self.text = text
        self.type = dtype

class Title(object):
    """ Base class and interface for titles as a metadata field of RDPs

    Attributes
    ----------
    text: str
        The text of the title
    type: str
        The type of the title, might be None
    """
    def __init__(self, text, ttype=None):
        self.text = text
        self.type = ttype

class Rights(object):
    """ Base class and interface of rights/licenses as part of metadata of RDPs

    Attributes
    ----------
    text: str
        The text field of the license/rights information
    uri: str
        URI poiniting to the text of the license/rights information
    spdx: str
        SPDX identifier as specified on https://spdx.org/licenses/
    """
    def __init__(self, text, uri=None, spdx=None):
        self.text = text
        self.uri = uri
        self.spdx = spdx

class OaiPmhMetadata(Metadata):
    """ Base class and interface for all OAI-PMH-based Metadata objects
    """

    def _initialize(self, oaipmh):
        """ Initializes the md attribute from an XML-encoded OAI-PMH response

        Parameters
        ----------
        oaipmh: str
            XML-encoded OAI-PMH response
        """
        oaipmh = xmltodict.parse(oaipmh)
        self.md = oaipmh["OAI-PMH"]["GetRecord"]["record"]["metadata"]["resource"]

    def _normalize(self, md=None) -> None:
        """ Normalizes the metadata (recursively)

        Parameters
        ----------
        md: dict, optional
            Metadata to be normalized. If empty, the md attribute of the object will be used.
        """
        if not md:
            md = self.md
        for key in md.keys():
            if type(md[key]) == OrderedDict:
                if '#text'in md[key].keys():
                    md[key][key] = md[key]['#text']
                    del md[key]['#text']
                self._normalize(md[key])
