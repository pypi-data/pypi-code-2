import unittest
import tempfile
import os
from slapos.libnetworkcache import NetworkcacheClient
from slapos.signature import parseArgument, \
                             createPrivateKeyAndCertificateFile

class OfflineTest(unittest.TestCase):
  def test_download_offline(self):
    nc = NetworkcacheClient('http://127.0.0.1:0', 'http://127.0.0.1:0')
    self.assertRaises(IOError, nc.download, 'sha512sum')

  def test_upload_offline(self):
    content = tempfile.TemporaryFile()
    nc = NetworkcacheClient('http://127.0.0.1:0', 'http://127.0.0.1:0')
    self.assertRaises(IOError, nc.upload, content)

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
    self.option_dict = parseArgument(*self.signature_creation_argument_list)
    self.cert_as_text = createPrivateKeyAndCertificateFile(**self.option_dict)

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
    self.assertEquals(default_dict, parseArgument())

  def test_parse_argument(self):
    '''
      Check if the argument is properly set.
    '''
    size_argument_list = len(self.signature_creation_argument_list)/2
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
    Class to test the NetworkcacheClient implementation.
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
    # checking the backwards compatibilty
    self.nc = NetworkcacheClient(shacache=self.shacache_url,
                                 shadir=self.shadir_url)

  def test_init_method_normal_http_url(self):
    """
      Check if the init method is setting the attributes correctly.
    """
    self.assertEquals({'Content-Type': 'application/json'}, \
                          self.nc.shacache_header_dict)
    self.assertEquals(self.host, self.nc.shacache_host)
    self.assertEquals(self.shacache_path, self.nc.shacache_path)
    self.assertEquals(self.port, self.nc.shacache_port)
    self.assertEquals(self.shacache_url, self.nc.shacache_url)

    self.assertEquals({'Content-Type': 'application/json'}, \
                         self.nc.shadir_header_dict)
    self.assertEquals(self.host, self.nc.shadir_host)
    self.assertEquals(self.shadir_path, self.nc.shadir_path)
    self.assertEquals(self.port, self.nc.shadir_port)

  def test_signature_creation_without_private_key_file(self):
    """
      Without the private key file, it is not possible to create the
      signature so it must return an empty string.
    """
    self.assertEquals('', self.nc._getSignatureString())

  def test_signature_creation_with_private_key_file(self):
    """
      Check if the signature creation does not have any error.
    """
    nc = NetworkcacheClient(
                   shacache=self.shacache_url,
                   shadir=self.shadir_url,
                   signature_private_key_file=self.signature_private_key_file)
    self.assertNotEquals('', nc._getSignatureString())

  def test_verification_without_signature_certificate_file_list(self):
    """
      Without the signature certificate file list it is not possible to
      verify if the signature if trusted or not.
      So, the _verifySignatureInCertificateList should return False.
    """
    nc = NetworkcacheClient(
             shacache=self.shacache_url,
             shadir=self.shadir_url,
             signature_private_key_file=self.signature_private_key_file)
    signature_string = nc._getSignatureString()
    self.assertFalse(nc._verifySignatureInCertificateList(signature_string))

  def test_verification_with_signature_certificate_file_list(self):
    """
      With the signature certificate file list it is possible to
      verify if the signature if trusted or not.

      So, the _verifySignatureInCertificateList should return True
      if the signature_string is valid and it should return False if the
      signature_string is not correct.
    """
    nc = NetworkcacheClient(
             shacache=self.shacache_url,
             shadir=self.shadir_url,
             signature_private_key_file=self.signature_private_key_file,
             signature_certificate_file_list=[self.signature_certificate_file])
    signature_string = nc._getSignatureString()
    self.assertTrue(nc._verifySignatureInCertificateList(signature_string))

    wrong_signature_string = 'InvalidSignatureString'.encode('base64')
    result_bool = nc._verifySignatureInCertificateList(wrong_signature_string)
    self.assertFalse(result_bool)

  # XXX(lucas): Should we provide the file under HTTP server using
  # SimpleHTTPServer? Because actually it gonna just throw an IOError.
  def test_verification_with_signature_certificate_file_list_url(self):
    """
      NetworkcacheClient supports to have the certification file under an HTTP
      server.

      During the _verifySignatureInCertificateList method, it'll try to
      download the certification from the given URL and check if the signature
      is valid.
    """
    nc = NetworkcacheClient(
             shacache=self.shacache_url,
             shadir=self.shadir_url,
             signature_private_key_file=self.signature_private_key_file,
             signature_certificate_file_list=['http://localhost:0/public.pem'])
    signature_string = nc._getSignatureString()
    self.assertRaises(IOError, \
                        nc._verifySignatureInCertificateList, signature_string)

  def test_signature_verification_priority(self):
    """
      During the signature vefirication, the filesystem path has priority over
      urls. So, if the public key is 
    """
    nc = NetworkcacheClient(
             shacache=self.shacache_url,
             shadir=self.shadir_url,
             signature_private_key_file=self.signature_private_key_file,
             signature_certificate_file_list=['http://localhost:0/public.pem'])
    signature_string = nc._getSignatureString()
    self.assertRaises(IOError, \
                        nc._verifySignatureInCertificateList, signature_string)
