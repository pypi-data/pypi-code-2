#from rdflib.store import Store
#from rdflib import plugin
#plugin.register("Virtuoso", Store, "virtuoso.vstore", "Virtuoso")

from ordf.command import Command as _Command
from ordf.graph import Graph, ConjunctiveGraph
from ordf.namespace import *
from ordf.term import URIRef, BNode
from ordf.vocab.opmv import Agent, Process

Process.add_distribution("ckanrdf")
Process.add_distribution("ckanclient")

import ckanclient
import logging
import tempfile
import os, sys
from pprint import pformat
from datetime import datetime
from ckanrdf import version
from getpass import getuser
from traceback import format_exc

log = logging.getLogger("ckanrdf")

from ckanrdf.package import Package

import urllib

class Command(_Command):
    def ckan_base(self):
        return self.config.get("ckan_base", "http://ckan.net/")
    def api_base(self):
        return self.config.get("ckan_api_base",
                               self.ckan_base() + "api")
    @property
    def client(self):
        return ckanclient.CkanClient(
            base_location = self.api_base(),
            api_key = self.config.get("ckan_apikey", None),
            http_user = self.config.get("ckan_http_user", None),
            http_pass = self.config.get("ckan_http_pass", None)
            )

class GenerateRDF(Command):
    parser = Command.StandardParser(usage="%prog [options]")
    parser.add_option("-f", "--format",
                      dest="format",
                      default=None,
                      help="RDF serialisation for output. One of "
                           "xml, pretty-xml, n3, nt")
    parser.add_option("-o", "--output",
                      dest="output",
                      default=None,
                      help="Destination file for output. For stdout use -")
    parser.add_option("--list",
                      dest="list",
                      action="store_true",
                      default=False,
                      help="Just datasets rather than complete metadata")
    parser.add_option("--describe",
                      dest="describe",
                      action="store_true",
                      default=False,
                      help="Describe packages")
    parser.add_option("--outdir",
                      dest="outdir",
                      help="Render various representations into this directory")

    def __init__(self, *av, **kw):
        super(GenerateRDF, self).__init__(*av, **kw)
        self.config.setdefault("ckanrdf_user", getuser())


    def command(self):
        log.info("ckanrdf (version %s) starting" % (version,))

        self.packager = Package(self.config)
        register_ns("pkg", self.packager.pkg_base())
        register_ns("pkgdesc", self.packager.rdf_pkg_base())

        self.store = self.handler.rdflib.store

        agent = Agent()
        agent.nick(self.config.get("ckanrdf_user"))

        # do stuff...
        if self.options.list:
            catalogue = self.packager.build_catalogue(self.packages(), self.store)
            proc = Process(identifier=URIRef(catalogue.identifier + "#" + BNode()))
            proc.agent(agent)
            proc.use(self.api_base())
            proc.result(catalogue)
            for ext in (".rdf", ".n3", ".nt"):
                doc = URIRef(catalogue.identifier + ext)
                catalogue.add((doc, RDF["type"], OPMV["Artifact"]))
                catalogue.add((doc, OPMV["wasGeneratedBy"], proc.identifier))
                catalogue.add((doc, FOAF["primaryTopic"], URIRef(self.packager.rdf_cat())))
                catalogue.add((URIRef(self.packager.rdf_cat()), FOAF["isPrimaryTopicOf"], doc))
            self.store.commit()
            if self.options.outdir:
                self.render(catalogue)

        if self.options.describe:
            for pkg in self.packages(full=True):
                try:
                    catrec = self.packager.describe(pkg, self.store)
#                print catrec.serialize(format="n3")
                    self.store.commit()
                    if self.options.outdir:
                        self.render(catrec)
                except:
                    if isinstance(pkg, basestring): info = pkg
                    else: info = pkg.get("name") or pkg
                    log.error("Exception describing: %s\n%s" % (info, format_exc()))
                    self.store.rollback()

    def packages(self, full=False):
        if self.args:
            _pkglist = self.args
        else:
            log.info("Retrieving all packages")
            _pkglist = self.client.package_register_get()
        for name in _pkglist:
            if full:
                yield self.client.package_entity_get(name)
            else:
                yield { "name": name }

    def render(self, g):
        if str(g.identifier) == self.packager.rdf_cat_doc():
            basename = os.path.join(self.options.outdir,
                                    os.path.basename(self.packager.rdf_cat_doc()))
        else:
            nstrip = len(self.packager.rdf_pkg_base())
            parts = [x for x in self.packager.rdf_pkg_base().split("/") if x]
            ident = g.identifier[nstrip:].lstrip("/")
            basename = os.path.join(self.options.outdir, parts[-1], ident[0], ident[1], ident)
        try:
            os.makedirs(os.path.dirname(basename))
        except OSError:
            pass
        log.info("Writing %s" % basename)
        x = Graph()
        x += g
        x.serialize(basename + ".rdf", format="xml")
        x.serialize(basename + ".n3", format="n3")
        x.serialize(basename + ".nt", format="nt")

class LoadRDF(Command):
    parser = Command.StandardParser(usage="%prog [options]")
    parser.add_option("-i", "--identifier",
                      dest="ident",
                      default="http://semantic.ckan.net/")

    def command(self):
        log.info("RDF LOAD INTO %s" % self.options.ident)
        cursor = self.handler.rdflib.store.cursor()
        cursor.execute("SPARQL CLEAR GRAPH <%s>" % self.options.ident)
        for d, s, files in os.walk(self.args[-1]):
            for f in files:
                if not f.endswith(".n3"):
                    continue
                fpath = os.path.join(d, f)
                log.info("LOADING %s" % fpath)
                data = open(fpath).read()
#                q = "DB.DBA.RDF_LOAD_RDFXML('%s', '', '%s')" % (
                q = "DB.DBA.TTLP('%s', '', '%s', 32)" % (
                    data.replace("\\", "\\\\").replace("'", "\\'"), self.options.ident
                    )
                cursor.execute(q.decode("iso-8859-1").encode("utf-8"))
        log.info("FINISHED %s" % self.options.ident)
        cursor.execute("COMMIT WORK")
        cursor.close()
        
def genrdf():
    GenerateRDF().command()

def loadrdf():
    LoadRDF().command()
