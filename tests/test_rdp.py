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

from breadp.rdp.metadata import parseDateString
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

def test_parseDateString():
    with pytest.raises(ValueError) as ve:
        parseDateString("12")
        assert str(ve) == "'12' is not in a supported format"
    with pytest.raises(ValueError) as ve:
        parseDateString("1212/12/12")
        assert str(ve) == "'1212/12/12' is not in a supported format"
    with pytest.raises(ValueError) as ve:
        parseDateString("2013-99")
        assert str(ve) == "'2013-99' is not in a supported format"
    with pytest.raises(ValueError) as ve:
        parseDateString("2013-01-01 20:00")
        assert str(ve) == "'2013-01-01 20:00' is not in a supported format"
    with pytest.raises(ValueError) as ve:
        parseDateString("2013-01-01T20:00")
        assert str(ve) == "'2013-01-01T20:00' is not in a supported format"
    with pytest.raises(ValueError) as ve:
        parseDateString("2013-01-01T20:00+1:00")
        assert str(ve) == "'2013-01-01T20:00+1:00' is not in a supported format"
    dt = parseDateString("2019")
    assert dt.year == 2019
    dt = parseDateString("2019-12")
    assert dt.month == 12
    dt = parseDateString("2019-12-24")
    assert dt.day == 24
    dt = parseDateString("2019-12-24T20:01+0100")
    assert dt.hour == 20
    assert dt.minute == 1
    dt = parseDateString("2019-12-24T20:01+01:00")
    assert dt.hour == 20
    assert dt.minute == 1
    dt = parseDateString("2019-12-24T20:01:01+0100")
    assert dt.second == 1
    dt = parseDateString("2019-12-24T20:01:01+01:00")
    assert dt.second == 1

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
def test_rdp_zenodo_pid(mock_get):
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    assert rdp.pid == "10.5281/zenodo.3490396"
    assert rdp.metadata.pid == "10.5281/zenodo.3490396"

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_rdp_zenodo_description(mock_get):
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    assert len(rdp.metadata.descriptions) > 0
    assert len(rdp.metadata.descriptions[0].text) > 15
    assert rdp.metadata.descriptions[0].type == "Abstract"

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    assert len(rdp.metadata.descriptions) == 0

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_rdp_zenodo_title(mock_get):
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    assert len(rdp.metadata.titles) == 2
    assert rdp.metadata.titles[0].type is None
    assert rdp.metadata.titles[0].text == "s-sized Training and Evaluation" \
        "  Data for Publication \"Using Supervised Learning to Classify Metadata of" \
        " Research Data by Discipline of Research\""
    assert rdp.metadata.titles[1].type == "TranslatedTitle"
    assert rdp.metadata.titles[1].text == "Irgend ein deutscher Titel mit einem" \
            " Hinweis, wie toll die Publikation ist."

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    assert len(rdp.metadata.titles) == 0

    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    assert len(rdp.metadata.titles) == 1
    assert rdp.metadata.titles[0].text == "survey.csv"
    assert rdp.metadata.titles[0].type == "TranslatedTitle"

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

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_rdp_zenodo_formats(mock_get):
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    assert len(rdp.metadata.formats) == 2
    assert rdp.metadata.formats[0] == "application/json"
    assert rdp.metadata.formats[1] == "text/csv"

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    assert len(rdp.metadata.formats) == 0

    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    assert len(rdp.metadata.formats) == 1
    assert rdp.metadata.formats[0] == "application/json"

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_rdp_zenodo_rights(mock_get):
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    assert rdp.metadata.rights[0].text == "Creative Commons Attribution 4.0 International"
    assert rdp.metadata.rights[0].uri == "http://creativecommons.org/licenses/by/4.0/legalcode"
    assert rdp.metadata.rights[0].spdx == "CC-BY-4.0"

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    assert len(rdp.metadata.rights) == 0

    # Test another setup (one field with params) --> artefacts/003.xml
    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    assert len(rdp.metadata.rights) == 3
    assert rdp.metadata.rights[0].text == "Open Access"
    assert rdp.metadata.rights[0].uri == "info:eu-repo/semantics/openAccess"
    assert rdp.metadata.rights[1].text == "Creative Commons Attribution 4.0 International"
    assert rdp.metadata.rights[1].uri == "http://thisurl does not exists"
    assert rdp.metadata.rights[1].spdx == None
    assert len(rdp.metadata.rights) == 3

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_rdp_zenodo_subjects(mock_get):
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    assert len(rdp.metadata.subjects) == 2
    assert rdp.metadata.subjects[0].scheme == "wikidata"
    assert rdp.metadata.subjects[0].uri == "https://www.wikidata.org/wiki/"
    assert rdp.metadata.subjects[0].text == "Q2539"
    assert rdp.metadata.subjects[1].scheme == "dewey"
    assert rdp.metadata.subjects[1].uri == "https://dewey.info/"
    assert rdp.metadata.subjects[1].text == "000 computer science"
    assert len(rdp.metadata.subjects) == 2

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_rdp_zenodo_creators(mock_get):
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    assert len(rdp.metadata.creators) == 2
    assert rdp.metadata.creators[0].name == "Weber, Tobias"
    assert rdp.metadata.creators[0].givenName == "Tobias"
    assert rdp.metadata.creators[0].familyName == "Weber"
    assert rdp.metadata.creators[0].affiliations[0] == "Leibniz Supercomputing Centre"
    assert rdp.metadata.creators[0].orcid == "0000-0003-1815-7041"
    assert rdp.metadata.creators[1].givenName == "Nelson"
    assert rdp.metadata.creators[1].familyName == "Tavares de Sousa"
    assert rdp.metadata.creators[1].affiliations[0] == "Software Engineering Group, Kiel University (Germany)"
    assert rdp.metadata.creators[1].orcid == "0000-0003-1866-7156"

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    assert len(rdp.metadata.creators) == 0

    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    assert rdp.metadata.creators[0].name == "Tobias Weber"
    assert rdp.metadata.creators[0].givenName is None
    assert rdp.metadata.creators[0].familyName is None
    assert rdp.metadata.creators[0].orcid is None

    rdp = RdpFactory.create("10.5281/zenodo.badex3", "zenodo", token="123")
    assert rdp.metadata.creators[1].name == "Leibniz Rechenzentrum"

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_rdp_zenodo_size(mock_get):
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    assert rdp.metadata.sizes[0] == "12000kb"

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    assert len(rdp.metadata.sizes) == 0

    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    assert len(rdp.metadata.sizes) == 2
    assert rdp.metadata.sizes[0] == "120 records"
    assert rdp.metadata.sizes[1] == "12 GB"

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_rdp_zenodo_version(mock_get):
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    assert rdp.metadata.version == "1.0.0"

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    assert rdp.metadata.version is None

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_rdp_zenodo_language(mock_get):
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    assert rdp.metadata.language == "en"

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    assert rdp.metadata.language is None

    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    assert rdp.metadata.language == "bribrabru"

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_rdp_zenodo_contributors(mock_get):
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    assert len(rdp.metadata.contributors) == 2
    assert rdp.metadata.contributors[0].name == "Weber, Tobias"
    assert rdp.metadata.contributors[0].givenName == "Tobias"
    assert rdp.metadata.contributors[0].familyName == "Weber"
    assert rdp.metadata.contributors[0].affiliations[0] == "Leibniz Supercomputing Centre"
    assert rdp.metadata.contributors[0].type == "ContactPerson"
    assert rdp.metadata.contributors[0].orcid == "0000-0003-1815-7041"
    assert rdp.metadata.contributors[1].givenName == "Nelson"
    assert rdp.metadata.contributors[1].familyName == "Tavares de Sousa"
    assert rdp.metadata.contributors[1].affiliations[0] == "Software Engineering Group, Kiel University (Germany)"
    assert rdp.metadata.contributors[1].orcid == "0000-0003-1866-7156"
    assert rdp.metadata.contributors[1].type == "ProjectMember"

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    assert len(rdp.metadata.contributors) == 0

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_rdp_zenodo_publicationYear(mock_get):
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    assert rdp.metadata.publicationYear == 2019

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    assert rdp.metadata.publicationYear == None

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_rdp_zenodo_dates(mock_get):
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    assert len(rdp.metadata.dates) == 2
    assert rdp.metadata.dates[0].type == "Issued"
    assert rdp.metadata.dates[0].date.year == 2019
    assert rdp.metadata.dates[0].date.month == 10
    assert rdp.metadata.dates[0].date.day == 15
    assert rdp.metadata.dates[0].end.year == rdp.metadata.dates[0].date.year
    assert rdp.metadata.dates[0].end.month == rdp.metadata.dates[0].date.month
    assert rdp.metadata.dates[0].end.day == rdp.metadata.dates[0].date.day
    assert rdp.metadata.dates[0].information is None
    assert not rdp.metadata.dates[0].duration
    assert rdp.metadata.dates[1].type == "Created"
    assert rdp.metadata.dates[1].date.year == 2019
    assert rdp.metadata.dates[1].date.month == 3
    assert rdp.metadata.dates[1].date.day == 1
    assert rdp.metadata.dates[1].end.day == 4
    assert rdp.metadata.dates[1].end.hour == 14
    assert rdp.metadata.dates[1].end.second == 13
    assert rdp.metadata.dates[1].duration
    assert rdp.metadata.dates[1].information is None

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    assert len(rdp.metadata.dates) == 0

    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    assert len(rdp.metadata.dates) == 1
    assert rdp.metadata.dates[0].type == None
    assert rdp.metadata.dates[0].date.year == 2019
    assert rdp.metadata.dates[0].date.month == 10
    assert rdp.metadata.dates[0].date.day == 15
    assert rdp.metadata.dates[0].information is None

    rdp = RdpFactory.create("10.5281/zenodo.badex3", "zenodo", token="123")
    assert rdp.metadata.dates[0].type == "Updated"
    assert rdp.metadata.dates[0].information == "First revision"
    assert rdp.metadata.dates[1].type == "Updated"
    assert rdp.metadata.dates[1].information == "Second revision"

    rdp = RdpFactory.create("10.5281/zenodo.badex4", "zenodo", token="123")
    assert rdp.metadata.dates[0].type == "Updated"
    assert rdp.metadata.dates[0].information is None
    assert rdp.metadata.dates[1].type == "Updated"
    assert rdp.metadata.dates[1].information is None

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_rdp_zenodo_data(mock_get):
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    assert len(rdp.data) == 2
