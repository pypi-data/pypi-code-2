import unittest

# FIXME Our Windows build server does not support GStreamer yet
import sys
if sys.platform == 'win32':
    from tests import SkipTest
    raise SkipTest

from mopidy import settings
from mopidy.backends.local import LocalBackend
from mopidy.models import Track

from tests.backends.base.current_playlist import \
    BaseCurrentPlaylistControllerTest
from tests.backends.local import generate_song

class LocalCurrentPlaylistControllerTest(BaseCurrentPlaylistControllerTest,
        unittest.TestCase):

    backend_class = LocalBackend
    tracks = [Track(uri=generate_song(i), length=4464)
        for i in range(1, 4)]

    def setUp(self):
        self.original_backends = settings.BACKENDS
        settings.BACKENDS = ('mopidy.backends.local.LocalBackend',)
        super(LocalCurrentPlaylistControllerTest, self).setUp()

    def tearDown(self):
        super(LocalCurrentPlaylistControllerTest, self).tearDown()
        settings.BACKENDS = settings.original_backends
