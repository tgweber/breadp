################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains all Check-related tests
#
################################################################################

import math
import re
from unittest import mock

from util import mocked_requests_get, mocked_requests_head, base_init_check_test
from breadp.checks import IsValidDoiCheck, DoiResolvesCheck
from breadp.checks.metadata import \
        CreatorsContainInstitutionsCheck, \
        CreatorsOrcidCheck, \
        CreatorsFamilyAndGivenNameCheck, \
        DataCiteDescriptionsTypeCheck, \
        DescriptionsNumberCheck, \
        DescriptionsLanguageCheck, \
        DescriptionsLengthCheck, \
        FormatsAreValidMediaTypeCheck, \
        isValidOrcid, \
        RightsHaveValidSPDXIdentifierCheck, \
        RightsHasAtLeastOneLicenseCheck, \
        SubjectsAreQualifiedCheck, \
        SubjectsHaveDdcCheck, \
        SubjectsHaveWikidataKeywordsCheck, \
        SubjectsNumberCheck, \
        TitlesJustAFileNameCheck, \
        TitlesLanguageCheck, \
        TitlesLengthCheck, \
        TitlesNumberCheck

from breadp.rdp.rdp import RdpFactory, Rdp

# Tests the PID check
@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_is_valid_doi_check(mock_get):
    check = IsValidDoiCheck()
    assert base_init_check_test(check, 0)

    # Successful
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert len(check.log) == 1
    assert check.log.log[-1].success == check.success
    assert check.result.outcome

    # Failure 1
    pid = rdp.pid
    rdp.pid = ""
    check.check(rdp)
    assert not check.success
    assert len(check.log) == 2
    assert check.log.log[-2].success
    assert not check.result.outcome
    rdp.pid = pid

    # Failure 2
    rdp = RdpFactory.create("10.123/zenodo.3490396-failure", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert len(check.log) == 3
    assert check.log.log[-3].success
    assert not check.log.log[-2].success
    assert not check.result.outcome

@mock.patch('requests.head', side_effect=mocked_requests_head)
@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_doi_resolve_check(mock_head, mock_get):
    check = DoiResolvesCheck()
    assert base_init_check_test(check, 1)

    # Successful resolution
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert check.result.outcome

    # failure
    rdp.pid = ""
    check.check(rdp)
    assert not check.success
    assert not check.result.outcome

    # Failed resolution
    rdp = RdpFactory.create("10.123/zenodo.3490396-failure", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert not check.result.outcome

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_descriptions_number_check(mock_get):
    check = DescriptionsNumberCheck()
    assert base_init_check_test(check, 2)
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert check.result.outcome == 2

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert check.result.outcome == 0

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_descriptions_length_check(mock_get):
    check = DescriptionsLengthCheck()
    assert base_init_check_test(check, 3)

    # Successful check
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert check.result.outcome[0] == 69
    assert check.result.outcome[1] == 3

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    check.check(rdp)
    assert not check.success
    assert len(check.result.outcome) == 0

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_descriptions_language_check(mock_get):
    check = DescriptionsLanguageCheck()
    assert base_init_check_test(check, 4)

    # Successful check
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert len(check.result.outcome) == 2
    assert check.result.outcome[0] == "en"

    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert check.result.outcome[0] == "de"

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_datacite_descriptions_types_check(mock_get):
    check =DataCiteDescriptionsTypeCheck()
    assert base_init_check_test(check, 5)

    # Successful check
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert len(check.result.outcome) == 2
    assert "Abstract" in check.result.outcome

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_titles_number_check(mock_get):
    check =TitlesNumberCheck()
    assert base_init_check_test(check, 6)

    # Successful check
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert check.result.outcome == 2

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    check.check(rdp)
    assert not check.success
    assert check.result.outcome == 0

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_titles_length_check(mock_get):
    check = TitlesLengthCheck()
    assert base_init_check_test(check, 7)

    # Successful check
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert len(check.result.outcome) == 2
    assert check.result.outcome[0] == 20
    assert check.result.outcome[1] == 12

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    check.check(rdp)
    assert not check.success

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_titles_language_check(mock_get):
    check = TitlesLanguageCheck()
    assert base_init_check_test(check, 8)

    # Successful check
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert len(check.result.outcome) == 2
    assert check.result.outcome[0] == "en"
    assert check.result.outcome[1] == "de"

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    check.check(rdp)
    assert not check.success

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_titles_just_a_filename_check(mock_get):
    check = TitlesJustAFileNameCheck()
    assert base_init_check_test(check, 9)

    # Successful check
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert len(check.result.outcome) == 2
    for o in check.result.outcome:
        assert not o

    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert check.result.outcome[0]

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_formats_are_valid_media_types(mock_get):
    check = FormatsAreValidMediaTypeCheck()
    assert base_init_check_test(check, 12)

    # Successful check
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert check.result.outcome[0]
    assert check.result.outcome[1]

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert len(check.result.outcome) == 0
    assert check.result.msg == "No formats found!"

    rdp = RdpFactory.create("10.5281/zenodo.badex4", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert check.result.outcome[0]
    assert not check.result.outcome[1]

    rdp = RdpFactory.create("10.5281/zenodo.badex5", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert not check.result.outcome[0]
    assert not check.result.outcome[1]

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_rights_have_valid_spdx_identifier(mock_get):
    check = RightsHaveValidSPDXIdentifierCheck()
    assert base_init_check_test(check, 13)

    # Successful check
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert check.result.outcome[0]

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert len(check.result.outcome) == 0
    assert check.result.msg == "No rights objects found!"

    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert not check.result.outcome[0]
    assert not check.result.outcome[1]
    assert not check.result.outcome[2]
    assert check.result.msg == "Idonotexistasarightsidentifier is not a valid SPDX identifier"

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_rights_has_at_least_one_license(mock_get):
    check = RightsHasAtLeastOneLicenseCheck()
    assert base_init_check_test(check, 14)

    # Successful check
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert check.result.outcome

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert not check.result.outcome
    assert check.result.msg == "No rights with URI retrievable: No rights specified"


    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert not check.result.outcome
    assert check.result.msg.startswith("No rights with URI retrievable:")


@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_subjects_are_qualified_check(mock_get):
    check = SubjectsAreQualifiedCheck()
    assert base_init_check_test(check, 15)

    # Successful check
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert check.result.outcome[0]
    assert check.result.outcome[1]

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert len(check.result.outcome) == 0
    assert check.result.msg == "No subjects retrievable"

    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert not check.result.outcome[0]
    assert check.result.outcome[4]

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_subjects_number_check(mock_get):
    check = SubjectsNumberCheck()
    assert base_init_check_test(check, 16)

    # Successful check
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert check.result.outcome == 2

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert check.result.outcome == 0

    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert check.result.outcome == 5

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_subjects_have_ddc_check(mock_get):
    check = SubjectsHaveDdcCheck()
    assert base_init_check_test(check, 17)

    # Successful check
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert check.result.outcome

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert not check.result.outcome

    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert not check.result.outcome

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_subjects_have_wikidata_keywords_check(mock_get):
    check = SubjectsHaveWikidataKeywordsCheck()
    assert base_init_check_test(check, 18)

    # Successful check
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert check.result.outcome

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert not check.result.outcome

    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert not check.result.outcome

def test_is_valid_orcid():
    assert isValidOrcid("0000-0003-1815-7041")
    assert not isValidOrcid("0000-0003-1815-7042")
    assert not isValidOrcid("abcd-0003-1815-7042")
    assert not isValidOrcid("0000-0003-1815-704X")

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_creators_orcid_check(mock_get):
    check = CreatorsOrcidCheck()
    assert base_init_check_test(check, 19)

    # Successful check
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert check.result.outcome[0]
    assert check.result.outcome[1]

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert len(check.result.outcome) == 0

    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert not check.result.outcome[0]

    rdp = RdpFactory.create("10.5281/zenodo.badex3", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert not check.result.outcome[0]
    assert not check.result.outcome[1]

    rdp = RdpFactory.create("10.5281/zenodo.badex4", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert check.result.outcome[0]


@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_creators_family_and_given_name_check(mock_get):
    check = CreatorsFamilyAndGivenNameCheck()
    assert base_init_check_test(check, 20)

    # Successful check
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert check.result.outcome[0]
    assert check.result.outcome[1]

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert len(check.result.outcome) == 0

    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert not check.result.outcome[0]
    assert check.result.outcome[1]

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_creators_contain_institutions_check(mock_get):
    check = CreatorsContainInstitutionsCheck()
    assert base_init_check_test(check, 21)

    # Successful check
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert not check.result.outcome

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    check.check(rdp)
    assert not check.success

    rdp = RdpFactory.create("10.5281/zenodo.badex3", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert check.result.outcome
    assert check.result.msg == "Leibniz Rechenzentrum is an institution"
