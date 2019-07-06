#!/usr/bin/env python3

# Create the encrypted egress files to be exported to the server farm

# egresses and backups derive from a base class

import Outputs


class Egresses(Outputs.Outputs):
    def __init__(self, *, rootConfig, workQueue):
        super(Egresses, self).__init__(rootConfig, workQueue)
