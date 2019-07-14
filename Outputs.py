#!/usr/bin/env python3

import os
import yaml
import abc
import io
import time

import shutil

import tarfile

import CertCreator

from pprint import pprint

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES

# Abstract Class


class Outputs(metaclass=abc.ABCMeta):
    rootConfig = None
    workQueue = None

    key = None
    __output = None

    writePrivateKey = False

    Manifest = None
    PassPhrases = []

    Path = None
    Tmp = None

    def __init__(self, rootConfig, workQueue, key, output, CAPrivate):
        self.rootConfig = rootConfig
        self.workQueue = workQueue
        self.key = key
        self.__output = output[key]

        self.writePrivateKey = CAPrivate

        self.PublicKeyFile = self.__output['Public-Key']
        self.Path = self.__output['Path']
        self.Tmp = self.__output['Tmp']

        self.Manifest = []

        pprint(self.__output)

    def RecapitulateExistingCerts(self):
        pass

    def ExportCerts(self):
        print("Export roots: ", self.writePrivateKey)
        self._exportCerts(self.workQueue.root_certificates,
                          self.writePrivateKey)
        self._exportCerts(self.workQueue.certificates, True)

    def ExportPassPhrases(self):
        publicKey = os.path.join(self.rootConfig['Prefix'], self.PublicKeyFile)
        if not os.path.exists(publicKey):
            print("Can't find your public key: "+publicKey)
            exit(10)

        with open(publicKey, "rb") as key_file:
            public_key = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend())

        # Capture the passphrase file into a string (and encode it)

        passphrases = io.StringIO()
        yaml.dump(self.PassPhrases, passphrases, default_flow_style=False)
        passBytes = passphrases.getvalue().encode('utf-8')
        passphrases.close()

        # Generate a password for aes and encrypt it with public key

        symetricPass = os.urandom(32)   # AES Max

        encrypted = public_key.encrypt(symetricPass,
                                       padding.OAEP(
                                           mgf=padding.MGF1(
                                               algorithm=hashes.SHA256()),
                                           algorithm=hashes.SHA256(),
                                           label=None
                                       ))

        # Encrypt payload with AES

        cipher = AES.new(symetricPass, AES.MODE_OCB)  # EAX mode doesn't work

        ciphered_data, tag = cipher.encrypt_and_digest(passBytes)

        nonce = cipher.nonce

        outFile = "passphrases.yaml.encrypted"

        keyInfo = {
            'Type': 'OCB',
            'SymmetricPass': encrypted,
            'Key': public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo),
            'Nonce': nonce,
            'MAC': tag,
            'File': outFile
        }

        del symetricPass
        del encrypted      # let this go out of scope now

        pasF = os.path.join(self.Tmp, "passphrases.yaml")
        with open(pasF, 'w') as yaml_file:
            yaml.dump(keyInfo, yaml_file, default_flow_style=False)

        del passBytes      # let this go out of scope now

        pasF = os.path.join(self.Tmp, outFile)
        with open(pasF, 'wb') as passF:
            passF.write(ciphered_data)

        del ciphered_data

    def ExportManifest(self):
        pasF = os.path.join(self.Tmp, "manifest.yaml")
        with open(pasF, 'w') as yaml_file:
            yaml.dump(self.Manifest, yaml_file, default_flow_style=False)

        # pprint(self.Manifest)

    def GenerateLog(self):
        pass

    def Close(self):
        print("[Remove: "+self.Tmp+']')
        shutil.rmtree(self.Tmp)

    def _exportCerts(self, queue, writePriv):
        CertCreator.ExportCerts(self.key, self, self.Manifest, queue, writePriv)

    def __addFile(self, tar, file):
        real = os.path.join(self.Tmp, file)
        tar.add(real, arcname=file)

    def GenerateTarFile(self):
        print(self.key, self.Path, self.Tmp)
        # pprint(self.Manifest)

        tarFile = os.path.join(self.Path, self.key+'_' +
                               time.strftime('%Y%m%d-%H%M%S')+'.tgz')
        with tarfile.open(tarFile, "w:gz") as tar:
            self.__addFile(tar, 'manifest.yaml')

            for m in self.Manifest:
                for e in ['CertificateFile', 'PrivateKeyFile']:
                    if e in m:
                        self.__addFile(tar, m[e])

            self.__addFile(tar, 'passphrases.yaml')
            self.__addFile(tar, 'passphrases.yaml.encrypted')
