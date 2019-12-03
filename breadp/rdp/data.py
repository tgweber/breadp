import csv

class Data(object):
    def __init__(self, source):
        self.source = source

# DataBundle?

################################################################################
# SPECIFIC DATA IMPLEMENTATIONS
################################################################################
class CSVData(Data):
    def __init__(self, source):
        super().__init__(source)
        with open(self.source, "r") as f:
            reader = csv.reader(f, skipinitialspace=True)
            self.header = next(reader)
            # TODO cast type of cell
            self.rows = [dict(zip(self.header, row)) for row in reader]
