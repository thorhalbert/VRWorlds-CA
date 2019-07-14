# VRWorlds-CA

Certificate Authority for VRWorlds - For Raspberry PI, written in Python.  This program manages the root certificates and the intermediate signers.  The Kudo server actually handles signing.

## Warning - I am not a cryptography expert.  Just assume this code will burn your bacon, flood your basement and expose your treasure to pirates...  Please learn what you can about crypto and check me. 

# USE AT YOUR OWN RISK!

HSM on a budget?

This is intended to be put onto a Raspberry Pi and locked in a safe between uses.   Data is intended to be exported via thumb drive.

Each time it is run, it will create any new certificates that have become necessary between the runs (or if the parameters are changed).   It will never make certificates in the past.  It should be run more often than the smallest 'lead-time'.


Raspberry Pi issues:
* These are supposed to be air-gapped
* Does air-gap mean we can't have an accurate clock - though our nature doesn't require too accurate a clock
* Need to look at entropy/random number generator hardware
* Should we look at using these FIDO Keys?

Contents of Archive - encrypted by transfer public key:
* Passphrase table - a different passphrase will be generated for each private key we generate - even if we've sent this private key before (new passphrases will be used each time).
* CRL list (if any), though only for revocation of signers or CAs (let's hope this seldom happens)
* All CA certs out to the CA-Lead-Time (5 years or so).  It also includes all CA's we've ever issued in the past.  No Private Keys for CAs ever.
* All of the full PEM files for signers, and all of the private keys for the signers - all passphrased via the passphrase table
* The passphrase map (what passphrase is used for what private key)
* A status/content table - map the files on the archive to what they are (filenames will be things like guid.key, guid.pem, etc)

Security Audit
* Need to look at this for sanity - need an expert to critique someday
  * Attack surface
  * Possible vectors
* Blast Radius Esimates
  * Generate threat analysis
  * How do we safely and securely back this up
    * Disaster recovery PKI stored offsite - keep list of public keys and
    * Trivially produce encrypted backups onto thumb drives for local and remote storage.   
    * Deal with PiHSM loss due to hardware failure.
    * Deal with PiHSM being compromised
    * Deal with backup being compromised
    * The encrypted passphrase info file includes the nonce and the mac/tag -- is it proper that these are in clear?
  