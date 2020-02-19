################################################################################
# Copyright: Tobias Weber 2020
#
# Apache 2.0 License
#
# This file contains all code related to metadata (as a component of RDPs)
#
################################################################################

from collections import OrderedDict

from breadp.rdp.metadata import Description, Title, OaiPmhMetadata

class DataCiteMetadata(OaiPmhMetadata):
    """ DataCite Metadata Object
    """
    def __init__(self):
        self._descriptions = []
        self._titles = []
        self._formats = []

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

