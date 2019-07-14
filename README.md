# VRWorlds-CA

Certificate Authority for VRWorlds - For Raspberry PI, written in Python.  This program manages the root certificates and the intermediate signers.  The Kudo server actually handles signing.

## Warning - I am not a cryptography expert.  Just assume this code will burn your bacon, flood your basement and expose your treasure to pirates...  Please learn what you can about crypto and check me. 

# USE AT YOUR OWN RISK!

HSM on a budget?   How about a PiSM

This is intended to be put onto a Raspberry Pi and locked in a safe between uses.   Data is intended to be exported via thumb drive.

VRWorlds-CA manages root certificates (whose private keys should never leave the HSM device--except for encrypted backups) for the VRWorlds infrastructure.
It also generates and signs (from the root) a number of intermediate signing certificates.   The duration of the certificate and how far into the future
certificates are pre-creates is managed from a configuration file.   

Info about the root certificates and the signers and their private keys are written into an encrypted tar file which is encrypted with a public key so the security servers (the Kudo servers) can assimilate the data safely, while assuring that even if the PiSM is lost or this archive is compromised then the data still can't be read.

All of the information on the PiSM is encrypted with an initial passphrase, so this must be entered before anything can be read from the PiSM.

Also, the program can write any number of fully encrypted backups (which do include the root keys) which are encrypted against another set of public keys, which can deal with offsite backups which are still secure--they also get around the possibility of the passphrase on the HSM being lost.

## Issues

* I want to run ed25519 elliptic key encryption.  So far it's not working on my test boxes, so I am constrained to using RSA which I don't want to use in production.
* AES Mode EAX symmetric encryption doesn't work for me.  I'm using OCB instead.  Nonces and MAC/Tags aer stored in the clear (which I think is fine, but want somebody that knows better to tell me it's ok)
* The only thing encrypted on the archive are the private keys, which I'm using the cryptography libraries serialization.BestAvailableEncryption algorithm with 64 bytes of randomness from os.urandom as the passphrase.   Also the passphrase database is encrypted with the public key (strictly speaking another random key is encrypted via the public key and that key is used via AES to encrypt the passphrase database--a yaml file).
  