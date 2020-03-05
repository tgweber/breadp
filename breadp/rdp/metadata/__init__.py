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
    formats: list<str>
        Formats of the RDP
    rights: list<Rights>
        Legal information about the RDP
    subjects: list<Subject>
        Keywords describing the RDP
    creators: list<Person>
        Creators of the RDP
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
    def rights(self):
        raise NotImplementedError("Must be implemented by subclasses of Metadata.")
    @property
    def subjects(self):
        raise NotImplementedError("Must be implemented by subclasses of Metadata.")
    @property
    def creators(self):
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

class Subject(object):
    """ Base class and interface for subjects as part of metadata of RDPs

    Attributes
    ----------
    text: str
        The payload of the subject
    scheme: str
        The name of the scheme of the subjects (not controlled)
    uri: str
        The uri to the scheme of the subject
    """
    def __init__(self, text, scheme=None, uri=None):
        self.text = text
        self.scheme = scheme
        self.uri = uri

class PersonOrInstitution(object):
    """ Base class and interface for objects that could be listed as either
        persons or institutions

    Attributes
    ----------
    name: str
        Name of the person/institution
    """
    def __init__(self, name, person=True):
        self.name = name
        self.person = person

    def __getattr__(self, name):
        return None

class Person(PersonOrInstitution):
    """ Base class and interface for persons as part of metadata of RDPs

    Attributes
    ----------
    name: str
        Name of the person
    givenName: str
        Given name of the person
    familiyName: str
        Familiy name of the person
    affiliation: str
        Affiliation of the person
    orcid: str
        ORCiD of the person
    """
    def __init__(self, name, affiliation=None, orcid=None):
        PersonOrInstitution.__init__(self, name, True)
        self.name = name
        if ", " in self.name:
            self.givenName = self.name.split(", ")[1]
            self.familyName = self.name.split(", ")[0]
        else:
            self.givenName = None
            self.familyName = None
        self.affiliations = [affiliation]
        self.orcid = orcid

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
