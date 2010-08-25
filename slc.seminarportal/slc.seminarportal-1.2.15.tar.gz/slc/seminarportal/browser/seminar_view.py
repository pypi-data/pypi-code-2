from zope.interface import implements

from DateTime import DateTime
from Acquisition import aq_inner

from Products.CMFPlone.PloneBatch import Batch
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView

from interfaces import ISeminarView

class SeminarView(BrowserView):
    """ Helper functionality for displaying a roster of speeches at a
        Seminar.
    """
    implements(ISeminarView)

    def get_datetime(self, date):
        """ Returns DateTime object
        """
        return DateTime(date)
        
    def get_venues(self):
        """ Return brains for SpeechVenue objects in context 
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(portal_type='SPSpeechVenue', 
                         path='/'.join(self.context.getPhysicalPath()),
                         sort_on='getObjPositionInParent',)
        return list(brains)
 
    def get_roster(self, venues=[]):
        """ Return a dict of {date:{venue_id:{time:[speeches]}}}
        """
        d = {}
        catalog = getToolByName(self.context, 'portal_catalog')
        venues = venues or self.get_venues()
        for venue in venues:
            venue_id = venue.id
            speeches = catalog(portal_type='SPSpeech', 
                               path='%s/speech-venues/%s' % ('/'.join(self.context.getPhysicalPath()), venue_id))
            for speech in speeches:
                date = speech.start.Date()
                time = speech.start
                if d.has_key(date):
                    if d[date].has_key(venue_id):
                        if d[date][venue_id].has_key(time):
                            d[date][venue_id][time].append(speech)
                        else:
                            d[date][venue_id][time] = [speech]
                    else:
                        d[date][venue_id] = {time:[speech]}
                else:
                    d[date] = {venue_id:{time:[speech]}}
        return d

    def get_event_summary(self, venues=[]):
        """ Return a dict of {date:[(time, speech)]}
        """
        d = {}
        catalog = getToolByName(self.context, 'portal_catalog')
        venues = venues or self.get_venues()
        for venue in venues:
            speeches = catalog(portal_type='SPSpeech', 
                               path='%s/speech-venues/%s' % ('/'.join(self.context.getPhysicalPath()), venue.id))
            for speech in speeches:
                date = speech.start.Date()
                time = speech.start
                if d.has_key(date):
                    d[date].append((time, speech.getPath(), speech))
                else:
                    d[date] = [(time, speech.getPath(), speech)]
        return d
        

    def get_day_times(self, roster={}):
        """ Return a dictionary of {seminar_day_date:[speech_time]}
        """
        roster = roster or self.get_roster()
        day_times = {}
        for day in roster.keys():
            times = []
            d = {} # Dict used to enforece uniqueness
            for venue_id in roster[day].keys():
                for t in roster[day][venue_id].keys():
                    d[t] = 'dummy'

            day_times[day] = sorted(d.keys())

        return day_times 


    def get_files_and_images(self):
        """ Return a list of files and images in current context
        """
        context = aq_inner(self.context)
        objs = context.objectValues(['ATFile', 'ATBlob', 'ATImage'])
        objs = [(o.pretty_title_or_id(), o) for o in objs]

        # See if the object is schema-extended with an 'attachment' field.
        # Pretty Unique and particular use-case, but necessary for us.
        attachment_field = context.Schema().get('attachment', None)
        if attachment_field:
            attachment = attachment_field.get(context)
            if attachment.size:
                objs += [(attachment.filename, attachment)]
        return objs


    def get_speechvenues(self):
        """ Return speech venues in current context
        """
        return self.context.objectValues(['SPSpeechVenue'])


    def query_items(self, type, b_size=10):
        """ """
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        speeches = catalog(
                    portal_type=type,
                    path='/'.join(context.getPhysicalPath())
                    )

        b_start = self.request.get('b_start', 0)
        batch = Batch(speeches, b_size, int(b_start), orphan=0)
        return batch

    def isAnonymous(self):
        """ """
        anonymous = getToolByName(self, 'portal_membership').isAnonymousUser()
        return anonymous
