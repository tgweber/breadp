################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains all code related to services (as a component of RDPs)
#
################################################################################
import requests
from typing import Generator

from breadp.rdp.metadata.factory import MetadataFactory, Metadata
from breadp.rdp.data import DataFactory, Data
from breadp.util import Bundle

class Service(object):
    """ Base class + interface for Services as a component of RDPS

    Parameters
    ----------
    endpoint: str
        URL indicating the endpoint of the service

    Attributes
    ----------
    endpoint: str
    protocol: str
        Name of the protocol used by this service
    See parameters
    """
    def __init__(self, endpoint):
        self.endpoint = endpoint

    @property
    def protocol(self):
        raise NotImplementedError("Protocol must be implemented by all subclasses of Services")

class ServiceBundle(Bundle):
    """ Collection of services with methods to select a service best fit for a task
    """

    def get_metadata(self, identifier, scheme) -> Metadata:
        """ Get a metadata object for the RDP

        Parameters
        ----------
        identifier: str
            Identifier to be used in the service request
        scheme: str
            Scheme of the metadata to-be-requested

        Returns
        -------
        Metadata
            Metadata object for RDP in format specified by scheme
        """

        for key, service in self.payload.items():
            if service.protocol == "oai-pmh":
                return service.get_record(identifier, scheme)
        return None

    def get_data(self, identifier) -> Generator[Data, None, None]:
        """ Get all data objects for the RDP

        Parameters
        ----------
        identifier: str
            Identifier to be used in the service request

        Yields
        ------
        Data
            Data objects for an RDP
        """
        for key, service in self.payload.items():
            if service.protocol == "zenodo-rest":
                return service.get_files(identifier)
        return None

################################################################################
# SPECIFIC SERVICE IMPLEMENTATIONS
################################################################################
class OaipmhService(Service):
    """ OAI-PMH service for an RDP

    Parameters
    ----------
    endpoint: str
        URL indicating the endpoint of the service
    identifierPrefix: str, optional
        Prefix which will always be prepended to the identifier in OAI-PMH requests.
        Default value is the empty string.

    Methods
    -------
    get_record(identifier, metadataPrefix="datacite")
        OAI-PMH GetRecord request to retrieve metadata for the RDP in format
        specified by metadataPrefix
    """
    def __init__(self, endpoint, identifierPrefix=""):
        super(OaipmhService, self).__init__(endpoint)
        self.identifierPrefix = identifierPrefix

    @property
    def protocol(self):
        return "oai-pmh"

    def get_record(self, identifier, metadataPrefix="datacite") -> Metadata:
        """ OAI-PMH GetRecord request to retrieve metadata for the RDP in format
            specified by metadataPrefix

        Parameters
        ----------
        identifier: str
            Identifier to request the record corresponding to the RDP
        metadataPrefix: str, optional
            Format of the metadata record
        """
        params = {
            'verb': 'GetRecord',
            'metadataPrefix': metadataPrefix,
            'identifier': "{}{}".format(self.identifierPrefix, identifier)
        }
        r = requests.get(self.endpoint, params)
        md_type = "oaipmh_{}".format(metadataPrefix)
        return MetadataFactory.create(md_type, r.content)

class ZenodoRestService(Service):
    """ Zenodo Rest API service for an RDP

    Parameters
    ---------
    endpoint: str
        URL indicating the endpoint of the service
    token: str
        Token to authenticate the client against the zenodo API

    Methods
    -------
    get_files(zenodo_Id) -> Generator[Data, None, None]
        Yields all Data objects of the RDP retrievable by the zenodo API
    """
    def __init__(self, endpoint, token):
        super(ZenodoRestService, self).__init__(endpoint)
        self.token = token

    @property
    def protocol(self):
        return "zenodo-rest"

    def get_files(self, zenodoId) -> Generator[Data, None, None]:
        """ Yields all Data objects of the RDP retrievable by the zenodo API

        Parameters
        ----------
        zenodoId: str
            Id used by zenodo to identify depositions

        Yields
        ------
        Data
            Data objects for an RDP
        """
        params = {
            'access_token': self.token
        }
        r = requests.get("{}/{}/files".format(self.endpoint, zenodoId), params)
        for data_item in r.json():
            yield DataFactory.create(data_item["links"]["download"])
