import requests

from breadp.rdp.metadata import MetadataFactory
from breadp.util.util import Bundle
from breadp.util.exceptions import NotCheckeableError

class Service(object):
    def __init__(self, endpoint):
        self.endpoint = endpoint

class ServiceBundle(Bundle):
    def get_metadata(self, identifier, scheme):
        if self.has("oai-pmh"):
            return self.get("oai-pmh").get_record(identifier, scheme)
        else:
            raise NotCheckeableError("No service available to get metadata!")

################################################################################
# SPECIFIC SERVICE IMPLEMENTATIONS
################################################################################
class OaipmhService(Service):
    def __init__(self, endpoint, identifier_prefix=""):
        super(OaipmhService, self).__init__(endpoint)
        self.identifier_prefix = identifier_prefix

    def get_record(self, identifier, metadataPrefix):
        params = {
            'verb': 'GetRecord',
            'metadataPrefix': metadataPrefix,
            'identifier': "{}{}".format(self.identifier_prefix, identifier)
        }
        r = requests.get(self.endpoint, params)
        return MetadataFactory.create(metadataPrefix, r.content)
