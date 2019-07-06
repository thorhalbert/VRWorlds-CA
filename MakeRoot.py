#!/usr/bin/env python3

# from OpenSSL
import Crypto
import SSL
from os.path import join
import random

CN = input("Enter the common name of the certificate you want: ")
pubkey = "%s.crt" % CN  # replace %s with CN
privkey = "%s.key" % CN  # replcate %s with CN

pubkey = join(".", pubkey)
privkey = join(".", privkey)

k = Crypto.PKey()
k.generate_key(Crypto.TYPE_RSA, 2048)
serialnumber = random.getrandbits(64)

# create a self-signed cert
cert = Crypto.X509()
cert.get_subject().C = input("Country: ")
cert.get_subject().ST = input("State: ")
cert.get_subject().L = input("City: ")
cert.get_subject().O = input("Organization: ")
cert.get_subject().OU = input("Organizational Unit: ")
cert.get_subject().CN = CN
cert.set_serial_number(serialnumber)
cert.gmtime_adj_notBefore(0)
cert.gmtime_adj_notAfter(31536000)  # 315360000 is in seconds.
cert.set_issuer(cert.get_subject())
cert.set_pubkey(k)
cert.sign(k, 'sha512')
pub = Crypto.dump_certificate(Crypto.FILETYPE_PEM, cert)
priv = Crypto.dump_privatekey(Crypto.FILETYPE_PEM, k)
open(pubkey, "wt").write(pub.decode("utf-8"))
open(privkey, "wt").write(priv.decode("utf-8"))
