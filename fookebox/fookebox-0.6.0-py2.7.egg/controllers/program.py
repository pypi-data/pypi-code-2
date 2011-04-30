# fookebox, http://fookebox.googlecode.com/
#
# Copyright (C) 2007-2011 Stefan Ott. All rights reserved.
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

import logging
import simplejson

from datetime import time, datetime
from pylons import request, response, config, app_globals as g
from pylons.controllers.util import abort
from fookebox.lib.base import BaseController, render
from fookebox.model import meta
from fookebox.model.jukebox import Jukebox
from fookebox.model.mpdconn import Track
from fookebox.model.schedule import Event, EVENT_TYPE_JUKEBOX

log = logging.getLogger(__name__)

class ProgramController(BaseController):

	def index(self):
		jukebox = Jukebox()
		artists = jukebox.getArtists()
		genres = jukebox.getGenres()
		jukebox.close()

		return render('/program.tpl')

	def status(self):
		jukebox = Jukebox()
		event = jukebox.getCurrentEvent()
		next = jukebox.getNextEvent()

		now = datetime.now()
		if now.second % 2 > 0:
			format = "%H %M"
		else:
			format = "%H:%M"

		event = jukebox.getCurrentEvent()
		currentEvent = {}
		currentEvent['type'] = event.type
		currentEvent['title'] = event.name

		if event.type == EVENT_TYPE_JUKEBOX:
			track = jukebox.getCurrentSong()

			if (track.artist == Track.NO_ARTIST and
						track.title == Track.NO_TITLE):
				track.artist = ''
				track.title = ''

			currentEvent['tracks'] = [{
				'artist': track.artist,
				'title': track.title,
			}]

			playlist = jukebox.getPlaylist()
			if len(playlist) > 1:
				track = Track()
				track.load(playlist[1])

				currentEvent['tracks'].append({
					'artist': track.artist,
					'title': track.title,
				})

		events = {}
		events['current'] = currentEvent

		next = jukebox.getNextEvent()
		if next != None:
			events['next'] = {
				'type': next.type,
				'title': next.name,
				'time': next.time.strftime("%H:%M")
			}

		data = {
			'events': events,
			'time': now.strftime(format),
		}

		jukebox.close()
		response.headers['content-type'] = 'application/json'
		return simplejson.dumps(data)

	def edit(self):
		if request.method == 'POST':
			name = request.params['name']
			type = int(request.params['type'])
			hour = request.params['hour']
			minute = request.params['minute']
			dateTime = datetime.strptime("%s:%s" % (hour, minute),
					"%H:%M")
			if 'id' in request.params:
				id = request.params['id']
				Event.update(id, name, type, dateTime.time())
			else:
				Event.add(name, type, dateTime.time())

		event_q = meta.Session.query(Event)

		vars = {
			'events': Event.all(),
			'current': Event.getCurrent()
		}

		params = request.params
		if 'edit' in params:
			vars['edit'] = int(params['edit'])

		return render('/program-edit.tpl', vars)


	def current(self):
		if request.method != 'POST':
			abort(400, 'Nothing to see here')

		try:
			post = simplejson.load(request.environ['wsgi.input'])
		except simplejson.JSONDecodeError:
			log.error("QUEUE: Could not parse JSON data")
			abort(400, 'Malformed JSON data')

		id = post['id']
		g.eventID = int(id)

	def delete(self):
		if request.method != 'POST':
			abort(400, 'Nothing to see here')

		try:
			post = simplejson.load(request.environ['wsgi.input'])
		except simplejson.JSONDecodeError:
			log.error("QUEUE: Could not parse JSON data")
			abort(400, 'Malformed JSON data')

		id = post['id']
		Event.delete(int(id))

	def move(self):
		if request.method != 'POST':
			abort(400, 'Nothing to see here')

		try:
			post = simplejson.load(request.environ['wsgi.input'])
		except simplejson.JSONDecodeError:
			log.error("QUEUE: Could not parse JSON data")
			abort(400, 'Malformed JSON data')

		id = post['id']
		direction = post['direction']

		if direction == 'up':
			Event.up(id)
		else:
			Event.down(id)
