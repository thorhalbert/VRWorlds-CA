#!/usr/bin/env python3

import os
import pickledb
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from base64 import b64encode, b64decode


class ManagePassPhrases():
    helloUuid = 'c24711b0-71e5-41ae-933d-8c857a3713e5'
    rootConfig = None
    passPhrase = None
    phraseSalt = b'N\xe10\xae|\xbe(HB\xe3\xba\xd6SSA\xb5\xc6x\xc38\x04\xab\x9b\x8fi6\xbe\xba\xea3\xb8\xf7'
    passKey = None

    def __init__(self, *, rootConfig):
        self.rootConfig = rootConfig

        picklePath = os.path.join(self.rootConfig['Prefix'], 'passDb.db')
        #print("PicklePath: "+picklePath)

        self.phraseDb = pickledb.load(picklePath, False)

    def AskForMasterLockPassphrase(self):
        self.passPhrase = input("\nPassphrase: ").strip()

        # generate a 32 byte AES key
        self.passKey = PBKDF2(
            bytes(self.passPhrase, encoding='utf-8'), self.phraseSalt, dkLen=32)
        # self.passKey = os.urandom(16)

        # See if he helloUuid exists
        if not self.phraseDb.exists(self.helloUuid):
            self.__setPassPhrase(self.helloUuid, self.passPhrase)

            return

        # See if the phrase matches
        originalPassphrase = self.__readPassPhrase(self.helloUuid)

        #print("Phrases: ", originalPassphrase, self.passPhrase)
        originalPassphrase = originalPassphrase.decode('utf-8')
        if originalPassphrase == self.passPhrase:
            print('[Passphrase Matches - Database Unlocked]')
        else:
            print('Error: Passprase Mismatch - Cannot Unlock')
            exit(100)

    def Close(self):
        self.phraseDb.dump()

    def __setPassPhrase(self, uuid, phrase):
        #print("Key: ", self.passKey)
        cipher = AES.new(self.passKey, AES.MODE_OCB)  # EAX mode doesn't work
        # cipher.update(b'header')

        plainText = bytes(phrase, encoding='utf-8')

        #print("PlainText: ", plainText)
        ciphered_data, tag = cipher.encrypt_and_digest(plainText)

        nonce = cipher.nonce

        #cipher = AES.new(self.passKey, AES.MODE_OCB, nonce=nonce)
        #newText = cipher.decrypt_and_verify(ciphered_data, tag)

        #print("Nonce=", nonce)
        #print("Tag=", tag)
        #print("Cypher=", ciphered_data)

        #print("Verify=", newText)

        enList = b64encode(nonce).decode('utf-8') + '|' + b64encode(
            tag).decode('utf-8') + '|' + b64encode(ciphered_data).decode('utf-8')
        # print(enList)

        self.phraseDb.set(uuid, enList)

    def __readPassPhrase(self, uuid):
        decRaw = self.phraseDb.get(uuid)

        parts = decRaw.split('|')
        # print("Parts=",parts)

        nonce = bytes(b64decode(parts[0]))
        tag = bytes(b64decode(parts[1]))
        ciphered_data = bytes(b64decode(parts[2]))

        #print("Nonce=", nonce)
        #print("Tag=", tag)
        #print("Cypher=", ciphered_data)

        # Decrypt and verify
        cipher = AES.new(self.passKey, AES.MODE_OCB, nonce=nonce)
        # cipher.update(b'header')

        # Mac error will throw here - we should trap it
        original_data = cipher.decrypt_and_verify(ciphered_data, tag)

        return original_data
