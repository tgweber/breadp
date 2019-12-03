from breadp.util.util import Bundle
from breadp.rdp.services import ServiceBundle, OaipmhService
from breadp.rdp.metadata import MetadataBundle

class RdpFactory(object):
    def create(pid, rdp_type=None):
        if rdp_type == "zenodo":
            return ZenodoRdp(pid)
        else:
            return Rdp(pid)

class Rdp(object):
    def __init__(self, pid):
        self.pid = pid
        self._data = Bundle()
        self._metadata = MetadataBundle()
        self._services = ServiceBundle()

class ZenodoRdp(Rdp):
    def __init__(self, pid):
       super(ZenodoRdp, self).__init__(pid)
       self.zenodo_id = self.pid.split(".")[-1]
       self._services.put("oai-pmh", OaipmhService("https://zenodo.org/oai2d", "oai:zenodo.org:"))

    @property
    def metadata(self):
        if not self._metadata.has("datacite"):
           self._metadata.put("datacite", self._services.get_metadata(self.zenodo_id, "datacite"))
        return self._metadata.get("datacite")

    @property
    def data(self):
        raise NotImplementedError("Data access to ZenodoRdp is not implemented")
