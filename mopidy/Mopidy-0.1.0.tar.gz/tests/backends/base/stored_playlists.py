import os
import shutil
import tempfile

from mopidy import settings
from mopidy.mixers.dummy import DummyMixer
from mopidy.models import Playlist

from tests import SkipTest, data_folder

class BaseStoredPlaylistsControllerTest(object):
    def setUp(self):
        self.original_playlist_folder = settings.LOCAL_PLAYLIST_FOLDER
        self.original_tag_cache = settings.LOCAL_TAG_CACHE
        self.original_music_folder = settings.LOCAL_MUSIC_FOLDER

        settings.LOCAL_PLAYLIST_FOLDER = tempfile.mkdtemp()
        settings.LOCAL_TAG_CACHE = data_folder('library_tag_cache')
        settings.LOCAL_MUSIC_FOLDER = data_folder('')

        self.backend = self.backend_class(mixer_class=DummyMixer)
        self.stored  = self.backend.stored_playlists

    def tearDown(self):
        self.backend.destroy()

        if os.path.exists(settings.LOCAL_PLAYLIST_FOLDER):
            shutil.rmtree(settings.LOCAL_PLAYLIST_FOLDER)

        settings.LOCAL_PLAYLIST_FOLDER = self.original_playlist_folder
        settings.LOCAL_TAG_CACHE = self.original_tag_cache
        settings.LOCAL_MUSIC_FOLDER = self.original_music_folder

    def test_create(self):
        playlist = self.stored.create('test')
        self.assertEqual(playlist.name, 'test')

    def test_create_in_playlists(self):
        playlist = self.stored.create('test')
        self.assert_(self.stored.playlists)
        self.assert_(playlist in self.stored.playlists)

    def test_playlists_empty_to_start_with(self):
        self.assert_(not self.stored.playlists)

    def test_delete_non_existant_playlist(self):
        self.stored.delete(Playlist())

    def test_delete_playlist(self):
        playlist = self.stored.create('test')
        self.stored.delete(playlist)
        self.assert_(not self.stored.playlists)

    def test_get_without_criteria(self):
        test = self.stored.get
        self.assertRaises(LookupError, test)

    def test_get_with_wrong_cirteria(self):
        test = lambda: self.stored.get(name='foo')
        self.assertRaises(LookupError, test)

    def test_get_with_right_criteria(self):
        playlist1 = self.stored.create('test')
        playlist2 = self.stored.get(name='test')
        self.assertEqual(playlist1, playlist2)

    def test_get_by_name_returns_unique_match(self):
        playlist = Playlist(name='b')
        self.stored.playlists = [Playlist(name='a'), playlist]
        self.assertEqual(playlist, self.stored.get(name='b'))

    def test_get_by_name_returns_first_of_multiple_matches(self):
        playlist = Playlist(name='b')
        self.stored.playlists = [
            playlist, Playlist(name='a'), Playlist(name='b')]
        try:
            self.stored.get(name='b')
            self.fail(u'Should raise LookupError if multiple matches')
        except LookupError as e:
            self.assertEqual(u'"name=b" match multiple playlists', e[0])

    def test_get_by_name_raises_keyerror_if_no_match(self):
        self.stored.playlists = [Playlist(name='a'), Playlist(name='b')]
        try:
            self.stored.get(name='c')
            self.fail(u'Should raise LookupError if no match')
        except LookupError as e:
            self.assertEqual(u'"name=c" match no playlists', e[0])

    def test_lookup(self):
        raise SkipTest

    def test_refresh(self):
        raise SkipTest

    def test_rename(self):
        playlist = self.stored.create('test')
        self.stored.rename(playlist, 'test2')
        self.stored.get(name='test2')

    def test_rename_unknown_playlist(self):
        self.stored.rename(Playlist(), 'test2')
        test = lambda: self.stored.get(name='test2')
        self.assertRaises(LookupError, test)

    def test_save(self):
        # FIXME should we handle playlists without names?
        playlist = Playlist(name='test')
        self.stored.save(playlist)
        self.assert_(playlist in self.stored.playlists)

    def test_playlist_with_unknown_track(self):
        raise SkipTest
