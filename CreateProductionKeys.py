#!/usr/bin/env python3

import LoadRootConfig
import ManagePassPhrases
import WorkQueue

# Terms:
#  quantum:
#    if < 1, then year is multiplied by this to get divide year into integer sections
#          These are divided up into into an integer number of days
#    if > 1, then this is still the fraction of year (but > 1 year).   2 is a max
#
#   Initially quantum will be set to a small number to force the rollover code to be tested heavily
#
#  load:
#    number of signers to be made for each period.   The more signers, the fewer
#    end-certificated would be invalidated if a signer must be revoked/repudiated

prefixDir = '/usr/local/etc/vrworlds_ca'

# Load the RootConfig.yaml

rootConfig = LoadRootConfig.LoadRootConfig(prefixDir)

# Open the PickleDb for the passphrases

passPhrases = ManagePassPhrases()

# Prompt for the Locking Passphrase
# validate the passphrase against the pickledb root entry (if any, or write new)

passPhrases.AskForMasterLockPassphrase()

# Prepare the work list

workQueue = WorkQueue(rootConfig, passPhrases)

# Read the current certificate manifest

workQueue.AssimilateExistingCerts()

# Create a directory for each of the egresses and the backups

egresses = Egresses(rootConfig)
backups = Backups(rootConfig)

# Create a work entry for each cert which must be created, including root CAs.
#    1.  Compute quantums and compare to existing certs.
#        Look at expire dates and see if new certs need to be created
#    2.  Look at the Load and see how many certs must be created for each type
#        and possibily more certs to handle higher load

workQueue.DiscoverAllNewWork()

# Loop through all previous certs
#  1.  Find their passphrase and decrypt them
#  2.  Compute a new passphrase
#  3.  Re-encrypt and rewrite locally
#  4.  Encrypt with egress public key and write to egress
#  5.  Encrypt all (including root certs) to backup public key and write
#  6.  Add to manifest

egresses.RecapitulateExistingCerts(workQueue)
backups.RecapitulateRootCerts()   # Egress doesn't get this
backups.RecapitulateExistingCerts(workQueue)

# Go through queue for new certs
#  Generate new pub/pri key and csr and make a new cert
#  Sign with the root
#  Do pretty much 1-6 of previous step for new certs

CertCreator.GenerateNewCerts(workQueue)
egresses.ExportNewCerts(workQueue)
backups.ExportNewCerts(workQueue)

# Write out the encrypted passphrases

egresses.ExportPassphrases(workQueue)
backups.ExportPassphrases(workQueue)

# Write out manifest

workQueue.GenerateLog()

# Write out log to each of the outputs

egresses.GenerateLog()
backups.GenerateLog()

# finish

egresses.Close()
backups.Close()

print("[Done]")