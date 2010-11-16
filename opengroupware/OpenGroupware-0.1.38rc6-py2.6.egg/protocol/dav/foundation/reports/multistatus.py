# Copyright (c) 2010 Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
from xml.sax.saxutils import escape, unescape

PROP_METHOD    = 0
PROP_NAMESPACE = 1
PROP_LOCALNAME = 2
PROP_DOMAIN    = 3

class Multistatus(object):

    @staticmethod
    def generate(resources, props, w):
        w.write('<?xml version="1.0" encoding="utf-8"?>\n')
        w.write('<D:multistatus xmlns:D="DAV:">\n')
        for href in resources.keys():
            unknown = [ ]
            known  = { }
            resource = resources.get(href)
            if (resource is not None):
                w.write(u'<D:response>')
                w.write(u'<D:href>{0}</D:href>'.format(href))
                for i in range(len(props)):
                    prop = props[i]
                    if (hasattr(resource, prop[PROP_METHOD])):
                        x = getattr(resource, prop[PROP_METHOD])
                        value = x()
                        if (value is not None):
                            known[prop] = escape(value)
                    else:
                        unknown.append(prop)
                # render found properties
                if (len(known) > 0):
                    w.write(u'<D:propstat>')
                    w.write(u'<D:status>HTTP/1.1 200 OK</D:status>')
                    for prop in known.keys():
                        w.write(u'<D:prop>')
                        if (known[prop] is None):
                            # PROPERTY VALUE NONE
                            if (prop[PROP_DOMAIN] == 'webdav'):
                                w.write(u'<D:%s/>' % prop[PROP_LOCALNAME])
                            elif (prop[PROP_NAMESPACE] is None):
                                w.write(u'<{0}/>'.format(prop[PROP_LOCALNAME]))
                            else:
                                w.write(u'<{0} xmlns="{1}"/>'.format(prop[PROP_LOCALNAME],
                                                                     prop[PROP_NAMESPACE]))
                        else:
                           # PROPERTY HAS VALUE
                            if (prop[PROP_DOMAIN] == 'webdav'):
                                w.write(u'<D:{0}>{1}</D:{2}>'.format(prop[PROP_LOCALNAME],
                                                                     str(known[prop]),
                                                                     prop[PROP_LOCALNAME]))
                            elif (prop[1] is None):
                                w.write(u'<{0}>{1}</{2}>'.format(prop[PROP_LOCALNAME],
                                                                 str(known[prop]),
                                                                 prop[PROP_LOCALNAME]))
                            else:
                                w.write(u'<{0} xmlns="{1}">{2}</{3}>'.format(prop[PROP_LOCALNAME],
                                                                             prop[PROP_NAMESPACE],
                                                                             str(known[prop]),
                                                                             prop[PROP_LOCALNAME]))
                        w.write(u'</D:prop>')
                    w.write(u'</D:propstat>')
                # UNKNOWN PROPERTIES
                if (len(unknown) > 0):
                    w.write(u'<D:propstat>')
                    w.write(u'<D:status>HTTP/1.1 404 Not found</D:status>')
                    for prop in unknown:
                        if (prop[PROP_DOMAIN] == 'webdav'):
                            w.write(u'<D:prop><D:{0}/></D:prop>'.format(prop[PROP_LOCALNAME]))
                        elif (prop[PROP_NAMESPACE] is None):
                            w.write(u'<D:prop><{0}/></D:prop>'.format(prop[PROP_LOCALNAME]))
                        else:
                            w.write(u'<D:prop><{0} xmlns="{1}"/></D:prop>'.format(prop[PROP_LOCALNAME],
                                                                                  prop[PROP_NAMESPACE]))
                    w.write(u'</D:propstat>')
                w.write(u'</D:response>\n')
        w.write('</D:multistatus>')
