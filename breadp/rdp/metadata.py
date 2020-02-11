################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains all code related to metadata (as a component of RDPs)
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
    pid: str
        Identifier for the RDP
    """
    @property
    def pid(self):
        raise NotImplementedError("pid must be implemented by subclasses of Metadata")
    @property
    def descriptions(self):
        raise NotImplementedError("description must be implemented by subclasses of Metadata")

    def getMainDescription(self):
        raise NotImplementedError("getMainDescription() must be implemented by subclasses of Metadata")

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


class MetadataFactory(object):
    """ Factory for Metadata

    Methods
    ------
    create(md_type, payload) -> Metadata
        Factory method returning a Metadata object appropriate for the given type and payload
    """
    def create(md_type, payload) -> Metadata:
        """ Creates a Metadata object appropriate for the given type and payload

        Parameters
        ----------
        md_type: str
            Type of the Metadata, supported types: oaipmh_datacite
        payload: misc
            Payload to be used to create the Metadata object

        Returns
        -------
        Metadata: The created Metadata object
        """
        if md_type in ("oaipmh_datacite"):
            md = DataCiteMetadata()
            md._initialize(payload)
            md._normalize()
            return md
        return Metadata()

################################################################################
# SPECIFIC METADATA IMPLEMENTATIONS
################################################################################
class DataCiteMetadata(OaiPmhMetadata):
    """ DataCite Metadata Object
    """
    @property
    def pid(self) -> str:
        return self.md["identifier"]["identifier"]
    @property
    def descriptions(self):
        return self.md["descriptions"]["description"]

    def getMainDescription(self):
        for d in self.descriptions:
            if d["@descriptionType"] == "Abstract":
                return d["#text"]
        return None
