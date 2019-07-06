#!/usr/bin/env python3

import abc

# Abstract Class


class Outputs(metaclass=abc.ABCMeta):
    rootConfig = None
    workQueue = None

    def __init__(self, rootConfig, workQueue):
        self.rootConfig = rootConfig
        self.workQueue = workQueue

    def RecapitulateExistingCerts(self, workQueue):
        pass

    def ExportNewCerts(self, workQueue):
        pass

    def ExportPassphrases(self, workQueue):
        pass

    def GenerateLog(self):
        pass

    def Close(self):
        pass
