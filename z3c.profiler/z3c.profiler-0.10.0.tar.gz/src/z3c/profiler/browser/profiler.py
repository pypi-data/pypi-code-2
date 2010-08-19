##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: __init__.py 72087 2007-01-18 01:03:33Z rogerineichen $
"""
__docformat__ = "reStructuredText"

import sys
from cStringIO import StringIO

from zope.traversing.browser import absoluteURL

from z3c.pagelet import browser
from z3c.profiler.wsgi import getStats
from z3c.profiler.wsgi import listStats
from z3c.profiler.wsgi import installProfiler
from z3c.profiler.wsgi import uninstallProfiler


class ProfilerPagelet(browser.BrowserPagelet):
    """Profiler page.

    It whould be so easy with z3c.form, but I decided to depend on
    less packages as possible and not using z3c.form and other packages.
    Forgive me the z3c.pagelet usage but it's so nice to do layout things
    without METAL macros ;-)

    Note: I didn't internationalize the profiler, should we?

    The stats output is horrible for formatting in html, but let's try to
    support a nice table instead of the ugly print out whihc needs a
    monitor with at least 3000px width.
    """

    doProfile = False
    _statsData = {}
    _callersData = {}
    _callesData = {}
    _printOutput = None

    @property
    def action(self):
        try:
            return '%s/doProfile' % absoluteURL(self.context, self.request)
        except TypeError, e:
            return './doProfile'

    @property
    def profilerButton(self):
        if self.doProfile:
            return {'name':'profiler.uninstall', 'value': 'Stop'}
        else:
            return {'name':'profiler.install', 'value': 'Start'}

    @property
    def showProfileButton(self):
        if self.doProfile:
            return True
        else:
            return False

    @property
    def statsData(self):
        return self._statsData

    @property
    def callesData(self):
        return self._callersData

    @property
    def callersData(self):
        return self._callesData

    @property
    def printOutput(self):
        return self._printOutput

    def listStats(self):
        return listStats()

    def process(self):
        aborted = False
        stats = getStats()

        if not stats:
            return ''

        uri = self.request.get('stats', None)

        info = stats.get(uri)
        if not info:
            info = stats.items()[0][1]

        stats = info[0]

        output = StringIO()

        stripdirs = self.request.get('stripdirs', False)
        if stripdirs:
            stats.strip_dirs()

        sorton = self.request.get('sorton', 'time')
        stats.sort_stats(sorton)

        mode = self.request.get('mode', 'stats')
        limit = int(self.request.get('limit', 500))

        stats_stream = stats.stream
        stats.stream = output

        try:
            getattr(stats, 'print_%s'%mode)(limit)
        finally:
            stats.stream = stats_stream

        output.seek(0)
        data = output

        info = {}
        rows = []
        info['rows'] = rows
        info['summary'] = []
        info['errors'] = []
        append = rows.append
        lines = data.readlines()

        if mode == 'stats':
            for i, line in enumerate(lines):
                print line,
                try:
                    ncalls, tottime, totpercall, cumtime, percall, fn = line.split()
                    d = {}
                    d['ncalls'] = ncalls
                    d['tottime'] = tottime
                    d['totpercall'] = totpercall
                    d['cumtime'] = cumtime
                    d['percall'] = percall
                    d['fn'] = fn
                    if ncalls == 'ncalls':
                        d['thead'] = True
                    else:
                        d['thead'] = False
                    append(d)
                except ValueError, e:
                    if i < 4:
                        info['summary'].append(line)
                    else:
                    # skip lines at the end and parser errors
                        info['errors'].append(line)
                except Exception, e:
                    aborted = True

            self._statsData = info

        else:
            for i, line in enumerate(lines):
                try:
                    d = {}
                    print line,
                    if ('...' in line or
                        'Ordered by:' in line):
                        # skip header line
                        continue
                    varius = line.split()
                    if len(varius) == 0:
                        continue
                    if len(varius) == 1:
                        d['fn'] = ''
                        d['caller'] = varius[0]
                        d['time'] = ''
                    elif len(varius) == 2:
                        if varius[1] in ['->', '<-']:
                            d['fn'] = varius[0]
                            d['caller'] = ''
                            d['time'] = ''
                        else:
                            d['fn'] = ''
                            d['caller'] = varius[0]
                            d['time'] = varius[1]
                    elif len(varius) == 3:
                        d['fn'] = varius[0]
                        d['caller'] = varius[1]
                        d['time'] = varius[2]
                    elif len(varius) == 4:
                        d['fn'] = varius[0]
                        d['caller'] = varius[2]
                        d['time'] = varius[3]
                    elif len(varius) > 4:
                        continue
                    append(d)
                except ValueError, e:
                    if i < 4:
                        if not 'Function' in line:
                            # append to summary, but skip header
                            info['summary'].append(line)
                    else:
                    # skip lines at the end and parser errors
                        info['errors'].append(line)
                except Exception, e:
                    print ""
                    print e
                    aborted = True

            if mode == 'callers':
                self._callersData = info

            if mode == 'callees':
                self._callesData = info

        if aborted:
            self._statsData = {}
            self._callersData = {}
            self._callesData = {}
            output.seek(0)
            self._printOutput = output.getvalue()

    def update(self):
        self.process()
        calls = int(self.request.get('calls', 2))
        if 'profiler.install' in self.request:
            installProfiler(calls)
            self.doProfile = True
        elif 'profiler.uninstall' in self.request:
            uninstallProfiler(calls)
            self.doProfile = False
