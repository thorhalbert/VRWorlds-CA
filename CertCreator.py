#!/usr/bin/env python3

import time
import uuid
import datetime
import Crypto
import base64

# import SSL
import os
import random

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes

from pprint import pprint


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
    # print("EndFrame=", endFrame)

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

            # print("   ", startInterval, endInterval)
            returns.append(startInterval)
            returns.append(endInterval)

    return returns


def checkExistingCert(certificates, start, end):
    return start, end, 0


def EnqueueCertificates(certificates, cType, name, quantum, load, lead, existing, s, e):
    queued = {
        'Target': name,
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
    for certToMake in workQueue.root_certificates:
        if not 'Enqueued' in certToMake:
            continue
        if not certToMake['Enqueued']:
            continue

        __generateCert(certToMake, workQueue)

    for certToMake in workQueue.certificates:
        if not 'Enqueued' in certToMake:
            continue
        if not certToMake['Enqueued']:
            continue

        __generateCert(certToMake, workQueue)


def __generateCert(certToMake, workQueue):

    rootConfig = workQueue.rootConfig
    locale = rootConfig['Locale']

    # See if we're root and see if we're current root
    iAmRoot = (certToMake['CertClass'] == 'Root')
    if iAmRoot:
        if certToMake['Start'] < datetime.datetime.utcnow() < certToMake['Stop']:
            workQueue.current_root = certToMake

    # Generate the private key (Elliptical 25519 - don't use RSA)

    # key = Ed25519PrivateKey.generate()

    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    certToMake['PrivateKey'] = key

    # k = Crypto.PKey()
    # k.generate_key(Crypto.TYPE_, 4096)

    # Pregenerate some important fields

    serialnumber = random.getrandbits(64)

    id = uuid.uuid4()

    certToMake['Id'] = str(id)
    certToMake['SerialNumber'] = serialnumber

    CN = str(id) + '@' + rootConfig['Domain']
    O = rootConfig['Manufacturer-Id'] + '@' + rootConfig['Domain']
    OU = str(id) + ' / ' + \
        certToMake['CertType'] + ' / ' + certToMake['CertClass']
    C = locale['Country']
    ST = locale['State']
    L = locale['City']

    print("Create: "+OU)
    # pprint(certToMake)

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

    path = 1
    if iAmRoot:
        path = 0    # root ca appearently has a path of 0

    csr = x509.CertificateBuilder()   \
        .subject_name(subject) \
        .public_key(key.public_key())   \
        .serial_number(serialnumber)    \
        .not_valid_before(certToMake['Start'])  \
        .not_valid_after(certToMake['Stop']) \
        .add_extension(x509.BasicConstraints(ca=True, path_length=path), True) \
        .add_extension(x509.KeyUsage(
            digital_signature=True,
            content_commitment=True,
            key_encipherment=False,
            data_encipherment=False,
            key_agreement=False,
            key_cert_sign=True,
            crl_sign=True,
            encipher_only=False,
            decipher_only=False), True)

    private_key = key   # assume self signed for CA (not current root)
    if not iAmRoot:
        if workQueue.current_root is None:
            print("Cannot find the current root cert")
            exit(10)

        root = workQueue.current_root
        # print("Issuer: ",root['CSR'])
        # pprint(root)
        csr = csr.issuer_name(root['Certificate'].issuer)

        # intermediates (even futuredated) must be signed by CURRENT root
        private_key = root['PrivateKey']
    else:
        csr = csr.issuer_name(subject)

    certificate = csr.sign(
        private_key=private_key, algorithm=hashes.SHA256(),
        backend=default_backend())

    # Save the values (uncrypted) on the work-list

    certToMake['Certificate'] = certificate
    certToMake['Persisted'] = False
    certToMake['Enqueued'] = False

    #fn = certToMake['CertType'] + '-'
    #fn += str(id) + ".pem"
    #fn = fn.replace('/','_')

    # with open(fn, "wb") as f:
    #    f.write(certificate.public_bytes(serialization.Encoding.PEM))


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


def GenPassphrase():
    phrase = os.urandom(64)
    return str(uuid.uuid4()), phrase, base64.b64encode(phrase).decode('utf-8')


def ExportCerts(key, output, queue, writePriv):
    print("[Output "+key+'] ')

    for cert in queue:
        # the passphrase uuid id is not actually written to the cert, just the manifest
        
        manifestEntry = {
            'Id': cert['Id'],
            'CertInfo': {
                'Cert-Class': cert['CertClass'],
                'Cert-Type': cert['CertType'],
                'Target': cert['Target'],
                'Lead-Time': cert['Lead-Time'],
                'Load': cert['Load'],
                'Quantum': cert['Quantum'],
                'Valid-From': cert['Start'],
                'Valid-To': cert['Stop']
            }
        }

        fnb = cert['CertType'] + '-' + cert['Id']
        fnb = fnb.replace('/', '_')
        fn = fnb + ".pem"

        manifestEntry['CertificateFile'] = fn

        fnm = os.path.join(output.Tmp, fn)
        print('[Write: '+fnm+']')
        with open(fnm, "wb") as f:
            f.write(cert['Certificate'].public_bytes(
                serialization.Encoding.PEM))

        if writePriv:
            # Get the random passphrase we're going to encrypt the private key with
            phraseKey, phraseBytes, phraseEnc = GenPassphrase()

            fn = fnb + "_key.pem"

            manifestEntry['PhraseKey'] = phraseKey

            manifestEntry['PrivateKeyFile'] = fn

            # Build the passphrase table - this is not encrypted in memory
            output.PassPhrases.append({
                'Key': phraseKey,
                'PhraseEnc': phraseEnc
            })

            fnm = os.path.join(output.Tmp, fn)

            with open(fnm, "wb") as f:
                f.write(cert['PrivateKey'].private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.BestAvailableEncryption(
                        phraseBytes),
                ))

        output.Manifest.append(manifestEntry)
