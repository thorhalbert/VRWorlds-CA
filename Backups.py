#!/usr/bin/env python3


# Create the encrypted backups


# egresses and backups derive from a base class


import Outputs


class Backups(Outputs.Outputs):
    def __init__(self, *, rootConfig, workQueue, key, output):
        super(Backups, self).__init__(rootConfig, workQueue, key, output)

        self.outputs = rootConfig['Backups']
        self.writePrivateKey = True

    def RecapitulateRootCerts(self):
        pass

   