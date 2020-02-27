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

from breadp.rdp.metadata.datacite import DataCiteMetadata
from breadp.rdp.metadata.factory import MetadataFactory
from breadp.rdp.data import CSVData
from breadp.rdp.services import OaipmhService, ZenodoRestService, Service
from breadp.rdp.rdp import RdpFactory, Rdp
from breadp.util.util import Bundle

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

# Checks the functionality of a zenodo RDP
@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_rdp_zenodo(mock_get):
    # "good" example (n fields, some with params) --> artefacts/md001.xml
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    assert rdp.pid == "10.5281/zenodo.3490396"
    assert rdp.metadata.pid == "10.5281/zenodo.3490396"
    assert len(rdp.metadata.descriptions) > 0
    assert len(rdp.metadata.descriptions[0].text) > 15
    assert rdp.metadata.descriptions[0].type == "Abstract"
    assert len(rdp.metadata.titles) == 2
    assert rdp.metadata.titles[0].type is None
    assert rdp.metadata.titles[0].text == "s-sized Training and Evaluation" \
        "  Data for Publication \"Using Supervised Learning to Classify Metadata of" \
        " Research Data by Discipline of Research\""
    assert rdp.metadata.titles[1].type == "TranslatedTitle"
    assert rdp.metadata.titles[1].text == "Irgend ein deutscher Titel mit einem" \
            " Hinweis, wie toll die Publikation ist."
    assert len(rdp.metadata.formats) == 2
    assert rdp.metadata.formats[0] == "application/json"
    assert rdp.metadata.formats[1] == "text/csv"
    assert len(rdp.data) == 2
    assert rdp.metadata.rights[0].text == "Creative Commons Attribution 4.0 International"
    assert rdp.metadata.rights[0].uri == "http://creativecommons.org/licenses/by/4.0/legalcode"
    assert rdp.metadata.rights[0].spdx == "CC-BY-4.0"

    # Test "bad" example (empty fields) --> artefacts/002.xml
    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    assert len(rdp.metadata.descriptions) == 0
    assert len(rdp.metadata.titles) == 0
    assert len(rdp.metadata.formats) == 0
    assert len(rdp.metadata.rights) == 0

    # Test another setup (one field with params) --> artefacts/003.xml
    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    assert len(rdp.metadata.titles) == 1
    assert rdp.metadata.titles[0].text == "survey.csv"
    assert rdp.metadata.titles[0].type == "TranslatedTitle"
    assert len(rdp.metadata.formats) == 1
    assert rdp.metadata.formats[0] == "application/json"
    assert len(rdp.metadata.rights) == 2
    assert rdp.metadata.rights[0].text == "Creative Commons Attribution 4.0 International"
    assert rdp.metadata.rights[0].uri == "http://creativecommons.org/licenses/by/4.0/legalcode"
    assert rdp.metadata.rights[0].spdx == None
    assert rdp.metadata.rights[1].text == "Open Access"
    assert rdp.metadata.rights[1].uri == "info:eu-repo/semantics/openAccess"


    # Test another setup (one field without params) --> artefacts/004.xml
    rdp = RdpFactory.create("10.5281/zenodo.badex3", "zenodo", token="123")
    assert len(rdp.metadata.titles) == 1
    assert rdp.metadata.titles[0].text == "One Title in English, no params"
    assert rdp.metadata.titles[0].type is None

    # Test another setup (n fields none with params) --> artefacts/005.xml
    rdp = RdpFactory.create("10.5281/zenodo.badex4", "zenodo", token="123")
    assert len(rdp.metadata.titles) == 2
    assert rdp.metadata.titles[0].text == "Several titles, none with params"
    assert rdp.metadata.titles[0].type is None
    assert rdp.metadata.titles[1].text == "Einige Titel, keiner mit Parametern"
    assert rdp.metadata.titles[1].type is None

    # Test another setup (n fields all with params) --> artefacts/006.xml
    rdp = RdpFactory.create("10.5281/zenodo.badex5", "zenodo", token="123")
    assert len(rdp.metadata.titles) == 2
    assert rdp.metadata.titles[0].text == "Two titles, one without params"
    assert rdp.metadata.titles[0].type is None
    assert rdp.metadata.titles[1].text == "Und einer mit einem Parameter"
    assert rdp.metadata.titles[1].type == "TranslatedTitle"


