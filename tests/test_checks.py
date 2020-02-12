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
from breadp.checks.metadata import DataCiteDescriptionsTypeCheck, \
        DescriptionsNumberCheck, \
        DescriptionsLanguageCheck, \
        DescriptionsLengthCheck, \
        MainTitleLanguageCheck, \
        MainTitleLengthCheck, \
        MainTitleProbablyJustAFileNameCheck, \
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
    assert check.result.outcome == 1

    rdp = RdpFactory.create("10.5281/zenodo.badex1", "zenodo", token="123")
    check.check(rdp)
    assert not check.success
    assert check.result.outcome == 0

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_main_title_length_check(mock_get):
    check = MainTitleLengthCheck()
    assert base_init_check_test(check, 7)

    # Successful check
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert check.result.outcome == 20

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_main_title_language_check(mock_get):
    check = MainTitleLanguageCheck()
    assert base_init_check_test(check, 8)

    # Successful check
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert check.result.outcome == "en"


@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_main_title_probably_just_a_filename_check(mock_get):
    check = MainTitleProbablyJustAFileNameCheck()
    assert base_init_check_test(check, 9)

    # Successful check
    rdp = RdpFactory.create("10.5281/zenodo.3490396", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert not check.result.outcome

    rdp = RdpFactory.create("10.5281/zenodo.badex2", "zenodo", token="123")
    check.check(rdp)
    assert check.success
    assert check.result.outcome
