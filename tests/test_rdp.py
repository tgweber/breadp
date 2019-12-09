################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains all RDP-related tests
#
################################################################################

import os

from unittest import mock
import pytest

from breadp.rdp.metadata import DataCiteMetadata, MetadataFactory
from breadp.rdp.data import CSVData
from breadp.rdp.services import OaipmhService, ZenodoRestService, Service
from breadp.rdp.rdp import RdpFactory, Rdp
from breadp.util.util import Bundle
from breadp.util.exceptions import NotCheckeableError

from util import mocked_requests_get
# Checks that all exceptions in metadata are thrown appropiately
def test_metadata_exceptions():
    with pytest.raises(NotImplementedError):
       md = MetadataFactory.create("some_type", "<tag></tag>")
       assert md.pid() == "123"

def test_services_exceptions():
    with pytest.raises(NotImplementedError):
        s = Service("http://www.example.com")
        assert s.protocol== "some_protocol"

# Checks implemented functionality of the oai-pmh service
@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_service_oaipmh(mock_get):
    oaipmh = OaipmhService("https://zenodo.org/oai2d", "oai:zenodo.org:")
    md = oaipmh.get_record("3490396", "datacite")
    assert md.pid == "10.5281/zenodo.3490396"

# Checks implemented functionality of the rest-zenodo service
@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_service_rest_zenodo(mock_get):
    rest = ZenodoRestService("https://zenodo.org/api/deposit/depositions", "123")
    data_bundle = Bundle()
    for f in rest.get_files("3490396"):
        data_bundle.put(f.source, f)
    assert len(data_bundle) == 2
    first = data_bundle.get("https://zenodo.org/api/files/abc/s_data_vectorized.csv")
    assert first.type == "text/csv"
    assert first.encoding == None
    assert "date" in first.header
    second = data_bundle.get("https://zenodo.org/api/files/abcd/s_data_vectorized.tar.gz")
    assert second.type == "application/x-tar"
    assert second.encoding == "gzip"
    assert "date" in first.rows[0].keys()

# Checks the functionality of an unspecified RDP
def test_rdp_unspecified():
    rdp = RdpFactory.create("some_id", "some_type")
    assert type(rdp) == Rdp
    with pytest.raises(NotCheckeableError):
        rdp.metadata.pid == "some_id"
    with pytest.raises(NotCheckeableError):
        len(rdp.data) == 2

# Checks the functionality of a zenodo RDP
@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_rdp_zenodo(mock_get):
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    assert rdp.pid == "10.5281/zenodo.3490396"
    assert rdp.metadata.pid == "10.5281/zenodo.3490396"
    assert len(rdp.data) == 2
