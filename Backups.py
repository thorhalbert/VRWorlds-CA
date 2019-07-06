#!/usr/bin/env python3


# Create the encrypted backups


# egresses and backups derive from a base class


import Outputs


class Backups(Outputs.Outputs):
    def __init__(self, *, rootConfig, workQueue):
        super(Backups, self).__init__(rootConfig, workQueue)

    def RecapitulateRootCerts(self):
        pass
