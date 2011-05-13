from lxml import objectify

namespace = "http://xspf.org/ns/0/"

E = objectify.ElementMaker( annotate=False,
                            namespace=namespace,
                            nsmap={ None:
                                     namespace } )
