import unittest
from slapos.libnetworkcache import NetworkcacheClient
import tempfile

class OfflineTest(unittest.TestCase):
  def test_download_offline(self):
    nc = NetworkcacheClient('http://127.0.0.1:0', 'http://127.0.0.1:0')
    self.assertRaises(IOError, nc.download, 'sha512sum')

  def test_upload_offline(self):
    content = tempfile.TemporaryFile()
    nc = NetworkcacheClient('http://127.0.0.1:0', 'http://127.0.0.1:0')
    self.assertRaises(IOError, nc.upload, content)
