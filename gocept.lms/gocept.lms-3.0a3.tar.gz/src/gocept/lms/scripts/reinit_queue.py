# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import transaction
import zope.app.component.hooks
import zc.queue
import zc.queue.interfaces


lms = root['lms']
zope.app.component.hooks.setSite(lms)

print "Re-initializing checking queue"

site_manager = lms.getSiteManager()
del site_manager['CompositeQueue']
site_manager['CompositeQueue'] = queue = zc.queue.CompositeQueue()
site_manager.registerUtility(queue, zc.queue.interfaces.IQueue, name='check')

transaction.commit()
