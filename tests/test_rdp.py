import os
from unittest import mock

from breadp.rdp.metadata import DataCiteMetadata
from breadp.rdp.data import CSVData
from breadp.rdp.services import OaipmhService
from breadp.rdp.rdp import RdpFactory

#def test_metadata_datacite():
#    # rewrite to not use file
#    md = DataCiteMetadata(source="./tests/artefacts/md001.json", fformat="json")
#    assert md.pid == "10.5072/example-full"

#def test_csv_datum():
#    data = CSVDatum("./tests/artefacts/d001.csv")
#    assert "date" in data.header

def mocked_requests_get(*args, **kwargs):

    class MockResponse:
        def __init__(self, content, status_code):
            self.content = content
            self.status_code = status_code
    import pprint
    pprint.pprint(args)
    if args[0] == "https://zenodo.org/oai2d":
        with open("./tests/artefacts/md001.xml", "rb") as f:
            content = f.read()
        return MockResponse(content, 200)
    return MockResponse(None, 404)

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_service_oaipmh(mock_get):
    oaipmh = OaipmhService("https://zenodo.org/oai2d", "oai:zenodo.org:")
    md = oaipmh.get_record("3490468", "datacite")
    assert md.pid == "10.5281/zenodo.3490396"

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_rdp_1(mock_get):
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo")
    assert rdp.pid == "10.5281/zenodo.3490396"
    assert rdp.metadata.pid == "10.5281/zenodo.3490396"
