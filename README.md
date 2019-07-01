# VRWorlds-CA
Certificate Authority for VRWorlds - For Raspberry PI, written in Python

 * Assure existence of encrypting certificates (must be heavily passphrased) 
   *  Ultimately we might only have this public key.  Though we probably have to sign something with the CA to prove we're who we say we are.   The Private key will be held by the main Kudo servers to be able to assimilate the archive we generate.
* If not, then generate them.  Probably a big of a manual process to get this bootstrapped - though maybe this is a Kudo function.  We load the private key from the thumb drive and verify it's fingerprint or some such.

* Check config file - has rules for expiration and defaults for this organization/manufacturer.   CA shouldn't have an expiration that's too deep (say 6-months to a year)
* Check to see if the CA meets the "lead time" criterion - a certain number of certs into the future, say 5 years should be produced.
* Iterate through the signers required and how many should be extant at a time (should be >1, maybe even as much as hundreds of them if the origanization is huge).  This permits a much more strategic revocation to occur.
* Proceed through the "lead time" criterion for these.  They aren't needed too far in the future.  More so that the CA only needs to be gotten out of the safe infrequently.
* Generate a new passphrase database.  This is never kept on disk non-encrypted.
* Generate all of the required certificates.   Passphrase randomly with the above passphrase database.
* Record everything in the required directories.   Private keys are never kept on disk non-passphrased.
* Write the import file (likely a tar file).  The CA private keys are never written - only the signers.
* Encrypt this with the encrypting cert.  It may again ask for this passphrase.
* Write the encrypted archive to the thumb drive.
* Clean up - possibly wiping some files (not just deleting them).

To-Do:
* Started on the Schema of the RootConfig.yaml.
* Need to figure out how I'm going to store things.   Possibly sqllite.   It has to have a very clear way of doing backups.  Nothing more catastophic than losing your CA keys.  
* Everything needs to be encrypted at rest (at least passphrased)
* There will be a passphrase database too.
* Have to figure out how to use the cert fields.  We're going going to use them like they are for https -- there will be a lot of guids sitting where normal values for organizational unit and such are supposed to live.  
  * DN will probably be the manufacturer id, possibily with the domain appended (where you can look up the server).  
  * OU might be the server guid.
  * Not sure if we need any of the geographical fields
  * We may want to have special emphasis on fields for DNS (or non DNS) server lookups - custom certificate extentions?

Raspberry Pi issues:
* These are supposed to be air-gapped
* Does air-gap mean we can't have an accurate clock - though our nature doesn't require too accurate a clock
* Need to look at entropy/random number generator hardware

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
    * Deal with PiHDM loss due to hardware failure.
    * Deal with PiHDM being compromised
    * Deal with backup being compromised
    * Backups would have to include the CA private keys - perhaps this is simply a copy or serialization of the sqlite (or whatever) database (and possibily even the code).