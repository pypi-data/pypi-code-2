from lxml import etree
from lxml.etree import Element, QName

from .jsonutil import JsonTable
from . import httputil


def computations_document(self._eobject, kw, overwrite):
    pass


class Computations(object):

    def __init__(self, eobject):
        self._intf = eobject._intf
        self._eboject = eobject

    def attach(self, kw, overwrite=False):
        doc = computations_document(self._eobject, kw, overwrite)

        body, content_type = httputil.file_message(
            doc, 'text/xml', 'comp.xml', 'comp.xml')

        comp_uri = self._eobject._uri

        if overwrite:
            comp_uri += '?allowDataDeletion=true'

        self._intf._exec(comp_uri, 
                         method='PUT', 
                         body=body,
                         headers={'content-type':content_type}
                         )

    def get(self, keys=None):
        pass


