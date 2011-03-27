from .base import *

register_ns("BIBLIOENTRY", Namespace("http://bibliographica.org/entry/"))
from ordf.namespace import BIBLIOENTRY, RDFS, RDF

class Label(DomainObject):
    '''A simple class to get the label or value from a blank node
    '''
    namespace = BIBLIOENTRY
    
    _label = predicate(RDFS.label)
    _value = predicate(RDF.value)

    def __init__(self, *av, **kw):
        super(Label, self).__init__(*av, **kw)
        self.value = None
        if self._label:
            self.value = self._label[0]
        elif self._value:
            self.value = self._value[0]
