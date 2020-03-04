################################################################################
# Copyright: Tobias Weber 2020
#
# Apache 2.0 License
#
# This file contains all code related to metadata (as a component of RDPs)
#
################################################################################

from collections import OrderedDict

from breadp.rdp.metadata import \
    Description, \
    Rights, \
    Subject, \
    Title, \
    OaiPmhMetadata

class DataCiteMetadata(OaiPmhMetadata):
    """ DataCite Metadata Object
    """
    def __init__(self):
        self._descriptions = []
        self._titles = []
        self._formats = []
        self._rights = []
        self._subjects = []

    @property
    def pid(self) -> str:
        return self.md["identifier"]["identifier"]

    @property
    def descriptions(self):
        if len(self._descriptions) == 0 and "descriptions" in self.md.keys():
            if not isinstance(self.md["descriptions"], dict):
                return self._descriptions
            if isinstance(self.md["descriptions"]["description"],str):
                self._descriptions.append(Description(self.md["descriptions"]["description"]))
                return self._descriptions
            if isinstance(self.md["descriptions"]["description"],OrderedDict):
                self._descriptions.append(Title(
                    self.md["descriptions"]["description"]["description"],
                    self.md["descriptions"]["description"].get("@descriptionType"))
                )
                return self._descriptions
            for d in self.md["descriptions"].get("description", []):
                if isinstance(d, OrderedDict):
                    self._descriptions.append(Description(
                        d["#text"],
                        d.get("@descriptionType", None))
                    )
                else:
                    self._descriptions.append(Description(d))
        return self._descriptions

    @property
    def titles(self):
        if len(self._titles) == 0 and "titles" in self.md.keys():
            if not isinstance(self.md["titles"], dict):
                return self._titles
            if isinstance(self.md["titles"]["title"],str):
                self._titles.append(Title(self.md["titles"]["title"]))
                return self._titles
            if isinstance(self.md["titles"]["title"],OrderedDict):
                self._titles.append(Title(
                    self.md["titles"]["title"]["title"],
                    self.md["titles"]["title"].get("@titleType"))
                )
                return self._titles
            for t in self.md["titles"].get("title", []):
                if isinstance(t, OrderedDict):
                    self._titles.append(Title(
                        t["#text"],
                        t.get("@titleType", None))
                    )
                else:
                    self._titles.append(Title(t))
        return self._titles

    @property
    def formats(self):
        if len(self._formats) == 0 and "formats" in self.md.keys():
            if isinstance(self.md["formats"]["format"], list):
                self._formats = self.md["formats"]["format"]
            else:
                self._formats.append(self.md["formats"]["format"])
        return self._formats

    @property
    def rights(self):
        if len(self._rights) == 0 and "rightsList" in self.md.keys() and \
            self.md["rightsList"] is not None:
            if isinstance(self.md["rightsList"].get("rights", None), OrderedDict):
                self._rights.append(
                    createRightsObjectFromOrderedDict(self.md["rightsList"]["rights"])
                )
            elif isinstance(self.md["rightsList"].get("rights", None), list):
                for r in self.md["rightsList"]["rights"]:
                    r["rights"] = r.get("#text", "")
                    self._rights.append(createRightsObjectFromOrderedDict(r))
        return self._rights

    @property
    def subjects(self):
        if len(self._subjects) == 0 \
           and "subjects" in self.md.keys() \
           and isinstance(self.md["subjects"], dict):
            if isinstance(self.md["subjects"].get("subject", None), OrderedDict):
                self._subjects.append(
                    createSubjectObjectFromOrderedDict(self.md["subjects"]["subject"])
                )
            elif isinstance(self.md["subjects"].get("subject", None), list):
                for s in self.md["subjects"]["subject"]:
                    if isinstance(s, str):
                        s = { "#text": s}
                    s["subject"] = s.get("#text", "")
                    self._subjects.append(
                        createSubjectObjectFromOrderedDict(s)
                    )
        return self._subjects

def createRightsObjectFromOrderedDict(r):
    ro = Rights(r.get("rights", ""), r.get("@rightsURI", None))
    if r.get("@schemeURI", "").startswith("https://spdx.org/licenses") \
        or r.get("@rightsIdentifierScheme", "").lower() == "spdx":
        ro.spdx = r.get("@rightsIdentifier", None)
    return ro

def createSubjectObjectFromOrderedDict(s):
    return Subject(
        s.get("subject", ""),
        s.get("@subjectScheme", ""),
        s.get("@schemeURI", "")
    )
