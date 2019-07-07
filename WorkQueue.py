#!/usr/bin/env python3

import CertCreator

# Class to manage the work queue


class WorkQueue():
    rootConfig = None
    passPhrases = None

    signers_Services = []
    signers_Infrastructure = []

    certificates = []

    def __init__(self, *, rootConfig, passPhrases):
        self.rootConfig = rootConfig
        self.passPhrases = passPhrases

    def AssimilateExistingCerts(self):
        pass

    def DiscoverAllNewWork(self):
        self.__findCAWork()
        self.__findSigners()

    def GenerateLog(self):
        pass

    def __findCAWork(self):
        self.CA_Lead = float(self.rootConfig['CA-Lead-Time'])
        self.CA_Quantum = float(self.rootConfig['Root-Quantum'])

        CertCreator.FindCertificates(
            'CA', 'Root', self.certificates, self.CA_Quantum, 1, self.CA_Lead)

    def __findSigners(self):
        self.Signer_Lead = float(self.rootConfig['Signer-Lead-Time'])

        if 'Signers' in self.rootConfig:
            signers = self.rootConfig['Signers']
            if 'Services' in signers:
                self.signers_Services = signers['Services']
            if 'Infrastructure' in signers:
                self.signers_Infrastructure = signers['Infrastructure']

        self.__searchSigners(self.signers_Services, 'Signers/Services')
        self.__searchSigners(self.signers_Infrastructure,
                             'Signers/Infrastructure')

    def __searchSigners(self, info, fType):
        for part in info:
            for name in part:
                print('Name: ',name)
                load=1
                quantum=1

                setup=part[name]
                if 'Load' in setup:
                    load=float(setup['Load'])

                if 'Quantum' in setup:
                    quantum=float(setup['Quantum'])

                CertCreator.FindCertificates(
                    fType, name, self.certificates, quantum, load, self.Signer_Lead)
