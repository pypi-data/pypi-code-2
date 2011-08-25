import BaseHTTPServer
import errno
import hashlib
import httplib
import json
import os
import urllib2
import random
import shutil
import socket
import tempfile
import threading
import time
import unittest
import slapos.libnetworkcache
import slapos.signature


class NCHandler(BaseHTTPServer.BaseHTTPRequestHandler):
  def __init__(self, request, address, server):
    self.__server = server
    self.tree = server.tree
    BaseHTTPServer.BaseHTTPRequestHandler.__init__(
      self, request, address, server)

  def do_KILL(self):
    raise SystemExit

  def do_GET(self):
    path = os.path.abspath(os.path.join(self.tree, *self.path.split('/')))
    if not (
      ((path == self.tree) or path.startswith(self.tree + os.path.sep))
      and
      os.path.exists(path)
      ):
      self.send_response(404, 'Not Found')
      return
    self.send_response(200)
    out = open(path, 'rb').read()
    self.send_header('Content-Length', len(out))
    self.end_headers()
    self.wfile.write(out)

  def do_PUT(self):
    path = os.path.abspath(os.path.join(self.tree, *self.path.split('/')))
    if not os.path.exists(os.path.dirname(path)):
      os.makedirs(os.path.dirname(path))
    data = self.rfile.read(int(self.headers.getheader('content-length')))
    cksum = hashlib.sha512(data).hexdigest()
    if 'shadir' in path:
      d = json.loads(data)
      data = json.dumps([d])
      if os.path.exists(path):
        f = open(path, 'r')
        try:
          file_data = f.read()
        finally:
          f.close()
        file_data = file_data.strip()
        json_data_list = json.loads(file_data)
        json_data_list.append(d)
        data = json.dumps(json_data_list)
    else:
      raise ValueError('shacache shall use POST')

    open(path, 'wb').write(data)
    self.send_response(201)
    self.send_header('Content-Length', str(len(cksum)))
    self.send_header('Content-Type', 'text/html')
    self.end_headers()
    self.wfile.write(cksum)
    return

  def do_POST(self):
    path = os.path.abspath(os.path.join(self.tree, *self.path.split('/')))
    if not os.path.exists(path):
      os.makedirs(path)
    data = self.rfile.read(int(self.headers.getheader('content-length')))
    cksum = hashlib.sha512(data).hexdigest()
    if 'shadir' in path:
      raise ValueError('shadir shall use PUT')
    else:
      path = os.path.join(path, cksum)

    open(path, 'wb').write(data)
    self.send_response(201)
    self.send_header('Content-Length', str(len(cksum)))
    self.send_header('Content-Type', 'text/html')
    self.end_headers()
    self.wfile.write(cksum)
    return


class NCHandlerPOST200(NCHandler):
  def do_POST(self):
    self.send_response(200)
    return


class NCHandlerReturnWrong(NCHandler):
  def do_POST(self):
    cksum = 'incorrect'
    self.send_response(201)
    self.send_header('Content-Length', str(len(cksum)))
    self.send_header('Content-Type', 'text/html')
    self.end_headers()
    self.wfile.write(cksum)
    return


class Server(BaseHTTPServer.HTTPServer):
  def __init__(self, tree, *args):
    BaseHTTPServer.HTTPServer.__init__(self, *args)
    self.tree = os.path.abspath(tree)

  __run = True

  def serve_forever(self):
    while self.__run:
      self.handle_request()

  def handle_error(self, *_):
    self.__run = False


def _run_nc(tree, host, port):
  server_address = (host, port)
  httpd = Server(tree, server_address, NCHandler)
  httpd.serve_forever()


class OfflineTest(unittest.TestCase):
  def test_download_offline(self):
    nc = slapos.libnetworkcache.NetworkcacheClient('http://127.0.0.1:0',
      'http://127.0.0.1:0')
    self.assertRaises(IOError, nc.download, 'sha512sum')

  def test_upload_offline(self):
    content = tempfile.TemporaryFile()
    nc = slapos.libnetworkcache.NetworkcacheClient('http://127.0.0.1:0',
      'http://127.0.0.1:0')
    self.assertRaises(IOError, nc.upload, content)


def wait(host, port):
  addr = host, port
  for i in range(120):
    time.sleep(0.25)
    try:
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.connect(addr)
      s.close()
      break
    except socket.error, e:
      if e[0] not in (errno.ECONNREFUSED, errno.ECONNRESET):
         raise
      s.close()
    else:
      raise


class OnlineMixin:
  def _start_nc(self):
    self.thread = threading.Thread(target=_run_nc, args=(self.tree,
      self.host, self.port))
    self.thread.setDaemon(True)
    self.thread.start()
    wait(self.host, self.port)

  def setUp(self):
    self.host = "127.0.0.1"
    self.port = 8080
    self.url = 'http://%s:%s/' % (self.host, self.port)
    self.shacache = os.environ.get('TEST_SHA_CACHE',
      self.url + 'shacache')
    self.shadir = os.environ.get('TEST_SHA_DIR',
      self.url + 'shadir')
    if not 'TEST_SHA_CACHE' in os.environ and not 'TEST_SHA_DIR' in os.environ:
      self.tree = tempfile.mkdtemp()
      self._start_nc()
    self.test_data = tempfile.TemporaryFile()
    self.test_string = str(random.random())
    self.test_data.write(self.test_string)
    self.test_data.seek(0)
    self.test_shasum = hashlib.sha512(self.test_data.read()).hexdigest()
    self.test_data.seek(0)

  def tearDown(self):
    if not 'TEST_SHA_CACHE' in os.environ and not 'TEST_SHA_DIR' in os.environ:
      try:
        httplib.HTTPConnection(self.host, self.port).request('KILL', '/')
      except Exception:
        pass

      if self.thread is not None:
        self.thread.join()
      shutil.rmtree(self.tree)


class OnlineTest(OnlineMixin, unittest.TestCase):
  """Online tests against real HTTP server"""
  def test_upload(self):
    nc = slapos.libnetworkcache.NetworkcacheClient(self.shacache, self.shadir)
    nc.upload(self.test_data)

  def test_upload_shadir(self):
    """Check scenario with shadir used"""
    nc = slapos.libnetworkcache.NetworkcacheClient(self.shacache, self.shadir)
    urlmd5 = str(random.random())
    nc.upload(self.test_data, 'mykey', urlmd5=urlmd5, file_name='my file')

  def test_upload_shadir_select(self):
    """Check scenario with shadir used"""
    nc = slapos.libnetworkcache.NetworkcacheClient(self.shacache, self.shadir)
    urlmd5 = str(random.random())
    key = 'somekey' + str(random.random())
    nc.upload(self.test_data, key, urlmd5=urlmd5, file_name='my file')
    result = nc.select(key)
    self.assertEqual(result.read(), self.test_string)

  def test_upload_shadir_select_not_exists(self):
    """Check scenario with shadir used"""
    nc = slapos.libnetworkcache.NetworkcacheClient(self.shacache, self.shadir)
    urlmd5 = str(random.random())
    key = 'somekey' + str(random.random())
    nc.upload(self.test_data, key, urlmd5=urlmd5, file_name='my file')
    try:
      nc.select('key_another_key' + str(random.random()))
    except urllib2.HTTPError, error:
      self.assertEqual(error.code, httplib.NOT_FOUND)

  def test_upload_shadir_no_filename(self):
    """Check scenario with shadir used, but not filename passed"""
    nc = slapos.libnetworkcache.NetworkcacheClient(self.shacache, self.shadir)
    urlmd5 = str(random.random())
    self.assertRaises(ValueError, nc.upload, self.test_data, 'somekey',
      urlmd5)

  def test_upload_twice_same(self):
    nc = slapos.libnetworkcache.NetworkcacheClient(self.shacache, self.shadir)
    nc.upload(self.test_data)
    self.test_data.seek(0)
    nc.upload(self.test_data)

  def test_download(self):
    # prepare some test data

    nc = slapos.libnetworkcache.NetworkcacheClient(self.shacache, self.shadir)

    # upload them
    nc.upload(self.test_data)

    # now try to download them
    result = nc.download(self.test_shasum)

    # is it correctly downloaded
    self.assertEqual(result.read(), self.test_string)

  def test_download_not_exists(self):
    nc = slapos.libnetworkcache.NetworkcacheClient(self.shacache, self.shadir)
    try:
      nc.download(self.test_shasum)
    except urllib2.HTTPError, error:
      self.assertEqual(error.code, httplib.NOT_FOUND)


  def test_select_DirectoryNotFound_too_many_for_key(self):
    nc = slapos.libnetworkcache.NetworkcacheClient(self.shacache, self.shadir)
    key = 'somekey' + str(random.random())
    urlmd5 = str(random.random())
    file_name='my file'
    test_data = tempfile.TemporaryFile()
    test_string = str(random.random())
    test_data.write(test_string)
    test_data.seek(0)
    nc.upload(self.test_data, key, urlmd5=urlmd5, file_name=file_name)
    nc.upload(test_data, key, urlmd5=urlmd5, file_name=file_name)
    try:
      nc.select(key)
    except slapos.libnetworkcache.DirectoryNotFound, msg:
      self.assertTrue(
        str(msg).startswith("Too many entries for a given key %r"% key))

  def test_DirectoryNotFound_non_trustable_entry(self):
    key = """-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQDDrOO87nSiDcXOf+xGc4Iqcdjfwd0RTOxEkO9z8mPZVg2bTPwt
/GwtPgmIC4po3bJdsCpJH21ZJwfmUpaQWIApj3odDAbRXQHWhNiw9ZPMHTCmf8Zl
yAJBxy9KI9M/fJ5RA67CJ6UYFbpF7+ZrXdkvG+0hdRX5ub0WyTPxc6kEIwIDAQAB
AoGBAIgUj1jQGKqum1bt3dps8CQmgqWyA9TJQzK3/N8MveXik5niYypz9qNMFoLX
S818CFRhdDbgNUKgAz1pSC5gbdfCDHYQTBrIt+LGpNSpdmQwReu3XoWOPZp4VWnO
uCpAkDVt+88wbxtMbZ5/ExNFs2xTO66Aad1dG12tPWoyAf4pAkEA4tCLPFNxHGPx
tluZXyWwJfVZEwLLzJ9gPkYtWrq843JuKlai2ziroubVLGSxeovBXvsjxBX95khn
U6G9Nz5EzwJBANzal8zebFdFfiN1DAyGQ4QYsmz+NsRXDbHqFVepymUId1jAFAp8
RqNt3Y78XlWOj8z5zMd4kWAR62p6LxJcyG0CQAjCaw4qXszs4zHaucKd7v6YShdc
3UgKw6nEBg5h9deG3NBPxjxXJPHGnmb3gI8uBIrJgikZfFO/ahYlwev3QKsCQGJ0
kHekMGg3cqQb6eMrd63L1L8CFSgyJsjJsfoCl1ezDoFiH40NGfCBaeP0XZmGlFSs
h73k4eoSEwDEt3dYJYECQQCBssN92KuYCOfPkJ+OV1tKdJdAsNwI13kA//A7s7qv
wHQpWKk/PLmpICMBeIiE0xT+CmCfJVOlQrqDdujganZZ
-----END RSA PRIVATE KEY-----
"""
    key_file = tempfile.NamedTemporaryFile()
    key_file.write(key)
    key_file.flush()
    key_file.seek(0)

    certificate = """-----BEGIN CERTIFICATE-----
MIICgDCCAekCADANBgkqhkiG9w0BAQsFADCBiDELMAkGA1UEBhMCVUwxETAPBgNV
BAgTCEJlZSBZYXJkMRgwFgYDVQQKEw9CZWUtS2VlcGVyIEx0ZC4xGDAWBgNVBAsT
D0hvbmV5IEhhcnZlc3RlcjEVMBMGA1UEAxMMTWF5YSB0aGUgQmVlMRswGQYJKoZI
hvcNAQkBFgxNYXlhIHRoZSBCZWUwHhcNMTEwODI0MDc1MTU2WhcNMTIwODI0MDc1
MTU2WjCBiDELMAkGA1UEBhMCVUwxETAPBgNVBAgTCEJlZSBZYXJkMRgwFgYDVQQK
Ew9CZWUtS2VlcGVyIEx0ZC4xGDAWBgNVBAsTD0hvbmV5IEhhcnZlc3RlcjEVMBMG
A1UEAxMMTWF5YSB0aGUgQmVlMRswGQYJKoZIhvcNAQkBFgxNYXlhIHRoZSBCZWUw
gZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBAMOs47zudKINxc5/7EZzgipx2N/B
3RFM7ESQ73PyY9lWDZtM/C38bC0+CYgLimjdsl2wKkkfbVknB+ZSlpBYgCmPeh0M
BtFdAdaE2LD1k8wdMKZ/xmXIAkHHL0oj0z98nlEDrsInpRgVukXv5mtd2S8b7SF1
Ffm5vRbJM/FzqQQjAgMBAAEwDQYJKoZIhvcNAQELBQADgYEAaT4yamJJowDKMSD2
eshUW8pjctg6O3Ncm5XDIKd77sRf7RwPjFh+BR59lfFf9xvOu8WymhtUU7FoPDW3
MYZmKV7A3nFehN9A+REz+WU3I7fE6vQRh9jKeuxnQLRv0TdP9CEdPcYcs/EQpIDb
8du+N7wcN1ZO8veWSafBzcqgCwg=
-----END CERTIFICATE-----
"""

    nc = slapos.libnetworkcache.NetworkcacheClient(self.shacache, self.shadir)
    key = 'somekey' + str(random.random())
    urlmd5 = str(random.random())
    file_name='my file'
    nc.upload(self.test_data, key, urlmd5=urlmd5, file_name=file_name)
    signed_nc = slapos.libnetworkcache.NetworkcacheClient(
      self.shacache, self.shadir, signature_certificate_list=[certificate])
    # when no signature is used, all works ok
    selected = nc.select(key).read()
    self.assertEqual(selected, self.test_string)
    # but when signature is used, networkcache will complain
    try:
      signed_nc.select(key)
    except slapos.libnetworkcache.DirectoryNotFound, msg:
      self.assertEqual(str(msg), 'Could not find a trustable entry.')

    # of course if proper key will be used to sign the content uploaded
    # into shacache all will work
    upload_nc = slapos.libnetworkcache.NetworkcacheClient(self.shacache,
      self.shadir, signature_private_key_file=key_file.name)
    upload_nc.upload(self.test_data, key, urlmd5=urlmd5, file_name=file_name)
    selected = signed_nc.select(key).read()
    self.assertEqual(selected, self.test_string)

def _run_nc_POST200(tree, host, port):
  server_address = (host, port)
  httpd = Server(tree, server_address, NCHandlerPOST200)
  httpd.serve_forever()


class OnlineTestPOST200(OnlineMixin, unittest.TestCase):
  def _start_nc(self):
    self.thread = threading.Thread(target=_run_nc_POST200, args=(self.tree,
      self.host, self.port))
    self.thread.setDaemon(True)
    self.thread.start()
    wait(self.host, self.port)

  def test_upload_wrong_return_code(self):
    """Check reaction on HTTP return code different then 201"""
    nc = slapos.libnetworkcache.NetworkcacheClient(self.shacache, self.shadir)
    self.assertRaises(slapos.libnetworkcache.UploadError, nc.upload,
      self.test_data)


def _run_nc_POSTWrongChecksum(tree, host, port):
  server_address = (host, port)
  httpd = Server(tree, server_address, NCHandlerReturnWrong)
  httpd.serve_forever()


class OnlineTestWrongChecksum(OnlineMixin, unittest.TestCase):
  def _start_nc(self):
    self.thread = threading.Thread(target=_run_nc_POSTWrongChecksum,
      args=(self.tree, self.host, self.port))
    self.thread.setDaemon(True)
    self.thread.start()
    wait(self.host, self.port)

  def test_upload_wrong_return_sha(self):
    """Check reaction in case of wrong sha returned"""
    nc = slapos.libnetworkcache.NetworkcacheClient(self.shacache, self.shadir)
    self.assertRaises(slapos.libnetworkcache.UploadError, nc.upload,
      self.test_data)


class LibNetworkCacheMixin(unittest.TestCase):

  def setUp(self):
    ''' Setup the test. '''
    self.pub_file_descriptor = tempfile.NamedTemporaryFile()
    self.priv_file_descritor = tempfile.NamedTemporaryFile()
    self.signature_certificate_file = self.pub_file_descriptor.name
    self.signature_private_key_file = self.priv_file_descritor.name
    self.signature_creation_argument_list = \
        ('--signature-certificate-file', self.signature_certificate_file,
         '--signature-private-key-file', self.signature_private_key_file,
         '--country', 'BR',
         '--state-name', 'Campos',
         '--locality-name', 'Rio de Janeiro',
         '--organization-name', 'Nexedi',
         '--organization-unit-name', 'Dev',
         '--common-name', 'R500.com',
         '--email', 'test@example.com')
    self.option_dict = slapos.signature.parseArgument(
      *self.signature_creation_argument_list)
    self.cert_as_text = slapos.signature.createPrivateKeyAndCertificateFile(
      **self.option_dict)

  def tearDown(self):
    ''' Remove the files which have been created during the test. '''
    self.priv_file_descritor.close()
    self.pub_file_descriptor.close()


class GenerateSignatureScriptTest(LibNetworkCacheMixin):
  ''' Class which must test the signature.py script. '''

  def test_parse_argument_with_empty_list(self):
    '''
      If the argument list is empty, then the parseArgument method should
    return a dictionary with default argument values.
    '''
    default_dict = {'organization_name': 'Default Company Ltd',
                    'state_name': 'Default Province',
                    'organization_unit_name': '',
                    'common_name': '',
                    'country': 'XX',
                    'locality_name': 'Default City',
                    'signature_private_key_file': 'private.pem',
                    'signature_certificate_file': 'public.pem',
                    'email': ''}
    self.assertEquals(default_dict, slapos.signature.parseArgument())

  def test_parse_argument(self):
    '''
      Check if the argument is properly set.
    '''
    size_argument_list = len(self.signature_creation_argument_list) / 2
    size_option_dict = len(self.option_dict)
    self.assertEquals(size_argument_list, size_option_dict,
        "Argument list should have the same size of option dict.")

    # Assert if the values are equals.
    for value in self.option_dict.values():
      self.assertTrue(value in self.signature_creation_argument_list,\
          '%s is not in %s.' % (value, self.signature_creation_argument_list))

  def test_key_and_certificate_file_creation(self):
    '''
      Check if key file and the certificate file are being created correctly.
    '''
    self.assertTrue(os.path.exists(self.signature_certificate_file))
    self.assertTrue(os.path.exists(self.signature_private_key_file))


class TestNetworkcacheClient(LibNetworkCacheMixin):
  """
    Class to test the slapos.libnetworkcache.NetworkcacheClient implementation.
  """

  def setUp(self):
    """ Setup the test. """
    LibNetworkCacheMixin.setUp(self)
    self.host = 'localhost'
    self.port = 8000
    self.shacache_path = '/shacache'
    self.shadir_path = '/shadir'
    url = 'http://%s:%s' % (self.host, self.port)
    self.shacache_url = url + self.shacache_path
    self.shadir_url = url + self.shadir_path

  def test_init_backward_compatible(self):
    """Checks that invocation with minimal parameter works fine"""
    nc = slapos.libnetworkcache.NetworkcacheClient(shacache=self.shacache_url,
                                 shadir=self.shadir_url)
    self.assertEqual(nc.shacache_url, self.shacache_url)
    self.assertTrue(nc.shadir_host in self.shadir_url)

  def test_init_method_normal_http_url(self):
    """
      Check if the init method is setting the attributes correctly.
    """
    nc = slapos.libnetworkcache.NetworkcacheClient(shacache=self.shacache_url,
                                 shadir=self.shadir_url)
    self.assertEquals({'Content-Type': 'application/json'}, \
                          nc.shacache_header_dict)
    self.assertEquals(self.host, nc.shacache_host)
    self.assertEquals(self.shacache_path, nc.shacache_path)
    self.assertEquals(self.port, nc.shacache_port)
    self.assertEquals(self.shacache_url, nc.shacache_url)

    self.assertEquals({'Content-Type': 'application/json'}, \
                         nc.shadir_header_dict)
    self.assertEquals(self.host, nc.shadir_host)
    self.assertEquals(self.shadir_path, nc.shadir_path)
    self.assertEquals(self.port, nc.shadir_port)

  def test_signature_creation_without_private_key_file(self):
    """
      Without the private key file, it is not possible to create the
      signature so it must return an empty string.
    """
    nc = slapos.libnetworkcache.NetworkcacheClient(shacache=self.shacache_url,
                                 shadir=self.shadir_url)
    self.assertEquals('', nc._getSignatureString())

  def test_signature_creation_with_private_key_file(self):
    """
      Check if the signature creation does not have any error.
    """
    nc = slapos.libnetworkcache.NetworkcacheClient(
                   shacache=self.shacache_url,
                   shadir=self.shadir_url,
                   signature_private_key_file=self.signature_private_key_file)
    self.assertNotEquals('', nc._getSignatureString())

  def test_verification_without_signature_certificate_list(self):
    """
      Without the signature certificate list it is not possible to
      verify if the signature if trusted or not.
      So, the _verifySignatureInCertificateList should return False.
    """
    nc = slapos.libnetworkcache.NetworkcacheClient(
             shacache=self.shacache_url,
             shadir=self.shadir_url,
             signature_private_key_file=self.signature_private_key_file)
    signature_string = nc._getSignatureString()
    self.assertFalse(nc._verifySignatureInCertificateList(signature_string))

  def test_verification_with_signature_certificate_list(self):
    """
      With the signature certificate list it is possible to
      verify if the signature if trusted or not.

      So, the _verifySignatureInCertificateList should return True
      if the signature_string is valid and it should return False if the
      signature_string is not correct.
    """
    nc = slapos.libnetworkcache.NetworkcacheClient(
             shacache=self.shacache_url,
             shadir=self.shadir_url,
             signature_private_key_file=self.signature_private_key_file,
             signature_certificate_list=[
              open(self.signature_certificate_file).read()])
    signature_string = nc._getSignatureString()
    self.assertTrue(nc._verifySignatureInCertificateList(signature_string))

    wrong_signature_string = 'InvalidSignatureString'.encode('base64')
    result_bool = nc._verifySignatureInCertificateList(wrong_signature_string)
    self.assertFalse(result_bool)
