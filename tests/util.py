################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains util methods for breadp tests
#
################################################################################
import json
import re

# Prepare Mock responses for the tests
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, content, status_code):
            self.content = content
            self.status_code = status_code

        def json(self):
            return self.content
    #print(args[0])
    if args[0] == "https://zenodo.org/oai2d":
        with open("./tests/artefacts/md001.xml", "rb") as f:
            content = f.read()
        return MockResponse(content, 200)
    elif args[0] == "https://zenodo.org/api/deposit/depositions/3490396/files":
        with open("./tests/artefacts/zenodo001.json", "r") as f:
            content = json.load(f)
        return MockResponse(content, 200)
    elif args[0] == "https://zenodo.org/api/files/abc/s_data_vectorized.csv":
        with open("./tests/artefacts/d001.csv", "rb") as f:
            content = f.read()
        return MockResponse(content, 200)
    return MockResponse(None, 404)

# Basic tests for all checks who did not already run
def base_init_check_test(check, check_id):
    if not check.id == check_id:
        print("Given check id ({}) is not identical of check's id ({})".format(check_id, check.id))
        return False
    if not re.match('^\d+\.\d+.\d+$', check.version):
        print("Unvalid version string: {}".format(check.version))
        return False
    if not len(check.desc) > 10:
        return False
    if not len(check.description) > 10:
        return False
    if not check.status == "unchecked":
        return False
    if not len(check.log) == 0:
        return False
    return True
