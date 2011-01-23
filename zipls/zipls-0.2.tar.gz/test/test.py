import unittest
from StringIO import StringIO

from zipls import zipls, Song, Songs


################################################################
# Mocking objects
class MockOpen(object):
    def __init__(self, mockfile):
        self.f = StringIO(mockfile)

    def __call__(self, *args, **kwargs):
        return self

    def __enter__(self, *args, **kwargs):
        return self.f

    def __exit__(self, *args, **kwargs):
        self.f.close()

class MockSong(Song):
    def __init__(self, **kwargs):
        "This init mostly just disables error checking"
        args={"path":None,
              "title":None,
              "artist":None,
              "ext":None,
              "track_number":None,
              "album":None,}
        args.update(kwargs)
        for arg in args:
            setattr(self,
                    arg,
                    args[arg])

################################################################
# Tests
class TestSong(unittest.TestCase):
    def test_nonexistent_song_raises(self):
        self.assertRaises(OSError,
                          Song,
                          "nonexistent_path")

    def test_set_simple_title(self):
        song = MockSong(path="Song.mp3")
        song._set_title()
        self.assertEqual(song.title,
                         "Song")

    def test_set_title(self):
        song = MockSong(path="hello/my/name/is/Example Song.mp3")
        song._set_title()
        self.assertEqual(song.title,
                         "Example Song")

    def test_set_broken_title(self):
        song = MockSong(path="Song")
        song._set_title()
        self.assertEqual(song.title,
                         "Song")

    def test_nonexistent_ext_raises(self):
        song = MockSong(path="Song")
        self.assertRaises(OSError,
                          song._set_ext_from_path,
                          song.path)

    def test___init__(self):
        song = Song(path="test/test-data/Sample.mp3",
                    title="Sample title",
                    artist="Sample artist",
                    ext="mp3")
        self.assertEqual(song.path,
                         "test/test-data/Sample.mp3")
        self.assertEqual(song.title,
                         "Sample title")
        self.assertEqual(song.artist,
                         "Sample artist")
        self.assertEqual(song.ext,
                         "mp3")

    def test_format_track_numbers(self):
        song = Song(path="test/test-data/Sample.mp3",
                    title="Title",
                    artist="Artist",
                    track_number='1',
                    album="Album")
        self.assertEqual(format(song,
                                "{track_number:02}"),
                         "01")

class TestM3U(unittest.TestCase):
    def setUp(self):
        self.playlist = """#EXTM3U

#EXTINF:123,Sample Artist - Sample title
music/Sample.mp3

#EXTINF:321,Example Artist - Example title
music/Greatest Hits/Example.ogg
"""
        self.songs = ({"path":"music/Sample.mp3",
                       "artist":"Sample Artist",
                       "title":"Sample title"},
                      {"path":"music/Greatest Hits/Example.ogg",
                       "artist":"Example Artist",
                       "title":"Example title"},
                      )
        self.original_open = __builtins__.open
        zipls.open = MockOpen(self.playlist)

        self.original_artist_from_tag = Song.set_artist_from_tag
        Song.set_artist_from_tag = lambda s: True

    def tearDown(self):
        zipls.open = self.original_open
        Song.set_artist_from_tag = self.original_artist_from_tag

    def test_m3u_parsing(self):
        songs = Songs("an.m3u", song_class=MockSong)
        for kwargs, song in zip(self.songs, songs):
            self.assertEqual(song,
                             MockSong(**kwargs))

if __name__ == "__main__":
    unittest.main()
