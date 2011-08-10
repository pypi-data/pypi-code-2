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


import base64
import hashlib
import httplib
import json
import os
import tempfile
import urllib
import urllib2
import urlparse
import M2Crypto
import socket


class NetworkcacheClient(object):
  '''
    NetworkcacheClient is a wrapper for httplib.
    It must implement all the required methods to use:
     - SHADIR
     - SHACACHE
  '''

  def parseUrl(self, url):
    return_dict = {}
    parsed_url = urlparse.urlparse(url)
    return_dict['header_dict'] = {'Content-Type': 'application/json'}
    user = parsed_url.username
    passwd = parsed_url.password
    if user is not None:
      authentication_string = '%s:%s' % (user, passwd)
      base64string = base64.encodestring(authentication_string).strip()
      return_dict['header_dict']['Authorization'] = 'Basic %s' %\
        base64string

    return_dict['path'] = parsed_url.path
    return_dict['host'] = parsed_url.hostname
    return_dict['scheme'] = parsed_url.scheme
    return_dict['port'] = parsed_url.port or \
                           socket.getservbyname(parsed_url.scheme)

    return return_dict

  def __init__(self, shacache, shadir,
               signature_private_key_file=None,
               signature_certificate_file_list=None):
    ''' Set the initial values. '''
    # ShaCache Properties
    for k, v in self.parseUrl(shacache).iteritems():
      setattr(self, 'shacache_%s' % k, v)
    self.shacache_url = shacache

    # ShaDir Properties
    for k, v in self.parseUrl(shadir).iteritems():
      setattr(self, 'shadir_%s' % k, v)

    self.signature_private_key_file = signature_private_key_file

    self.signature_certificate_file_list = []
    self.signature_certificate_url_list = []
    if signature_certificate_file_list is not None:
      # Split the path and urls
      for value in signature_certificate_file_list:
        if os.path.exists(value):
          self.signature_certificate_file_list.append(value)
        elif value.startswith('http'):
          self.signature_certificate_url_list.append(value)

  def upload(self, file_descriptor, directory_key=None, **kw):
    ''' Upload the file to the server.
    If directory_key is None it must only upload to SHACACHE.
    Otherwise, it must create a new entry on SHADIR.
    '''
    if directory_key is not None and 'urlmd5' not in kw:
      msg = 'The parameter "urlmd5" is required once you set directory_key.'
      raise ValueError(msg)

    sha512sum = hashlib.sha512()
    # do not trust, go to beginning of opened file
    file_descriptor.seek(0)
    while True:
      d = file_descriptor.read(sha512sum.block_size)
      if not d:
        break
      sha512sum.update(d)
    sha512sum = sha512sum.hexdigest()
    path = os.path.join(self.shacache_path, sha512sum)

    file_descriptor.seek(0)
    shacache_connection = httplib.HTTPConnection(self.shacache_host,
      self.shacache_port)
    try:
      shacache_connection.request('PUT', path, file_descriptor,
                                                 self.shacache_header_dict)
      result = shacache_connection.getresponse()
      data = result.read()
    finally:
      shacache_connection.close()

    if result.status != 201:
      raise UploadError('Failed to upload the file to SHACACHE Server.' \
                        'URL: %s. Response code: %s. Response data: %s' % \
                                   (self.shacache_host, result.status, data))

    if directory_key is not None:
      path = os.path.join(self.shadir_path, directory_key)

      file_name = kw.get('file', None)
      if file_name is None:
        kw['file'] = os.path.basename(file_descriptor.name)

      sha512 = kw.get('sha512', None)
      if sha512 is None:
        kw['sha512'] = sha512sum

      signature = self._getSignatureString()
      data = [kw, signature]

      shadir_connection = httplib.HTTPConnection(self.shadir_host,
        self.shadir_port)
      try:
        shadir_connection.request('PUT', path, json.dumps(data),
                                                 self.shadir_header_dict)
        result = shadir_connection.getresponse()
        data = result.read()
      finally:
        shadir_connection.close()

      if result.status != 201:
        raise UploadError('Failed to upload data to SHADIR Server.' \
                          'URL: %s. Response code: %s. Response data: %s' % \
                                     (self.shacache_host, result.status, data))
    return True

  def download(self, sha512sum):
    ''' Download the file.
    It uses http GET request method.
    '''
    sha_cache_url = os.path.join(self.shacache_url, sha512sum)
    file_descriptor = tempfile.NamedTemporaryFile()
    path, headers = urllib.urlretrieve(sha_cache_url, file_descriptor.name)
    file_descriptor.seek(0)
    return file_descriptor

  def select(self, directory_key=None):
    ''' Download a file from shacache by selecting the entry in shadir
    Raise DirectoryNotFound if multiple files are found.
    '''
    path_info = self.shadir_path
    if directory_key is not None:
      path_info = os.path.join(self.shadir_path, directory_key)

    url = "http://%s:%s%s" % (self.shadir_host, self.shadir_port, path_info)
    request = urllib2.Request(url=url, data=None,headers=self.shadir_header_dict)
    try:
      result = urllib2.urlopen(request)
      data = result.read()
    except urllib2.HTTPError, error:
      raise DirectoryNotFound("%s : %s" % (error.code, error.msg))

    # Filtering...
    data_list = json.loads(data)
    if len(data_list) > 1 and not \
         (self.signature_certificate_file_list or \
          self.signature_certificate_url_list):
      raise DirectoryNotFound('Too many entries for a given directory. ' \
               'Directory: %s. Entries: %s.' % (directory_key, str(data_list)))

    if self.signature_certificate_file_list or \
         self.signature_certificate_url_list:
      method = self._verifySignatureInCertificateList
      data_list = filter(lambda x: method(x[1]), data_list)
      if len(data_list) > 1:
        raise DirectoryNotFound('Too many entries for a given key. ' \
               'Directory: %s. Entries: %s.' %(directory_key, str(data_list)))

      if not data_list:
        raise DirectoryNotFound('Could not find a trustable entry.')

    information_dict, signature = data_list[0]
    sha512 = information_dict.get('sha512')
    return self.download(sha512)

  def _getSignatureString(self):
    """
      Return the signature based on certification file.
    """
    if not self.signature_private_key_file:
      return ''

    SignEVP = M2Crypto.EVP.load_key(self.signature_private_key_file)
    SignEVP.sign_init()
    SignEVP.sign_update('')
    StringSignature = SignEVP.sign_final()
    return StringSignature.encode('base64')

  def _verifySignatureInCertificateList(self, signature_string):
    """
      Returns true if it can find any valid certificate or false if it does not
      find any.

      It must check the local certificate files first before checking the files
      which are available under HTTP.
    """
    for certificate_path in self.signature_certificate_file_list:
      if self._verifySignatureCertificate(signature_string, certificate_path):
        return True

    for certificate_url in self.signature_certificate_url_list:
      file_descriptor = self._fetchCertificateFileFromUrl(certificate_url)
      try:
        file_name = file_descriptor.name
        if self._verifySignatureCertificate(signature_string, file_name):
          return True
      finally:
        file_descriptor.close()

    return False

  def _verifySignatureCertificate(self, signature_string, certificate_path):
    """ verify if the signature is valid for a given certificate. """
    PubKey = M2Crypto.X509.load_cert(certificate_path)
    VerifyEVP = M2Crypto.EVP.PKey()
    VerifyEVP.assign_rsa(PubKey.get_pubkey().get_rsa())
    VerifyEVP.verify_init()
    VerifyEVP.verify_update('')
    return VerifyEVP.verify_final(signature_string.decode('base64'))

  def _fetchCertificateFileFromUrl(self, certification_file_url):
    """ Download the certification files from the url. """
    file_descriptor = tempfile.NamedTemporaryFile()
    path, headers = urllib.urlretrieve(certification_file_url, file_descriptor.name)
    file_descriptor.seek(0)
    return file_descriptor



class DirectoryNotFound(Exception):
  pass


class UploadError(Exception):
  pass
