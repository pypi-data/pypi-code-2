## Script (Python) "bibflexview_get_authors"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=prop_src, path=''
##title=
##

# XXX verlaesst sich auf existenz eines typs "all", eine entsprechende ueberpruefung muesste
# in die konfig-seite!
if not prop_src.authors_from_references:
    authors = list(prop_src.authors)
else:            
    #cat = context.portal_catalog
    cat = context.queryCatalog
    pubs = cat({'portal_type': context.portal_bibliography.getReferenceTypes(), 'Language':'all', 'path':path});
    authors = []
    for p in pubs:
        # eleganter/zukunftssicherer waers, vorname/nachname aus der referenz zu holen
        # aber wenn wir hier direkt auf die objekte zugreifen wirds arg langsam
        pauths = p.Authors.replace('and ', '').split(',')
        # wir sollten jetzt ne liste mit n*2 eintraegen haben. wenn nicht versuchen
        # wir erst gar nicht draus schlau zu werden
        if len(pauths) % 2 == 0:
            for i in [x * 2 for x in range(len(pauths)/2)]:
                pau = pauths[i]
                if pau not in authors: authors.append(pau)
authors.sort()
return authors
