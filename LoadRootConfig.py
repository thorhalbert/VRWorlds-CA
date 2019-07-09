#!/usr/bin/env python3

import os
import yaml
from pprint import pprint

# Eventually need a schema for list of mandatory fields, and possibly field type checking

def LoadRootConfig(prefix):

    fName = 'RootConfig.yaml'

    fName = os.path.join(prefix, fName)
    certPath = os.path.join(prefix, 'certs')

    if not os.path.exists(fName):
        print("[Create: "+fName+"]")
        os.mkdir(fName, 0o700)

    if not os.path.exists(certPath):
        print("[Create: "+certPath+"]")
        os.mkdir(certPath, 0o700)

    if not os.path.exists(fName):
        print("Root Config: "+fName+" - does not exist")
        exit(10)

    with open(fName, 'r') as stream:
        try:
            config = yaml.safe_load(stream)

            config['Prefix'] = prefix
            config['CertPath'] = certPath

            pprint(config)

            return config
        except yaml.YAMLError as exc:
            print(exc)

            exit(10)

    return None  # Should not get here
