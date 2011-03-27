from openbiblio.commands import Command
from ordf.namespace import BIBO, DC, OWL
from ordf.term import BNode, URI
log = __import__("logging").getLogger(__name__)

class Materialise(Command):
    summary = "Materialise authors and publishers and fixup URIs"
    usage = "config.ini"
    parser = Command.standard_parser(verbose=False)

    def command(self):
        from openbiblio import handler
        from pylons import config
        sprefix = config.get("openbiblio.serials_prefix", "BB")
        
        for doc in self.docs():
            log.info("processing %s" % doc.identifier)
            contributors = doc.distinct_objects(doc.identifier, DC["contributor"])
            publishers = doc.distinct_objects(doc.identifier, DC["publisher"])
            for person_id in contributors + publishers:
                if isinstance(person_id, URIRef):
                    continue
                person = doc.bnc((person_id, None, None), identifier=person_id)
                same = person.distinct_objects(person_id, OWL["sameAs"])
                if len(same) == 0:
                    log.warn("%d has no sameAs links..." % person_id)
                    continue
                if len(same) > 1:
                    log.warn("%d has more than one sameAs link..." % person_id)
                same = same[0]
                if not isinstance(same, URIRef):
                    log.error("sameAs: %s is not a URI" % same)

                doc -= person
                root, slug = same.rsplit("/", 1)
                if not same.startswith(slug):
                    new_uri = self.new_identifier(root)
                    person = person.replace((person_id, None, None), (new_person_id, None, None),
                                            identifier=new_uri)
                    
                doc = doc.replace((None, None, person_id), (None, None, person.identifier),
                                  identifier=doc.identifier)
                doc += person

            print doc.serialize(format="n3")
            
    def new_identifier(self, root):
        from pylons import config
        serialis = config.get("openbiblio.serials", "openbiblio.serials")
        sprefix = config.get("openbiblio.serials_prefix", "BB")
        with flockdb(serials, "w") as db:
            key = str(root)
            try:
                current = db[key]
            except KeyError:
                current = 9999
            serial = current + 1
            db[key] = serial
        return URIRef("%s%s%09d" % (root, sprefix, serial))
        
    def docs(self):
        from openbiblio import handler
        offset, limit = 0, 10
        qt = """
        PREFIX bibo: %(bibo)s
        SELECT DISTINCT ?doc WHERE {
            ?doc a bibo:Document
        } ORDER BY ?doc LIMIT %(limit)s OFFSET %(offset)s
        """
        while True:
            q = qt % { "bibo": BIBO[""].n3(), "limit": limit, "offset": offset }
            docs = [x[0] for x in handler.query(q)]
            for doc in docs:
                yield handler.get(doc)
            if len(docs) < limit:
                break
