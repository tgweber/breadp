################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains util methods for breadp tests
#
################################################################################

import inspect
import json
import re

from breadp.checks.pid import IsValidDoiCheck
from breadp.checks.metadata import \
    DescriptionsNumberCheck, \
    DescriptionsLengthCheck, \
    DescriptionsTypeCheck, \
    TitlesJustAFileNameCheck
from breadp.rdp import RdpFactory, Rdp

class _MockResponse:
    def __init__(self, content, status_code, headers = {}):
        self.content = content
        self.status_code = status_code
        self.headers = headers

    def json(self):
        return self.content

# Prepare Mock responses for the tests
def mocked_requests_get(*args, **kwargs):
    if args[0] == "https://zenodo.org/oai2d" and args[1]["identifier"] == "oai:zenodo.org:3490396":
        with open("./tests/artefacts/md001.xml", "rb") as f:
            content = f.read()
        return _MockResponse(content, 200)
    elif args[0] == "https://zenodo.org/oai2d" and args[1]["identifier"] == "oai:zenodo.org:badex1":
        with open("./tests/artefacts/md002.xml", "rb") as f:
            content = f.read()
        return _MockResponse(content, 200)
    elif args[0] == "https://zenodo.org/oai2d" and args[1]["identifier"] == "oai:zenodo.org:badex2":
        with open("./tests/artefacts/md003.xml", "rb") as f:
            content = f.read()
        return _MockResponse(content, 200)
    elif args[0] == "https://zenodo.org/oai2d" and args[1]["identifier"] == "oai:zenodo.org:badex3":
        with open("./tests/artefacts/md004.xml", "rb") as f:
            content = f.read()
        return _MockResponse(content, 200)
    elif args[0] == "https://zenodo.org/oai2d" and args[1]["identifier"] == "oai:zenodo.org:badex4":
        with open("./tests/artefacts/md005.xml", "rb") as f:
            content = f.read()
        return _MockResponse(content, 200)
    elif args[0] == "https://zenodo.org/oai2d" and args[1]["identifier"] == "oai:zenodo.org:badex5":
        with open("./tests/artefacts/md006.xml", "rb") as f:
            content = f.read()
        return _MockResponse(content, 200)
    elif args[0] == "https://zenodo.org/oai2d" and args[1]["identifier"] == "oai:zenodo.org:goodex1":
        with open("./tests/artefacts/md007.xml", "rb") as f:
            content = f.read()
        return _MockResponse(content, 200)
    elif args[0] == "https://zenodo.org/oai2d" and args[1]["identifier"] == "oai:zenodo.org:goodex2":
        with open("./tests/artefacts/md008.xml", "rb") as f:
            content = f.read()
        return _MockResponse(content, 200)
    elif args[0] == "https://zenodo.org/oai2d" and args[1]["identifier"] == "oai:zenodo.org:goodex3":
        with open("./tests/artefacts/md009.xml", "rb") as f:
            content = f.read()
        return _MockResponse(content, 200)
    elif args[0] == "https://zenodo.org/api/deposit/depositions/3490396/files":
        with open("./tests/artefacts/zenodo001.json", "r") as f:
            content = json.load(f)
        return _MockResponse(content, 200)
    elif args[0] == "https://zenodo.org/api/files/abc/s_data_vectorized.csv":
        with open("./tests/artefacts/d001.csv", "rb") as f:
            content = f.read()
        return _MockResponse(content, 200)
    return _MockResponse(None, 404)

def mocked_requests_head(*args, **kwargs):
    #print(args[0])
    if args[0] == "https://doi.org/10.5281/zenodo.3490396":
        return _MockResponse(
            "", 302, {"Location": "https://zenodo.org/record/3490396"}
        )
    elif args[0] == "https://doi.org/10.123/zenodo.3490396-exception" or \
        args[0] == "https://somethingwentterriblywrong.com":
        raise Exception("Something went terribly wrong")
    elif args[0] == "http://creativecommons.org/licenses/by/4.0/legalcode" or \
            args[0] == "https://creativecommons.org/licenses/by-sa/4.0/legalcode" or \
            args[0] == "http://creativecommons.org/licenses/by-sa/4.0/":
        return _MockResponse("Some License text", 200)
    return _MockResponse(None, 404)

# Basic tests for all checks which did not already run
def base_init_check_test(check, check_id):
    if not check.id == check_id:
        print("Given check id ({}) is not identical of check's id ({})".format(check_id, check.id))
        return False
    if not re.match('^\d+\.\d+.\d+$', check.version):
        print("Unvalid version string: {}".format(check.version))
        return False
    if not len(check.log) == 0:
        return False
    return True

def get_rdps():
    return [
        RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123"),
        RdpFactory.create("10.123/zenodo.badex1", "zenodo", token="123"),
        RdpFactory.create("10.123/zenodo.badex2", "zenodo", token="123"),
        RdpFactory.create("10.123/zenodo.badex3", "zenodo", token="123"),
        RdpFactory.create("10.123/zenodo.badex4", "zenodo", token="123"),
        RdpFactory.create("10.123/zenodo.badex5", "zenodo", token="123"),
        RdpFactory.create("10.123/zenodo.goodex1", "zenodo", token="123"),
        RdpFactory.create("10.123/zenodo.goodex2", "zenodo", token="123"),
        RdpFactory.create("10.123/zenodo.goodex3", "zenodo", token="123")
    ]

def get_checks(rdps):
    checks = {
        "metric": DescriptionsNumberCheck(),
        "string": DescriptionsTypeCheck(),
        "boolean": IsValidDoiCheck(),
        "lom": DescriptionsLengthCheck(),
        "lob": TitlesJustAFileNameCheck(),
    }
    for c in checks.values():
        for r in rdps:
            c.check(r)
    return checks
