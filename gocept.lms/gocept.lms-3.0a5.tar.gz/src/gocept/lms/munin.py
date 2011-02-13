# vim:fileencoding=utf-8
# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Munin data views."""

import gocept.lms.app
import gocept.lms.interfaces
import grok
import zc.queue.interfaces
import zope.component


grok.context(gocept.lms.app.LMS)


class ViewMuninData(grok.Permission):
    grok.name('gocept.lms.ViewMuninData')


class StatisticalView(object):
    grok.require(ViewMuninData)

    @property
    def stats(self):
        return zope.component.getUtility(gocept.lms.interfaces.IStatistics)

class QueueSize(StatisticalView, grok.View):
    grok.name('munin-queuesize')
    grok.require(ViewMuninData)

    def render(self):
        return 'queue-size:%s' % self.stats.queue_size


class ThreadPool(StatisticalView, grok.View):
    grok.name('munin-threadpool')
    grok.require(ViewMuninData)

    def render(self):
        return 'thread-pool:%s' % self.stats.thread_pool


class Statistics(grok.Model):

    zope.interface.implements(gocept.lms.interfaces.IStatistics)
    
    thread_pool = 0

    @property
    def queue_size(self):
        check_queue = zope.component.getUtility(
                zc.queue.interfaces.IQueue, name='check')
        return len(check_queue)


@grok.subscribe(gocept.lms.app.LMS, grok.IObjectAddedEvent)
def add_statistics(lms, event):
    sm = lms.getSiteManager()
    sm['statistics'] = Statistics()
    sm.registerUtility(sm['statistics'],
        provided=gocept.lms.interfaces.IStatistics)
