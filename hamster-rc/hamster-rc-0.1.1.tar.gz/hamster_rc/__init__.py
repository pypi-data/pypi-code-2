# Copyright(c) 2011 by Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
#
# This file is part of hamster-rc.
# hamster-rc is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# hamster-rc is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with hamster-rc.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import mimetypes
import optparse
import os
import time
import wsgiref.simple_server

import dbus

import mako.template

import routes

import webob
import webob.exc
import webob.dec


HAMSTER_URI = "org.gnome.Hamster"
HAMSTER_PATH = "/org/gnome/Hamster"

BASEDIR = os.path.abspath(os.path.dirname(__file__))


def media_dir():
    return os.path.join(BASEDIR, 'media')


def templates_dir():
    return os.path.join(BASEDIR, 'templates')


def get_mimetype(filename):
    mime_type, encoding = mimetypes.guess_type(filename)
    return mime_type or 'application/octet-stream'


def get_template(name):
    template_file = os.path.join(templates_dir(), name)
    return mako.template.Template(filename=template_file,
                                  output_encoding='utf-8')


def seconds_to_datetime(seconds):
    if seconds != 0:
        gmtime = time.gmtime(seconds)
        return datetime.datetime(*gmtime[:7]).strftime("%H:%M")


def delta_to_string(seconds):
    minutes = seconds / 60
    if minutes > 0:
        hours = minutes / 60
        minutes = minutes % 60
    else:
        hours = 0

    return '%02d:%02d' % (hours, minutes)


def from_dbus_fact(fact):
    return dict(
        id=int(fact[0]),
        start_time=seconds_to_datetime(int(fact[1])),
        end_time=seconds_to_datetime(int(fact[2])),
        description=unicode(fact[3]),
        name=unicode(fact[4]),
        activity_id=int(fact[5]),
        category=unicode(fact[6]),
        tags=fact[7],
        date=seconds_to_datetime(int(fact[8])),
        delta=int(fact[9]),
        duration=delta_to_string(int(fact[9])),
        )


def now():
    return time.time() - time.timezone


class HamsterRC(object):

    map = routes.Mapper()
    map.connect('index', '/', method='index')
    map.connect('media', '/media/{path_info:.*}', method='media')

    def __init__(self):
        self.__bus = dbus.SessionBus()
        self.__hamster = self.__bus.get_object(HAMSTER_URI, HAMSTER_PATH)

    @webob.dec.wsgify
    def __call__(self, req):
        results = self.map.routematch(environ=req.environ)
        if not results:
            return webob.exc.HTTPNotFound()
        match, route = results
        req.urlvars = ((), match)
        kwargs = match.copy()
        method = kwargs.pop('method')
        return getattr(self, method)(req, **kwargs)

    def index(self, req):
        activities = [unicode(a[0]) for a in self.__hamster.GetActivities()]

        if req.method == 'POST':
            action = req.POST.get('action', None)
            if action == u'start':
                activity = req.POST.get('activity-select', None)
                if activity in activities:
                    self.__hamster.AddFact(activity, "", now(), 0)
            elif action == u'stop':
                self.__hamster.StopTracking(now())

            raise webob.exc.HTTPSeeOther(location='/')

        today_facts = [from_dbus_fact(fact)
                       for fact in self.__hamster.GetTodaysFacts()]

        data = {'current_fact': None, 'facts': today_facts}

        if today_facts:
            last_fact = today_facts[-1]
            is_active = last_fact['end_time'] is None
            if is_active:
                data['current_fact'] = last_fact

        total = sum([f['delta'] for f in today_facts])
        data['total'] = delta_to_string(total)

        data['activities'] = sorted(activities)

        template = get_template('index.html')
        return template.render(**data)

    def media(self, req, path_info):
        filename = os.path.join(media_dir(), path_info)
        if not os.path.exists(filename):
            return webob.exc.HTTPNotFound()
        response = webob.Response(content_type=get_mimetype(filename))
        response.body = open(filename, 'rb').read()
        return response


def main():
    parser = optparse.OptionParser()
    parser.add_option('-s', '--host', dest='host', default='localhost',
                      help='Host where the server will bind to')
    parser.add_option('-p', '--port', dest='port', type='int', default=8888,
                      help='Port where the server will bind to')

    (options, args) = parser.parse_args()

    app = HamsterRC()
    server = wsgiref.simple_server.make_server(options.host, options.port, app)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
