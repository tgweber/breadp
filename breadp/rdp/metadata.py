import json
from collections import OrderedDict
import xmltodict

from breadp.util.exceptions import NotCheckeableError
from breadp.util.util import Bundle

class MetadataFactory(object):
    def create(scheme, payload):
        if scheme == "datacite":
            return DataCiteMetadata(oaipmh=payload)
        else:
            raise NotCheckeableError("Scheme %s is not supported".format(scheme))

class MetadataBundle(Bundle):
    @property
    def pid(self):
        if self.has("datacite"):
            return self.get("datacite").pid()
        else:
            raise NotCheckeableError("No metadata object that supports PID retrieval")

################################################################################
# SPECIFIC METADATA IMPLEMENTATIONS
################################################################################

class DataCiteMetadata(object):
    def __init__(self, **kwargs):
        if "oaipmh" in kwargs:
            oaipmh = xmltodict.parse(kwargs["oaipmh"])
            self.md = oaipmh["OAI-PMH"]["GetRecord"]["record"]["metadata"]["resource"]
            self.normalize_metadata()

    def normalize_metadata(self, md=None):
        if not md:
            md = self.md
        for key in md.keys():
            if type(md[key]) == OrderedDict:
                if '#text'in md[key].keys():
                    md[key][key] = md[key]['#text']
                    del md[key]['#text']
                self.normalize_metadata(md[key])

    @property
    def pid(self):
        return self.md["identifier"]["identifier"]
