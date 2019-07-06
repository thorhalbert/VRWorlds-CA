#!/usr/bin/env python3

# Class to manage the work queue


class WorkQueue():
    rootConfig = None
    passPhrases = None

    def __init__(self, *, rootConfig, passPhrases):
        self.rootConfig = rootConfig
        self.passPhrases = passPhrases

    def AssimilateExistingCerts(self):
        pass

    def DiscoverAllNewWork(self):
        pass

    def GenerateLog(self):
        pass
