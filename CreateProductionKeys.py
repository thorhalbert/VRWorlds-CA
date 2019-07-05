#!/usr/bin/env python3


# Load the RootConfig.yaml

# Open the PickleDb for the passphrases

# Prompt for the Locking Passphrase

# validate the passphrase against the pickledb root entry

# Prepare the work list

# Enumerate all of the certificate types

# Read the current certificate manifest

# Create a directory for each of the egresses and the backups

# Create a work entry for each cert which must be created, including root CAs.
#    1.  Compute quantums and compare to existing certs.
#        Look at expire dates and see if new certs need to be created
#    2.  Look at the Load and see how many certs must be created for each type
#        and possibily more certs to handle higher load

# Loop through all previous certs
#  1.  Find their passphrase and decrypt them
#  2.  Compute a new passphrase
#  3.  Re-encrypt and rewrite locally
#  4.  Encrypt with egress public key and write to egress
#  5.  Encrypt all (including root certs) to backup public key and write
#  6.  Add to manifest

# Go through queue for new certs
#  Generate new pub/pri key and csr and make a new cert
#  Sign with the root
#  Do pretty much 1-6 of previous step for new certs

# Write out manifest

# Write out log to each of the outputs

# finish