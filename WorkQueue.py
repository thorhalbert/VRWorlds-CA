#!/usr/bin/env python3

import os
import yaml
import time

import Egresses
import Backups
import CertCreator

# Class to manage the work queue


class WorkQueue():
    rootConfig = None
    passPhrases = None

    egresses = {}
    backups = {}

    signers_Services = []
    signers_Infrastructure = []

    root_certificates = []
    certificates = []

    current_root = None

    def __init__(self, *, rootConfig, passPhrases):
        self.rootConfig = rootConfig
        self.passPhrases = passPhrases

        if 'Egresses' in rootConfig:
            for obj in rootConfig['Egresses']:
                for key in obj:
                    self.egresses[key] = Egresses.Egresses(
                        rootConfig=rootConfig, workQueue=self, key=key, output=obj)

        if 'Backups' in rootConfig:
            for obj in rootConfig['Backups']:
                for key in obj:
                    self.backups[key] = Backups.Backups(
                        rootConfig=rootConfig, workQueue=self, key=key, output=obj)

    def AssimilateExistingCerts(self):
        # read in all existing certs and decrypt
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
            'CA', 'Root', self.root_certificates, self.CA_Quantum, 1, self.CA_Lead)

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
                print('Name: ', name)
                load = 1
                quantum = 1

                setup = part[name]
                if 'Load' in setup:
                    load = float(setup['Load'])

                if 'Quantum' in setup:
                    quantum = float(setup['Quantum'])

                CertCreator.FindCertificates(
                    fType, name, self.certificates, quantum, load, self.Signer_Lead)

    def RecapitulateRootCerts(self):
        # rewrite all previous root certs with new passphrase
        pass

    def RecapitulateExistingCerts(self):
        # rewrite all previous certs with new passphrase
        pass

    def ExportCerts(self):
        # export other certs to backups and egresses

        for egress in self.egresses:
            print("[Process Egress: "+egress+']')

            egressObj = self.egresses[egress]
            egressObj.ExportCerts()

        for backup in self.backups:
            print("[Process Backup: "+backup+']')

            backupObj = self.backups[backup]
            backupObj.ExportCerts()

    def ExportPassPhrases(self):
        # write encrypted passphrase databases to backups and egresses

        for egress in self.egresses:
            print("[Passphrases for Egress: "+egress+']')

            egressObj = self.egresses[egress]
            egressObj.ExportPassPhrases()

        for backup in self.backups:
            print("[Passphrases for Backup: "+backup+']')

            backupObj = self.backups[backup]
            backupObj.ExportPassPhrases()

    def ExportManifest(self):
        for egress in self.egresses:
            print("[Manifest for Egress: "+egress+']')

            egressObj = self.egresses[egress]
            egressObj.ExportManifest()

        for backup in self.backups:
            print("[Manifest for Backup: "+backup+']')

            backupObj = self.backups[backup]
            backupObj.ExportManifest()

    def ExportTarFile(self):
        # write encrypted passphrase databases to backups and egresses

        for egress in self.egresses:
            print("[Tar for Egress: "+egress+']')

            egressObj = self.egresses[egress]
            egressObj.GenerateTarFile()

        for backup in self.backups:
            print("[Tar for Backup: "+backup+']')

            backupObj = self.backups[backup]
            backupObj.GenerateTarFile()

    def PersistLocalCerts(self):
        # Write out all files, including existing ones with new passphrases

        manifest = []
        passphrases = []

        outputDir = self.rootConfig['CertPath']

        self.__persistCerts(self.root_certificates,
                            manifest, passphrases, outputDir)
        self.__persistCerts(self.certificates, manifest,
                            passphrases, outputDir)

        # Store the passphrases in pickledb encrypted and write the manifest out
        # Need to insulate against errors, like out of disk

        self.passPhrases.ProcessNewPhrases(passphrases)

        # We should read in the encrypted pickledb and make a timestamped dump of it

        # Output the current manifest and make a timestamped backup of same
        for file in ['manifest.yaml', 'manifest-'+time.strftime('%Y%m%d-%H%M%S')+'.yaml']:
            man = os.path.join(outputDir, file)
            with open(man, 'w') as yaml_file:
                yaml.dump(manifest, yaml_file, default_flow_style=False)

    def __persistCerts(self, certList, manifest, passphrases, outputDir):

        passphrases.extend(CertCreator.ExportCerts(
            "Main Persistence", outputDir, manifest, certList, True))

    def Close(self):
        for egress in self.egresses:
            egressObj = self.egresses[egress]
            egressObj.Close()

        for backup in self.backups:
            backupObj = self.backups[backup]
            backupObj.Close()
