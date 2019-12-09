################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains all code related to data (as a component of RDPs)
#
################################################################################
import csv
import os
import requests
import tempfile
from mimetypes import guess_type

class Data(object):
    """ Base class and interface for Data as components of RDPs

    Methods
    -------
    download() -> None
        Downloads the data item (will be removed on object deletion)
    """
    def __init__(self, source):
        self.source = source
        self.downloaded = False
        (self.type, self.encoding) = guess_type(source)

    def __del__(self):
        if self.downloaded:
            os.unlink(self.tmpfile)

    def download(self) -> None:
        """ Downloads the data item (will be removed on object deletion)
        """
        (self.fd, self.tmpfile) = tempfile.mkstemp()
        r = requests.get(self.source)
        os.write(self.fd, r.content)
        os.close(self.fd)
        self.downloaded = True

class DataFactory(object):
    """ Factory for Data

    Methods
    -------
    create(source) -> Data
        Factory method returning a Data object appropriate for the specified source
    """
    def create(source):
        """ Creats a Data object appropriate for the specified source

        Parameters
        ----------
        source: str
            URI indicating where to find the data item

        Returns
        -------
        Data: The created Data object
        """
        (file_type, encoding) = guess_type(source)
        # TODO handle zipped/archives
        if file_type == "text/csv":
            return CSVData(source)
        return Data(source)

################################################################################
# SPECIFIC DATA IMPLEMENTATIONS
################################################################################
class CSVData(Data):
    """ Comma-separated Data object

    Attributes
    ----------
    header: dict
        List of column names of the csv (first row)
    rows: list of dicts
        List of key-value pairs for each row, keys are column headers
    """
    def __init__(self, source):
        super().__init__(source)
        self._header = []
        self._rows = []

    def _read_csv(self):
        if not self._rows:
            with open(self.tmpfile, "r") as f:
                reader = csv.reader(f, skipinitialspace=True)
                self._header = next(reader)
                self._rows = [dict(zip(self.header, row)) for row in reader]

    def _read_csv_header(self):
        if not self._header:
            with open(self.tmpfile, "r") as f:
                reader = csv.reader(f, skipinitialspace=True)
                self._header = next(reader)

    def _check_or_download(self):
        if not self.downloaded:
            self.download()

    @property
    def header(self):
        self._check_or_download()
        self._read_csv_header()
        return self._header

    @property
    def rows(self):
        self._check_or_download()
        self._read_csv()
        return self._rows
