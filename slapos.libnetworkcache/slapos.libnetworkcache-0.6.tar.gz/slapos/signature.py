##############################################################################
#
# Copyright (c) 2010 ViFiB SARL and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################


import M2Crypto
import time
import argparse
import sys


def createPrivateKeyAndCertificateFile(signature_certificate_file, signature_private_key_file, **kw):
  ''' It must create a private key and a certificate file. '''
  cur_time = M2Crypto.ASN1.ASN1_UTCTIME()
  cur_time.set_time(int(time.time()) - 60*60*24)
  expire_time = M2Crypto.ASN1.ASN1_UTCTIME()
  expire_time.set_time(int(time.time()) + 60 * 60 * 24 * 365)

  cs_rsa = M2Crypto.RSA.gen_key(1024, 65537, lambda: None)
  cs_pk = M2Crypto.EVP.PKey()
  cs_pk.assign_rsa(cs_rsa)

  cs_cert = M2Crypto.X509.X509()
  cs_cert.set_not_before(cur_time)
  cs_cert.set_not_after(expire_time)
  cs_cert.set_pubkey(cs_pk)

  cs_name = M2Crypto.X509.X509_Name()
  cs_name.C = kw.get('country', '')
  cs_name.SP = kw.get('state_name', '')
  cs_name.L = kw.get('locality', '')
  cs_name.O = kw.get('organization_name', '')
  cs_name.OU = kw.get('organization_unit_name', '')
  cs_name.CN = kw.get('common_name', '')
  cs_name.Email = kw.get('common_name', '')

  cs_cert.set_subject(cs_name)
  cs_cert.set_issuer_name(cs_name)
  cs_cert.sign(cs_pk, md="sha256")

  # Saving...
  cs_cert.save_pem(signature_certificate_file)
  cs_rsa.save_pem(signature_private_key_file, None)
  return cs_cert.as_text()


def parseArgument(*args):
  ''' Parses command line arguments. '''
  parser = argparse.ArgumentParser()
  parser.add_argument('--signature-certificate-file',
                      default='public.pem',
                      help='X509 Cetification file.')

  parser.add_argument('--signature-private-key-file',
                      default='private.pem',
                      help='Signature private key file.')

  parser.add_argument('-c','--country',
                      default='XX',
                      help='Country Name (2 letter code).')

  parser.add_argument('-s', '--state-name',
                      default='Default Province',
                      help='State or Province Name (full name).')

  parser.add_argument('-l', '--locality-name',
                      default='Default City',
                      help='Locality Name (eg, city).')

  parser.add_argument('-o', '--organization-name',
                      default='Default Company Ltd',
                      help='Organization Name (eg, company).')

  parser.add_argument('-ou', '--organization-unit-name',
                      default='',
                      help='Organizational Unit Name (eg, section).')

  parser.add_argument('-cn', '--common-name',
                      default='',
                      help="Common Name (eg, your name or your server's " \
                           "hostname).")

  parser.add_argument('-e', '--email',
                      default='',
                      help='Email Address.')

  argument_option_instance = parser.parse_args(list(args))
  option_dict = {}
  for argument_key, argument_value in vars(argument_option_instance
      ).iteritems():
    if argument_value is not None:
      option_dict.update({argument_key: argument_value})

  return option_dict


def run():
  ''' Validate the parameters and call the function to create
    private key and certificate file.
  '''
  option_dict = parseArgument(*sys.argv[1:])
  print createPrivateKeyAndCertificateFile(**option_dict)
