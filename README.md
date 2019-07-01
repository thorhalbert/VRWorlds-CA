# VRWorlds-CA
Certificate Authority for VRWorlds - For Raspberry PI, written in Python

* Assure existence of encrypting certificates (must be heavily passphrased) 
* If not, then generate them.

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
* Have to figure out how to use the cert fields.  We're going going to use them like they are for https -- there will be a lot of guids sitting where normal values for organizational unit and such are supposed to live.  DN will probably be the manufacturer id, possibily with the domain appended (where you can look up the server).  OU might be the server guid.

