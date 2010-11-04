from zope.app.publisher.interfaces.browser import IBrowserView

class ISeminarFolderView(IBrowserView):
    """
    """
    def get_seminars(self):
        """ Return brains for SPSeminar objects in context 
        """

class ISeminarView(IBrowserView):
    """
    """
    def get_datetime(self, date):
        """ Returns DateTime object
        """

    def get_venues(self):
        """ Return brains for SPSpeechVenue objects in context 
        """

    def get_roster(self, venues=[]):
        """ Return a dict of {date:{venue_id:{time:[speeches]}}}
        """

    def get_event_summary(self, venues=[]):
        """ Return a dict of {date:[(time, speech)]}
        """

    def get_day_times(self, roster={}):
        """ Return a dictionary of {seminar_day_date:[speech_time]}
        """

    def get_files_and_images(self):
        """ Return a list of files and images
        """

    def get_speechvenues(self):
        """ Return speech venues in current context
        """

    def get_speeches(self):
        """ Return speeches in current context
        """

