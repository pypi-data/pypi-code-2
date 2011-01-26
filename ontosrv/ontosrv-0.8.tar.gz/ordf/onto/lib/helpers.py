"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
# Import helpers as desired, or define your own, ie:
from webhelpers.html.tags import checkbox, password, literal
from ordf.namespace import RDFS
from ordf.term import URIRef, BNode, Node
import cgi

def render_html(u):
    """
    Take an RDFLib node and render an HTML representation.
    This uses labels for links if *u* is an instance of 
    :class:`URIRef`.
    """
    if not isinstance(u, URIRef):
        return cgi.escape(u"%s" % u)

    from ordf.onto.lib.base import BaseController
    if hasattr(BaseController.handler, "fourstore"):
        store = BaseController.handler.fourstore
    elif hasattr(BaseController.handler, "rdflib"):
        store = BaseController.handler.rdflib
    else:
        return '<a href="%s">%s</a>' % (cgi.escape(u), cgi.escape(u))

    from ordf.onto.lib.base import request
    q = "SELECT DISTINCT ?label WHERE { %s %s ?label }" % (u.n3(), RDFS["label"].n3())
    labels = [x if isinstance(x, Node) else x[0] for x in store.query(q)]
    label_langs = dict([(x.language, x) for x in labels])
    if None in label_langs:
        no_lang = label_langs[None]
        del label_langs[None]
    elif "en" in label_langs:
        no_lang = label_langs["en"]
    elif labels:
        no_lang = labels[0]
    else:
        no_lang = u

    ## fix for fourstore which upper-cases labels
    label_langs = dict([(x.lower(), label_langs[x]) for x in label_langs])

    lang = request.accept_language.best_match(label_langs.keys())
    if lang:
        label = label_langs[lang]
    else:
        label = no_lang

    return '<a href="%s">%s</a>' % (cgi.escape(u), cgi.escape(label))
