#!/usr/bin/env python3

import os
import yaml
from pprint import pprint


def __procConfig(config):
    # create work directories for the egresses and backups

    egress_count = 0

    prefix = config['Prefix']
    egresses = os.path.join(prefix, 'egresses')
    backups = os.path.join(prefix, 'backups')

    if not os.path.exists(egresses):
        print("[Create: "+egresses+"]")
        os.mkdir(egresses, 0o700)

    if not os.path.exists(backups):
        print("[Create: "+backups+"]")
        os.mkdir(backups, 0o700)

    def __procWorkDir(dirObj, key, basePath):
        proc = dirObj[key]

        path = os.path.join(basePath, key)
        if not os.path.exists(path):
            print("[Create: "+path+"]")
            os.mkdir(path, 0o700)

        tmp = os.path.join(path, 'tmp')
        if not os.path.exists(tmp):
            print("[Create: "+tmp+"]")
            os.mkdir(tmp, 0o700)

        proc['Path'] = path
        proc['Tmp'] = tmp

    if 'Egresses' in config:
        for obj in config['Egresses']:
            for key in obj:
                __procWorkDir(obj, key, egresses)
                egress_count += 1
    else:
        config['Egresses'] = []

    if 'Backups' in config:
        for obj in config['Backups']:
            for key in obj:
                __procWorkDir(obj, key, backups)
    else:
        config['Backups'] = []

    # Asserts

    if egress_count < 1:
        print("There must be at least one egress defined")
        exit(10)

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

            __procConfig(config)

            return config
        except yaml.YAMLError as exc:
            print(exc)

            exit(10)

    return None  # Should not get here
