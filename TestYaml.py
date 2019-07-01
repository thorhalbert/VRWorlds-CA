#!/usr/bin/env python3

import yaml
from pprint import pprint

with open("RootConfig.yaml", 'r') as stream:
    try:
        doc = yaml.safe_load(stream)
        pprint(doc)
    except yaml.YAMLError as exc:
        print(exc)
