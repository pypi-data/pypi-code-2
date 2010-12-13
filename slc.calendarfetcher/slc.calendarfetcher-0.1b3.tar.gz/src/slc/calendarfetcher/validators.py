from zope.schema import interfaces
from z3c.form import validator
from Products.validation import validation
from slc.calendarfetcher import calendarfetcher_messagefactory as _

class TextLineURLValidator(validator.SimpleFieldValidator):
    """ Validates a Text field for URLS (each one on a new line) """

    def validate(self, value):
        """  """
        if value is None:
            msg = _("Please provide a valid URL.")
            raise interfaces.InvalidURI(msg)

        urls = [v.strip() for v in value.split()]
        verify = validation.validatorFor("isURL")
        for url in urls:
            # Google's (and perhaps other) ICS URLs don't validate, so we only
            # validate the first part...
            surl = '/'.join(url.split('/')[:3])
            if verify(str(surl)) != True:
                msg = _("The specified resource, '%s' is not a valid URL." % url)
                raise interfaces.InvalidURI(msg)

