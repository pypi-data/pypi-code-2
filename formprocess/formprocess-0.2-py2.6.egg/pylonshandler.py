""" Pylons specific form handlers and schemas. """
import pylons

from formprocess.handler import FormHandler


class PylonsFormHandler(FormHandler):
    """ A form handler for use with pylons. """
    
    def fetch_form_params(self, state=None):
        """ Fetch the form params from pylson.request.POST. """
        return pylons.request.POST

    def customize_fill_kwargs(self, defaults, errors, state, fill_kwargs):
        """ Set the encoding for htmlfill to use. """
        fill_kwargs.update({
            'encoding': pylons.response.determine_charset(),
        })
        return fill_kwargs
