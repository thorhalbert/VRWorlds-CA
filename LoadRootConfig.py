#!/usr/bin/env python3

import os
import yaml

def LoadRootConfig(prefix):

    fName = 'RootConfig.yaml'
    if prefix is not None:
        fName = os.path.join(prefix, fName)

    if not os.path.exists(fName):
        print("Root Config: "+fName+" - does not exist")
        exit(10)

    with open(fName, 'r') as stream:
        try:
            config = yaml.safe_load(stream)

            return config
        except yaml.YAMLError as exc:
            print(exc)

            exit(10)

    return null  # Should not get here