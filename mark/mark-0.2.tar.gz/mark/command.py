"""
.. program:: mark

Bookmarking utility

Usage: ``mark [options] uri``

.. cmdoption:: -c config.ini

    default ~/.mark.ini
"""

import argparse

import warnings
warnings.simplefilter("ignore", DeprecationWarning)
import logging
import urllib2
import os, sys
from datetime import datetime
from string import ascii_letters, digits
from rdflib.graph import Graph
from rdflib.namespace import Namespace
from rdflib.plugin import get as get_plugin
from rdflib.store import Store
from rdflib.term import URIRef, Literal, BNode

def slugify(s):
    slug = ""
    for c in s:
        if c in ascii_letters + digits: slug += c
        else: slug += "-"
    return slug.lower()

config = {
    "store": "IOMemory",
    "store_args": "",
    "graph": "http://example.org/bookmarks",
    "tag_ns": "tag:example.org,2011:",
    "tagger": "http://example.org/nobody#i",
}

def mark():
    parser = argparse.ArgumentParser(description="""
Bookmarking utility
""")
    parser.add_argument("-c", "--config", default=os.path.join(os.environ.get("HOME", "/"), ".mark.ini"),
                        dest="config", help="Config")
    parser.add_argument("-t", "--title", 
                        dest="title", help="Title")
    parser.add_argument("-m", "--comment", action="append", help="Comment", default=[])
    parser.add_argument("-d", "--debug", action="store_true",
                        dest="debug", help="Debug")
    parser.add_argument("uri", help="URI")
    parser.add_argument("tags", nargs="*", help="Tags")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    log = logging.getLogger(__name__)

    try:
        fp = open(args.config)
        config.update(eval(fp.read()))
        fp.close()
    except IOError:
        pass

    S = get_plugin(config["store"], Store)
    store = S(config["store_args"])

    RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    TAGGING = Namespace("http://tagora.ecs.soton.ac.uk/schemas/tagging#")
    TAG = Namespace(config["tag_ns"])

    graph = Graph(store, identifier=URIRef(config["graph"]))

    resource = URIRef(args.uri)

    post = BNode()
    graph.add((post, RDF["type"], TAGGING["Post"]))
    graph.add((post, TAGGING["taggedOn"], Literal(datetime.utcnow())))
    graph.add((post, TAGGING["taggedResource"], resource))

    if args.title:
        graph.add((resource, RDFS["label"], Literal(args.title)))

    for comment in args.comment:
        graph.add((post, RDFS["comment"], Literal(comment)))

    tagger = URIRef(config["tagger"])
    graph.add((tagger, RDF["type"], TAGGING["Tagger"]))
    graph.add((tagger, TAGGING["hasPost"], post))

    ntags = len(args.tags)
    if ntags > 0:
        tagseg = BNode()
        graph.add((post, TAGGING["hasTagSequence"], tagseg))
        for i in range(ntags):
            if i < (ntags-1):
                graph.add((tagseg, RDF["type"], TAGGING["TagSegment"]))
            else:
                graph.add((tagseg, RDF["type"], TAGGING["FinalTagSegment"]))
            tag = TAG[slugify(args.tags[i])]
            graph.add((tagger, TAGGING["usesTag"], tag))
            graph.add((tagseg, TAGGING["tagUsed"], tag))
            graph.add((tag, RDF["type"], TAGGING["UserTag"]))
            graph.add((tag, RDFS["label"], Literal(args.tags[i])))
            if i < (ntags-1):
                next = BNode()
                graph.add((tagseg, TAGGING["hasNextSegment"], next))
                tagseg = next

    graph.commit()

def marq():
    parser = argparse.ArgumentParser(description="""
Bookmarking utility
""")
    parser.add_argument("-c", "--config", default=os.path.join(os.environ.get("HOME", "/"), ".mark.ini"),
                        help="Config file (default ~/.mark.ini)")
    parser.add_argument("words", nargs="+", help="Words to query")
    args = parser.parse_args()
 
    try:
        fp = open(args.config)
        config.update(eval(fp.read()))
        fp.close()
    except IOError:
        pass

    S = get_plugin(config["store"], Store)
    store = S(config["store_args"])

    fts = u" } UNION { ".join(u'?resource rdfs:label ?title . ?title bif:contains "%s"' % word for word in args.words)

    q = u"""
    SELECT DISTINCT ?date, ?resource, ?title
    WHERE {
       ?post a tagging:Post .
       ?post tagging:taggedResource ?resource .
       ?post tagging:taggedOn ?date .
       { %(fts)s }
    } ORDER BY DESC(?date)
""" % { "fts": fts }

    for date, resource, title in store.sparql_query(q):
        print date.toPython().strftime("%Y/%m/%d %H:%M"), resource, "\t", title
