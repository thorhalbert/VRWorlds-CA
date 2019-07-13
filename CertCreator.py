#!/usr/bin/env python3

import time
import uuid
import datetime
import Crypto

#import SSL
import os
import random

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends.openssl import hashes




def getYearMap(quantum, lead):
    returns = []

    # Let's enforce some limits (somewhat arbitrary)

    if quantum > 1.0:
        quantum = 1.0    # for now not allowing greater than 1 year
    if quantum < .05:
        quantum = .05    # Year into 20 slices

    if lead < .1:
        lead = .1
    if lead > 5:
        lead = 5

    # Compute real lead - how many years do we need to concern ourselves with
    rLead = int(float(lead)+.5)+1
    if rLead < 1:
        rLead = 1

    # Don't process certs requests starting after this date
    endFrame = datetime.datetime.fromtimestamp(time.time() + (366*lead*86400))
    #print("EndFrame=", endFrame)

    thisYear = datetime.date.fromtimestamp(time.time())

    # loop through all possible years
    for endYear in range(0, rLead):
        start = datetime.datetime(thisYear.year+endYear, 1, 1)
        end = datetime.datetime(thisYear.year+endYear+1, 1, 1)

        # Compute from quantum the number of slices to make of year

        delta = (end - start).days   # days in year
        interval = int(1.0 / quantum)   # number of slices in a year

        days = int(delta / interval)   # Number of days in a slice
        last = int(delta % interval)   # Remainder for last slice

        # print("This: ", start, end, delta, interval, days, last)

        # generate the slices
        for i in range(0, interval):
            startInterval = start + datetime.timedelta(days=i*days)
            if i < (interval - 1):
                endInterval = startInterval + datetime.timedelta(days=days)
            else:
                endInterval = startInterval + \
                    datetime.timedelta(
                        days=days+last)   # add the remainder for last slice

            if endInterval < datetime.datetime.now():
                continue   # We never make certificates in the past

            if startInterval > endFrame:
                continue   # Don't make the certs after the lead time

            #print("   ", startInterval, endInterval)
            returns.append(startInterval)
            returns.append(endInterval)

    return returns


def checkExistingCert(certificates, start, end):
    return start, end, 0


def EnqueueCertificates(certificates, cType, name, quantum, load, lead, existing, s, e):
    queued = {
        'Enqueued': True,
        'CertType': cType,
        'CertClass': name,
        'Quantum': float(quantum),
        'Lead-Time': float(lead),
        'Existing': int(existing),
        'Load': int(load),
        'Start': s,
        'Stop': e
    }

    certificates.append(queued)

def GenerateNewCerts(workQueue):
    rootConfig = workQueue.rootConfig
    locale = rootConfig['Locale']

    for certToMake in workQueue.certificates:
        if not 'Enqueued' in certToMake:
            continue
        if not certToMake['Enqueued']:
            continue

    print("Create: ", certToMake)

    # Generate the private key (Elliptical 25519 - don't use RSA)

    key = Ed25519PrivateKey.generate()

    #k = Crypto.PKey()
    #k.generate_key(Crypto.TYPE_, 4096)

    # Pregenerate some important fields

    serialnumber = random.getrandbits(64)

    id = uuid.uuid4()

    CN = str(id) + '@' + rootConfig['Domain']
    O = rootConfig['Manufacturer-Id'] + '@' + rootConfig['Domain']
    OU = str(id) + ' / ' + \
        certToMake['CertType'] + ' / ' + certToMake['CertClass']
    C = locale['Country']
    ST = locale['State']
    L = locale['City']

    # create the csr

    # there will be a difference between the roots and the signers (intermediates)

    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, C),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, ST),
        x509.NameAttribute(NameOID.LOCALITY_NAME, L),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, O),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, OU),
        x509.NameAttribute(NameOID.COMMON_NAME, CN)])

    # There's probably several other fields here we can support, though maybe not for root
    # or signers.  The Kudo servers can use them

    csr = x509.CertificateBuilder()   \
        .subject_name(subject) \
        .public_key(key.public_key())   \
        .serialnumber(serialnumber )    \
        .not_valid_before(certToMake['Start'])  \
        .not_valid_after(certToMake['Stop'])

    # these need some extensions - not sure which yet
    # one, for sure, is that they can sign for time-ranges outside of their span
    # signing cert is the one that's valid for today, but it may be that the thing that's
    # getting signed is somewhat in the future - this is about managing the CRLs

    # Retreive the root (whichever span is currently valid), or self-sign

    # if signing from root, retreive the issuer so it can be put on the csr

    # Save the values (uncrypted) on the work-list


def FindCertificates(cType, name,  certificates, quantum, load, lead):
    # Compute the slice map from the quantum and the lead-time

    sliceMap = getYearMap(quantum, lead)
    # print(sliceMap)

    for i in range(0, len(sliceMap), 2):
        sliceStart = sliceMap[i]
        sliceEnd = sliceMap[i+1]

        s, e, existing = checkExistingCert(certificates, sliceStart, sliceEnd)

        if s == None:
            continue

        EnqueueCertificates(certificates, cType, name, quantum,
                            load, lead, existing, s, e)
