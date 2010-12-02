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

import sys
import mpd
import base64
import logging
import simplejson

from pylons import request, response, session, tmpl_context as c, url
from pylons import config, cache
from pylons.controllers.util import abort, redirect
from pylons.i18n.translation import _, ungettext

from fookebox.lib.base import BaseController, render
from fookebox.model.jukebox import Jukebox
from fookebox.model.mpdconn import Track, Album
from fookebox.model.albumart import AlbumArt

log = logging.getLogger(__name__)

from pylons.i18n.translation import _

class JukeboxController(BaseController):

	def index(self):
		jukebox = Jukebox()
		artists = jukebox.getArtists()
		genres = jukebox.getGenres()
		jukebox.close()

		return render('/client.tpl', extra_vars={
			'genres': genres,
			'artists': artists,
			'config': config,
		})

	def status(self):
#		log.debug("STATUS: Client updating")
		jukebox = Jukebox()
		jukebox.cleanQueue()

		try:
			queueLength = jukebox.getQueueLength()
			enabled = jukebox.isEnabled()
			timeLeft = jukebox.timeLeft()
		except:
			jukebox.close()
			raise

		if (config.get('auto_queue') and queueLength == 0 and enabled
			and timeLeft <= config.get('auto_queue_time_left')):
			try:
				jukebox.autoQueue()
			except:
				jukebox.close()
				raise

		try:
			track = jukebox.getCurrentSong()
		except:
			raise
		finally:
			jukebox.close()

		data = {
			'queueLength': queueLength,
			'jukebox': enabled
		}

		if track:
#			log.debug("STATUS: Playing %s" % track)
			songPos = int(track.timePassed)
			songTime = track.time

			total = "%02d:%02d" % (songTime / 60, songTime % 60)
			position = "%02d:%02d" % (songPos / 60, songPos % 60)

			album = Album(track.artist, track.album)
			album.add(track)

			data['artist'] = track.artist
			data['track'] = track.title
			data['album'] = track.album
			data['has_cover'] = album.hasCover()
			data['cover_uri'] = album.getCoverURI()
			data['timePassed'] = position
			data['timeTotal'] = total

#		log.debug("STATUS: Queue length: %d" % queueLength)

		response.headers['content-type'] = 'application/json'
		return simplejson.dumps(data)

	def _showQueue(self):
		jukebox = Jukebox()
		output = []
		items = jukebox.getPlaylist()
		jukebox.close()

		for item in items[1:]:
			track = Track()
			track.load(item)
			output.append(render('/playlist-entry.tpl',
				extra_vars={
				'entry': track,
				'config': config,
			}))

		log.debug("QUEUE: Contains %d item(s)" % len(items[1:]))

		response.headers['content-type'] = 'application/json'
		return simplejson.dumps(output)

	def _addToQueue(self):
		try:
			post = simplejson.load(request.environ['wsgi.input'])
		except simplejson.JSONDecodeError:
			log.error("QUEUE: Could not parse JSON data")
			abort(400, 'Malformed JSON data')

		if 'file' not in post:
			log.error('QUEUE: No file specified in JSON data')
			abort(400, 'Malformed JSON data')

		b64 = post['file']

		try:
			file = base64.urlsafe_b64decode(b64)
		except TypeError:
			log.error("QUEUE: Failed to decode base64 data: %s" %
					b64)
			abort(400, 'Malformed base64 encoding')

		if file == '' or file == None:
			log.error("QUEUE: No file specified")
			abort(400, 'No file specified')

		jukebox = Jukebox()

		if jukebox.getQueueLength() >= config.get('max_queue_length'):
			log.error('QUEUE: Full, aborting')
			jukebox.close()
			abort(409, _('The queue is full'))

		jukebox.queue(file)
		jukebox.close()

	def queue(self):
		if request.method == 'GET':
			log.debug("QUEUE: GET")
			return self._showQueue()
		elif request.method == 'POST':
			log.debug("QUEUE: POST")
			return self._addToQueue()

	def _search(self, where, what, forceSearch = False):
		log.debug("SEARCH: '%s' in '%s'" % (what, where))

		jukebox = Jukebox()
		albums = jukebox.search(where, what, forceSearch)
		jukebox.close()

		log.debug("SEARCH: found %d album(s)" % len(albums))

		log.debug("SEARCH2")

		return render('/search.tpl', extra_vars={
			'what': what,
			'albums': albums.values()
		})

	def genre(self, genreBase64=''):
		log.debug('GENRE')
		try:
			genre = genreBase64.decode('base64')
		except:
			log.error("GENRE: Failed to decode base64 data: %s" %
				genreBase64)
			abort(400, 'Malformed request data')

		return self._search('genre', genre)

	def artist(self, artistBase64):
		try:
			artist = artistBase64.decode('base64')
		except:
			log.error("ARTIST: Failed to decode base64 data: %s" %
				artistBase64)
			abort(400, 'Malformed request data')

		return self._search('artist', artist)

	def search(self):
		try:
			post = simplejson.load(request.environ['wsgi.input'])
		except simplejson.JSONDecodeError:
			log.error("SEARCH: Failed to parse JSON data")
			abort(400, 'Malformed JSON data')

		try:
			what = post['what']
			where = post['where']
		except KeyError:
			log.error("SEARCH: Incomplete JSON data")
			log.error(sys.exc_info())
			abort(400, 'Malformed JSON data')

		forceSearch = 'forceSearch' in post and post['forceSearch']

		return self._search(where, what, forceSearch)

	def remove(self):
		if not config.get('enable_song_removal'):
			log.error("REMOVE: Disabled")
			abort(400, _('Song removal disabled'))

		try:
			post = simplejson.load(request.environ['wsgi.input'])
		except simplejson.JSONDecodeError:
			log.error('REMOVE: Failed to parse JSON data')
			abort(400, 'Malformed JSON data')

		if 'id' not in post:
			log.error('REMOVE: No id specified in JSON data')
			abort(400, 'Malformed JSON data')

		id = post['id']

		jukebox = Jukebox()
		jukebox.remove(id)
		jukebox.close()

	def control(self):
		if not config.get('enable_controls'):
			log.error('CONTROL: Disabled')
			abort(400, _('Controls disabled'))

		try:
			post = simplejson.load(request.environ['wsgi.input'])
		except simplejson.JSONDecodeError:
			log.error('CONTROL: Failed to parse JSON data')
			abort(400, 'Malformed JSON data')

		if 'action' not in post:
			log.error('CONTROL: No action specified in JSON data')
			abort(400, 'Malformed JSON data')

		action = post['action']
		log.debug('CONTROL: Action=%s' % action)

		jukebox = Jukebox()
		commands = {
			'play': jukebox.play,
			'pause': jukebox.pause,
			'prev': jukebox.previous,
			'next': jukebox.next,
			'voldown': jukebox.volumeDown,
			'volup': jukebox.volumeUp,
			'rebuild': jukebox.refreshDB,
		}

		if action not in commands:
			log.error('CONTROL: Invalid command')
			jukebox.close()
			abort(400, 'Invalid command')

		try:
			commands[action]()
		except:
			jukebox.close()
			log.error('Command %s failed' % action)
			abort(500, _('Command failed'))

		jukebox.close()

	def cover(self, artist, album):
		try:
			artist = base64.urlsafe_b64decode(str(artist))
			album = base64.urlsafe_b64decode(str(album))
		except:
			log.error("COVER: Failed to decode base64 data")
			abort(400, 'Malformed base64 encoding')

		album = Album(artist, album)
		art = AlbumArt(album)
		path = art.get()

		if path == None:
			log.error("COVER: missing for %s/%s" % (artist, album))
			abort(404, 'No cover found for this album')

		file = open(path, 'r')
		data = file.read()
		file.close()

		response.headers['content-type'] = 'image/jpeg'
		return data

	def disabled(self):
		return render('/disabled.tpl', extra_vars={
			'config': config,
			'base_url': request.url.replace('disabled', ''),
		})
