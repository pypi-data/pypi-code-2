import os
import tempfile

from zope.interface import Interface
from zc.lockfile import LockFile, LockError
from Products.Five import BrowserView

from collective.pdfLeadImage.async import get_queue

LOCKFILE_NAME = os.path.join(tempfile.gettempdir(),
                             __name__ + '.process_pdfLeadImage_queue')


class IpdfLeadImageQueueView(Interface):

    def process_conversion_queue(self):
        """process the queue.
        This is what you call from cron or zope clock server to get
        periodic image preview generation.
        """


class pdfLeadImageQueueView(BrowserView):

    def process_conversion_queue(self):
        """process the queue.
        """
        try:
            lock = LockFile(LOCKFILE_NAME)
        except LockError:
            return "`process_conversion_queue` is locked by another process (%r)." % (
                LOCKFILE_NAME)

        try:
            return self._process_conversion_queue()
        finally:
            lock.close()

    def _process_conversion_queue(self):
        msg = u''
        num = 0
        queue = get_queue('collective.pdfLeadImage.conversion')
        num = queue.process()
        if num:
            msg += u'%d Jobs in queue. Processing queue...\n' % num
            for job in queue.finished[-1:]:
                msg += str(job) + u'\n'
                msg += u'Finished Job'
        if num == 0:
            msg += u'No Jobs in Queue. No Action Required, None Taken.'
        return msg
