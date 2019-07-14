#!/usr/bin/env python3

import os
import yaml
import time
import datetime

import Egresses
import Backups
import CertCreator

from pprint import pprint

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

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

    # last date for cert
    root_cert_last = datetime.datetime(1900, 1, 1)
    cert_last = {}

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

        maniFile = os.path.join(self.rootConfig['CertPath'], 'manifest.yaml')
        if not os.path.exists(maniFile):
            print('[Initial Run - Manifest File Not Seen]')
            return

        print("[Read Current Manifest]")
        with open(maniFile, 'r') as stream:
            try:
                manifest = yaml.safe_load(stream)

            except yaml.YAMLError as exc:
                print(exc)

                exit(10)

        for cert in manifest:
            info = cert['CertInfo']

            certEntry = {
                'Id': cert['Id'],
                'Target': info['Target'],
                'Enqueued': False,
                'CertType': info['Cert-Type'],
                'CertClass': info['Cert-Class'],
                'Quantum': info['Quantum'],
                'Lead-Time': info['Lead-Time'],
                'Existing': True,
                'Load': info['Load'],
                'Start': info['Valid-From'],
                'Stop': info['Valid-To'],
                'PhraseKey': cert['PhraseKey'],
                'CertificateFile': cert['CertificateFile'],
                'PrivateKeyFile': cert['PrivateKeyFile'],
            }

            # We now need to bring the actual cert in -- we always write to egress/backup
            # and we have to decrypt the passprase and then decrypt the private key with that

            # Read the cert - someday we'll want to trap errors - losing a cert is a catastrophe anyway

            certFile = os.path.join(
                self.rootConfig['CertPath'], cert['CertificateFile'])

            print("[Load Cert: "+cert['CertificateFile']+']')
            with open(certFile, "rb") as cert_file:
                cert_body = x509.load_pem_x509_certificate(
                    cert_file.read(), default_backend())

            certEntry['Certificate'] = cert_body
            certEntry['Persisted'] = True
            certEntry['Enqueued'] = False

            # Read the private key

            passphrase = self.passPhrases.RetreivePassPhrase(cert['PhraseKey'])

            privateKeyFile = os.path.join(
                self.rootConfig['CertPath'], cert['PrivateKeyFile'])

            print("[Load Key: "+cert['PrivateKeyFile']+']')
            with open(privateKeyFile, "rb") as key_file:
                private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=passphrase,
                    backend=default_backend())

            certEntry['PrivateKey'] = private_key

            # Capture cert into correct type, and also capture the last date
            #  Since they're always created contiguously we don't need to deal
            #  with any certs who's start is before this max ending (there might be
            #  need to make a truncated cert, but only new certs after this date)

            if info['Cert-Class'] == 'Root':
                self.root_certificates .append(certEntry)

                if info['Valid-To'] > self.root_cert_last:
                    self.root_cert_last = info['Valid-To']
            else:
                self.certificates.append(certEntry)

                certKey = info['Cert-Type']+'/'+info['Target']
                if certKey not in self.cert_last:
                    self.cert_last[certKey] = datetime.datetime(1900, 1, 1)

                if info['Valid-To'] > self.cert_last[certKey]:
                    self.cert_last[certKey] = info['Valid-To']

    def DiscoverAllNewWork(self):
        self.__findCAWork()
        self.__findSigners()

    def GenerateLog(self):
        pass

    def __findCAWork(self):
        self.CA_Lead = float(self.rootConfig['CA-Lead-Time'])
        self.CA_Quantum = float(self.rootConfig['Root-Quantum'])

        rootDates = {
            'CA/Root': self.root_cert_last
        }

        CertCreator.FindCertificates(
            'CA', 'Root', self.root_certificates, self.CA_Quantum, 1, self.CA_Lead, rootDates)

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
                    fType, name, self.certificates, quantum, load, self.Signer_Lead, self.cert_last)

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
            "Main Persistence", outputDir, manifest, certList, True, True))

    def Close(self):
        for egress in self.egresses:
            egressObj = self.egresses[egress]
            egressObj.Close()

        for backup in self.backups:
            backupObj = self.backups[backup]
            backupObj.Close()
