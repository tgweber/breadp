################################################################################
# Copyright: Tobias Weber 2019
#
# Apache 2.0 License
#
# This file contains all code related to log objects
#
################################################################################

class Log(object):
    def __init__(self):
        self.log = []

    def __len__(self):
        return len(self.log)

    def add(self, le):
        self.log.append(le)

    def get_by_pid(self, pid):
        rv = []
        for le in self.log:
            import pprint
            pprint.pprint(le)
            if le.pid == pid:
                rv.append(le)
        return rv

class LogEntry(object):
    def __init__(self, start, end, version, pid, msg):
        self.start = start
        self.end = end
        self.version = version
        self.pid = pid
        self.msg = msg

class CheckLogEntry(LogEntry):
    def __init__(self, start, end, version, pid, msg, state):
        super(CheckLogEntry, self).__init__(start, end, version, pid, msg)
        self.state = state

class AssessmentLogEntry(LogEntry):
    def __init__(self, start, end, version, pid, msg, assessment):
        super(AssessmentLogEntry, self).__init__(start, end, version, pid, msg)
        self.assessment = assessment
