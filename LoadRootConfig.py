#!/usr/bin/env python3

import yaml

def LoadRootConfig():

    with open("RootConfig.yaml", 'r') as stream:
        try:
            config = yaml.safe_load(stream)

            return config
        except yaml.YAMLError as exc:
            print(exc)

            exit(10)

    return null
