from pprint import pformat
import ckanclient
from ordf.graph import ConjunctiveGraph
from ckanrdf.command import Command

log = __import__("logging").getLogger("ckanlinks")

query = """
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX void: <http://rdfs.org/ns/void#>

SELECT DISTINCT ?dset COUNT(?url) WHERE {
    <http://semantic.ckan.net/catalogue> dcat:record ?rec .
    ?rec dcat:dataset ?dset .
    ?dset void:exampleResource ?url
}
"""

class CkanLinks(Command):
    parser = Command.StandardParser(usage="%prog [options]")

    def command(self):
        store = self.handler.rdflib.store
        if hasattr(store, "sparql_query"):
            select = store.sparql_query
        else:
            select = ConjunctiveGraph(store).query

        client = self.client
        log.info("Requesting CKAN Package")
        ckan = client.package_entity_get("ckan")
        log.info("%s %s" % (client.last_status, client.last_location))

        links = [e for e in ckan["extras"] if e.startswith("links:")]
        for link in links:
            del ckan["extras"][link]

        ## kludge to try to pass the api
        del ckan["id"]
        if ckan["relationships"] == []:
            del ckan["relationships"]
        del ckan["ratings_average"]
        del ckan["ratings_count"]
        del ckan["ckan_url"]
        if ckan["groups"] == []:
            del ckan["groups"]

        for link, count in select(query):
            base, pkg = link.rsplit("/",1)
            if pkg == "ckan":
                continue
            ckan["extras"]["links:%s" % pkg] = count.toPython()

        log.info("Saving CKAN Package")
        client.package_entity_put(ckan)
        if client.last_status == 200:
            log.info("%s %s" % (client.last_status, client.last_message))
        else:
            log.error("%s %s" % (client.last_status, client.last_message))
            log.debug(pformat(ckan))

def ckanlinks():
    CkanLinks().command()
