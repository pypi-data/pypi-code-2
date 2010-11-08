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
                catalogue.add((doc, FOAF["primaryTopic"], catalogue.identifier))
                catalogue.add((catalogue.identifier, FOAF["isPrimaryTopicOf"], doc))
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
                    log.error("Exception describing: %s\n%s" % (pkg.get("name") or pkg, format_exc()))
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
        if g.identifier.startswith(self.packager.rdf_cat_base()):
            basename = os.path.join(self.options.outdir, os.path.basename(self.packager.rdf_cat_base()))
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

    def describe_packages(self):
        for pkg in self.packages:
            log.info("Describing Package: %s" % (pkg,))
            self.connect() # kludge for auth refusal after some requests

            data = self.client.package_entity_get(pkg)
            if isinstance(data, basestring): # this happens on error, abort
                tmpnam = tempfile.mktemp() + ".html"
                log.error("retrieved %s for %s instead of data" % (tmpnam, pkg))
                fp = open(tmpnam, "w+")
                fp.write(data)
                fp.close()
                continue
            if self.options.debug:
                log.debug("retrieved %s:\n%s" % (pkg, pformat(data)))

            catrec = self.describe_package(data)

            if self.options.nocs:
                self.handler.put(catrec)
            else:
                ctx = self.handler.context(getuser(), "Describing %s from API" % pkg)
                ctx.add(catrec)
                ctx.commit()
            
    def describe_package(self, data):
        uri = self.pkg_uri(data)
        rdf_uri = self.rdf_pkg_uri(data)
        
        catrec = Graph(identifier=rdf_uri)
        catrec.add((rdf_uri, RDF.type, DCAT.CatalogRecord))
        catrec.add((rdf_uri,DC.publisher, URIRef(self.config.get("rdf_publisher", "http://ckan.net/"))))
        catrec.add((rdf_uri,DCAT.dataset, uri))

        catproc  = self.process()
        catproc.use(uri)
        catproc.use(self.api_base())
        catproc.result(catrec)

        dset = Graph(identifier=uri)
        dset.add((uri,RDF.type,DCAT.Dataset))
        dset.add((uri,WDRS.describedby,rdf_uri))
        dset.add((uri,OWL.sameAs,UUID[data["id"]]))
        dset.add((uri,DC.identifier, Literal(data["name"])))

        del data["id"]
        del data["name"]

        if self.options.authoritative:
            dset.add((uri,RDFS.isDefinedBy, rdf_uri))

        if data["url"] is not None:
            dset.add((uri,FOAF.homepage, URIRef(data["url"])))
        del data["url"]

        if data["title"] is not None:
            dset.add((uri,RDFS.label, Literal(data["title"])))
            dset.add((uri,DC["title"], Literal(data["title"])))
        del data["title"]
        if data["notes"] is not None:
            dset.add((uri,DC.description, Literal(data["notes"])))
        del data["notes"]

        if "license" in data and data["license"] is not None:
            rights = URIRef(rdf_uri + "#rights") #BNode()
            dset.add((uri,DC.rights, rights))
            dset.add((rights,RDFS.label, Literal(data["license"])))
            dset.add((rights,RDFS.comment, Literal("TODO: proper URI for licenses")))
        del data["license"]
        del data["license_id"]

        author = URIRef(rdf_uri + u"#author") #BNode()
        if data["author"] or data["author_email"]:
            dset.add((uri,DC.creator, author))
            dset.add((author,RDFS.comment, Literal("TODO: proper URI for author")))
        if data["author"]:
            dset.add((author,FOAF.name, Literal(data["author"])))
        if data["author_email"]:
            dset.add((author,FOAF.mbox, URIRef("mailto:" + data["author_email"])))
        del data["author"]
        del data["author_email"]

        maintainer = URIRef(rdf_uri + u"#maint") #BNode()
        if data["maintainer"] or data["maintainer_email"]:
            dset.add((uri,DC.contributor, maintainer))
            dset.add((maintainer,RDFS.comment, Literal("TODO: proper URI for maintainer")))
        if data["maintainer"]:
            dset.add((maintainer,FOAF.name, Literal(data["maintainer"])))
        if data["maintainer_email"]:
            dset.add((maintainer,FOAF.mbox, URIRef("mailto:" + data["maintainer_email"])))
        del data["maintainer"]
        del data["maintainer_email"]
            
        for tag in data["tags"]:
            dset.add((uri,DCAT.keyword, Literal(tag)))
            #dset.add((uri,DC.subject, self.tag_uri(tag)))
        del data["tags"]

        if data["ratings_average"] is not None:
            dset.add((uri,REV.rating, Literal(str(data["ratings_average"]))))
        # can't useREV.totalVotes since that implies being a Review
        # ask Mr. Ayers
        #if data["ratings_count"] is not None:
        #    g.add((uri,REV.totalVotes,
        #           Literal(data["ratings_count"], datatype=XSD.integer)))
        del data["ratings_average"]
        del data["ratings_count"]

        if data["resources"]:
            for res in data["resources"]:
                distribution = URIRef(res["url"])
                dset.add((uri,DCAT.distribution, distribution))
                description = res["description"].strip()
                if description:
                    dset.add((distribution,RDFS.label, Literal(description)))
                if res["format"]:
                    # have to use dict notation since .format is a method
                    dset.add((distribution,DC["format"], Literal(res["format"])))
        else:
            dset.add((uri,DCAT.distribution, URIRef(data["download_url"])))
        del data["resources"]
        del data["download_url"]
        
        # skip handle groups
        del data["groups"]

        extra = data["extras"]
        del data["extras"]

        if "department" in extra:
            if extra["department"]:
                department = self.dept_uri(extra["department"])
                dset.add((uri,DC.publisher, department))
                dset.add((uri,DC.rightsHolder, department))
                dset.add((department,RDF.type,DC.Agent))
                dset.add((department,FOAF.name, Literal(extra["department"])))
                dset.add((department,RDFS.comment,
                       Literal("TODO: URI for department")))
            del extra["department"]

        if "agency" in extra:
            if extra["agency"]:
                agency = self.dept_uri(extra["agency"])
                dset.add((uri,DC.publisher, agency))
                dset.add((uri,DC.rightsHolder, agency))
                dset.add((agency,RDF.type,DC.Agent))
                dset.add((agency,FOAF.name, Literal(extra["agency"])))
                dset.add((agency,RDFS.comment,
                       Literal("TODO: URI for agencies")))
            del extra["agency"]
            
        if "categories" in extra:
            if extra["categories"]:
                dset.add((uri,DC.subject, Literal(extra["categories"])))
            del extra["categories"]

        if "date_released" in extra:
            if extra["date_released"]:
                obj = Literal(extra["date_released"], datatype=XSD.date)
                dset.add((uri,DC.date, obj))
                dset.add((uri,DC.issued, obj))
            del extra["date_released"]

        if "date_updated" in extra:
            if extra["date_updated"]:
                obj = Literal(extra["date_updated"], datatype=XSD.date)
                dset.add((uri,DC.modified, obj))
            del extra["date_updated"]

        if "import_source" in extra:
            if extra["import_source"]:
                source = extra["import_source"]
                if source.startswith("http://"):
                    src = URIRef(source)
                else:
                    src = BNode()
                    dset.add((src,RDFS.label, Literal(source)))
                dset.add((uri,DC.source, src))
            del extra["import_source"]

        if "geographic_coverage" in extra:
            if extra["geographic_coverage"]:
                # TODO: something fancier here
                dset.add((uri,DC.spatial, Literal(extra["geographic_coverage"])))
            del extra["geographic_coverage"]
        if "geographical_granularity" in extra:
            dset.add((uri,DCAT.granularity, Literal(extra["geographical_granularity"])))
            del extra["geographical_granularity"]

        temporal = ""
        if "temporal_coverage_from" in extra:
            # TODO: infer data types for temporal coverage
            if extra["temporal_coverage_from"]:
                dset.add((uri,ICAL.dtstart,
                       Literal(extra["temporal_coverage_from"])))
            temporal += extra["temporal_coverage_from"]
            del extra["temporal_coverage_from"]
        if "temporal_coverage_to" in extra:
            if extra["temporal_coverage_to"]:
                dset.add((uri,ICAL.dtend,
                       Literal(extra["temporal_coverage_to"])))
            temporal += "-" + extra["temporal_coverage_to"]
            del extra["temporal_coverage_to"]
        if temporal:
            dset.add((uri,DC.temporal, Literal(temporal)))
        if "temporal_granularity" in extra:
            dset.add((uri,DCAT.granularity, Literal(extra["temporal_granularity"])))
            del extra["temporal_granularity"]

        if "external_reference" in extra:
            # TODO: This is almost always ONSHUB. Put somewhere else?
            #if extra["external_reference"]:
            #    dset.add((uri,DC.identifier, Literal(extra["external_reference"])))
                       
            del extra["external_reference"]

        if "national_statistic" in extra:
            if extra["national_statistic"] and extra["national_statistic"] == "yes":
                dset.add((uri,DC.extent, Literal("National Statistic")))
            del extra["national_statistic"]

        if "precision" in extra:
            if extra["precision"]:
                dset.add((uri,RDFS.comment, Literal(extra["precision"])))
            del extra["precision"]
            
        # TODO handle these items
        del data["revision_id"]
        del data["state"]
        if "update_frequency" in extra:
            if extra["update_frequency"]:
                dset.add((uri,DC.accrualPeriodicity, Literal(extra["update_frequency"])))
            del extra["update_frequency"]
            
        for x in data.values():
            if x:
                log.warn("Unhandled data for %s:\n%s" % (uri, pformat(data)))
                break
        for x in extra.values():
            if x:
                log.warn("Unhandled extra for %s:\n%s" % (uri, pformat(extra)))
                break

        catrec += dset

        return catrec
    
    def serialise(self, output):
        g = ConjunctiveGraph(store=self.handler.rdflib.store)

        if output == "-":
            out = sys.stdout
        else:
            out = open(output, "w+")

        if self.options.format is not None:
            rdf_format = self.options.format
        else:
            rdf_format = self.config.get("rdf_format", "n3")

        g.serialize(out, format=rdf_format)

        if output[0] not in ("-",):
            out.close()
            st = os.stat(output)
            log.info("Wrote %d bytes" % (st.st_size,))
        
    def dept_uri(self, name):
        # TODO make URIRef to department
        return BNode()

def genrdf():
    GenerateRDF().command()
