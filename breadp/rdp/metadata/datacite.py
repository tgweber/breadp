################################################################################
# Copyright: Tobias Weber 2020
#
# Apache 2.0 License
#
# This file contains all code related to metadata (as a component of RDPs)
#
################################################################################

from collections import OrderedDict
import re

from breadp.rdp.metadata import \
    Date, \
    Description, \
    OaiPmhMetadata, \
    Person, \
    PersonOrInstitution, \
    Rights, \
    Subject, \
    Title

class DataCiteMetadata(OaiPmhMetadata):
    """ DataCite Metadata Object
    """
    def __init__(self):
        self._creators = []
        self._descriptions = []
        self._formats = []
        self._rights = []
        self._sizes = []
        self._subjects = []
        self._titles = []
        self._language = None
        self._version = None
        self._publicationYear = None
        self._contributors = []
        self._dates = []

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

    @property
    def creators(self):
        if len(self._creators) == 0 and "creators" in self.md.keys() \
           and isinstance(self.md["creators"], OrderedDict):
            if isinstance(self.md["creators"].get("creator", None), OrderedDict):
                self._creators.append(
                    createPersonOrInstitutionObjectFromOrderedDict(self.md["creators"]["creator"])
                )
            elif isinstance(self.md["creators"].get("creator", None), list):
                for p in self.md["creators"]["creator"]:
                    if isinstance(p, OrderedDict):
                        self._creators.append(
                            createPersonOrInstitutionObjectFromOrderedDict(p)
                        )
        return self._creators

    @property
    def contributors(self):
        if len(self._contributors) == 0 and "contributors" in self.md.keys() \
           and isinstance(self.md["contributors"], OrderedDict):
            if isinstance(self.md["contributors"].get("contributor", None), OrderedDict):
                self._contributors.append(
                    createPersonOrInstitutionObjectFromOrderedDict(
                        self.md["contributors"]["contributor"]
                    )
                )
            elif isinstance(self.md["contributors"].get("contributor", None), list):
                for p in self.md["contributors"]["contributor"]:
                    if isinstance(p, OrderedDict):
                        self._contributors.append(
                            createPersonOrInstitutionObjectFromOrderedDict(p)
                        )
        return self._contributors

    @property
    def sizes(self):
        if len(self._sizes) == 0 and "sizes" in self.md.keys() \
           and isinstance(self.md["sizes"], OrderedDict):
            if isinstance(self.md["sizes"].get("size", None), str):
                self._sizes = [self.md["sizes"]["size"]]
            if isinstance(self.md["sizes"].get("size", None), list):
                for s in self.md["sizes"]["size"]:
                    self._sizes.append(s)
        return self._sizes

    @property
    def language(self):
        if self._language is None:
            self._language = self.md.get("language")
        return self._language

    @property
    def version(self):
        if self._version is None:
            self._version = self.md.get("version")
        return self._version

    @property
    def publicationYear(self):
        if self._publicationYear is None:
            if self.md.get("publicationYear") is not None:
                self._publicationYear = int(self.md["publicationYear"])
        return self._publicationYear

    @property
    def dates(self):
        if len(self._dates) == 0 and isinstance(self.md["dates"], OrderedDict) \
          and "date" in self.md["dates"].keys():
            dateField = self.md["dates"]["date"]
            if dateField is None:
                return None
            if not isinstance(dateField, list):
                dateField = [ dateField ]
            for d in dateField:
                if isinstance(d, str):
                    self._dates.append((Date(d)))
                if isinstance(d, OrderedDict):
                    if d.get("date") is None:
                        d["date"] = d["#text"]
                    self._dates.append(
                        Date(
                            d["date"],
                            d.get("@dateType"),
                            d.get("@dateInformation")
                        )
                    )
        return self._dates


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

def createPersonOrInstitutionObjectFromOrderedDict(p):
    nameField = p.get("creatorName", p.get("contributorName", None))
    if isinstance(nameField, OrderedDict):
        if nameField.get("@nameType", None) == "Organizational":
            return PersonOrInstitution(nameField["#text"], False)
        # after this p is considered to be a person
        else:
            name = nameField.get("#text",
                 nameField.get("creatorName",
                     nameField.get("contributorName")
                  )
            )
    else:
        name = nameField

    po = Person(name)
    affiliations = p.get("affiliation", None)
    if isinstance(affiliations, str):
        affiliations = [affiliations]
    po.affiliations = affiliations
    po.type = p.get("@contributorType", None)


    if po.familyName is None:
        po.familyName = p.get("familyName")
    if po.givenName is None:
        po.givenName = p.get("givenName")
    if isinstance(p.get("nameIdentifier", None), OrderedDict):
        p["nameIdentifier"] = [p["nameIdentifier"]]

    for ni in p.get("nameIdentifier", []):
        if isinstance(ni, OrderedDict):
            if isinstance(ni.get("nameIdentifier", None), str):
                ni["#text"] = ni["nameIdentifier"]
            if re.match("^orcid$", ni.get("@nameIdentifierScheme", ""), re.IGNORECASE) \
               or ni.get("@schemeURI", "").startswith("https://orcid.org"):
                po.orcid = ni["#text"]
    return po
