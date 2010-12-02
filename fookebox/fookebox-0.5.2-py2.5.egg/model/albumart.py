# fookebox, http://fookebox.googlecode.com/
#
# Copyright (C) 2007-2010 Stefan Ott. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import os
import mpd
import base64
import logging
from datetime import datetime
from threading import BoundedSemaphore

from pylons import config, cache

log = logging.getLogger(__name__)

class AlbumArt(object):
	def __init__(self, album):
		self.album = album

	def _getRockboxPath(self, compilation=False):
		pattern = re.compile('[\/:<>\?*|]')
		album = pattern.sub('_', self.album.name)

		if compilation:
			artist = pattern.sub('_', config.get(
				'compliations_name'))
		else:
			artist = pattern.sub('_', self.album.artist)

		return "%s/%s-%s.jpg" % (config.get('album_cover_path'),
				artist, album)

	def _getRhythmboxPath(self, compilation=False):
		album = self.album.name.replace('/', '-')

		if compilation:
			artist = config.get('compliations_name').replace(
					'/', '-')
		else:
			artist = self.album.artist.replace('/', '-')

		return "%s/%s - %s.jpg" % (config.get('album_cover_path'),
				artist, album)

	def _getInDirCover(self):
		basepath = config.get('music_base_path')

		if basepath == None:
			return None

		if len(self.album.tracks) > 0:
			track = self.album.tracks[0]
		else:
			self.album.load()
			if len(self.album.tracks) < 1:
				return None

			track = self.album.tracks[0]

		fullpath = os.path.join(basepath, track.file)
		dirname = os.path.dirname(fullpath)

		def best_image(x, y):
			pattern = '(cover|album|front)'

			if re.match(pattern, x, re.I):
				return x
			else:
				return y

		dir = os.listdir(dirname)
		dir = filter(lambda x: x.endswith(
			('jpg', 'JPG', 'jpeg', 'JPEG')), dir)

		if len(dir) < 1:
			return None

		bestmatch = reduce(best_image, dir)
		return os.path.join(dirname, bestmatch)

	def get(self):

		if config.get('cache_cover_art'):
			cover_path_cache = cache.get_cache('cover_path')
			song = "%s - %s" % (self.album.artist, self.album.name)
			path = cover_path_cache.get_value(key=song,
				createfunc=self._getCover, expiretime=300)

			if path == None:
				cover_path_cache.remove_value(song)
		else:
			path = self._getCover()

		return path

	def _getCover(self):
		path = self._getRockboxPath()
		if os.path.exists(path):
			return path

		path = self._getRockboxPath(True)
		if os.path.exists(path):
			return path

		path = self._getRhythmboxPath()
		if os.path.exists(path):
			return path

		path = self._getRhythmboxPath(True)
		if os.path.exists(path):
			return path

		cover = self._getInDirCover()

		return cover

