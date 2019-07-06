#!/usr/bin/env python3

import abc


class Outputs(metaclass=abc.ABCMeta):
    pass

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
