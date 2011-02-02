from formencode.validators import *
from formencode.api import Invalid
from formencode import compound, validators
from formencode.foreach import ForEach
from formencode.schema import Schema

from rum import app

All = compound.All
class MaxLength(MaxLength):
    if_empty=''

_ = lambda s: s

class RelatedFetcher(FancyValidator):
    messages = {
        'empty' : _("Please select a value")
    }
    not_empty = False
    def __init__(self, resource, app=None, **kw):
        self.resource = resource
        self.app=app
        for k,v in kw.iteritems():
            setattr(self, k, v)

    @property
    def repository(self):
        if self.app:
            return self.app.repositoryfactory(self.resource)
        else:
            return app.repositoryfactory(self.resource)

    def _from_python(self, value, state=None):
        if not isinstance(value, (basestring,list)):
            # deal with the related object
            return self.repository.get_id(value)
        else:
            # deal with a the related object's id when
            # the form is redisplayed due to validation errors
            return value

    def _to_python(self, value, state=None):
        if value and isinstance(value, basestring):
            return self.repository.get(value)
        elif value:
            return value
        if self.not_empty:
            raise Invalid(self.message('empty', state), value, state)
        return None

class FilteringSchema(Schema):
    allow_extra_fields = True
    filter_extra_fields = True

class UnicodeString(UnicodeString):
    """
    Keeps unicode strings as unicode since Genshi (and most template languages)
    handle unicode internally and will break if passed encoded strings for
    variable substitution.
    """
    def _from_python(self, value, state):
        if isinstance(value, basestring):
            return value
        elif hasattr(value, '__unicode__'):
            return unicode(value)
        else:
            return str(value)
