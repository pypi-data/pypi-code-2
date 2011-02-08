import sys
import DateTime # zope
import transaction
import datetime
from AccessControl.SecurityManagement import \
    newSecurityManager, setSecurityManager
from Testing.makerequest import makerequest

site = app.unrestrictedTraverse(sys.argv[1])

print "Logging in as %s" % sys.argv[2]
user = site.acl_users.getUser(sys.argv[2])

newSecurityManager(None, user)
site = makerequest(app).unrestrictedTraverse(sys.argv[1])

last = DateTime.DateTime('1970/01/01')

start = datetime.datetime.now()
indexed = 0
retrieving = site.portal_linkchecker.retrieving

seen = set()

while True:
    total = len(site.portal_catalog_real)
    docs_remaining = site.portal_catalog.searchResults(
        Language='all', modified=dict(query=last, range='min'),
        sort_on='modified')
    count_remaining = len(docs_remaining)
    print "Indexing documents (%s total, %s remaining)" % (total, count_remaining)
    i = 0
    for doc in docs_remaining:
        if i >= 500:
            break
        if (doc.getRID(), doc.modified) in seen:
            continue
        seen.add((doc.getRID(), doc.modified))
        try:
            doc = doc.getObject()
            last_modified = doc.modified()
            i += 1
        except Exception, e:
            print "Crawl raised an error for %s: %s" % (doc.getPath(), str(e))
            continue
        retrieving.retrieveObject(doc, online=False)
    indexed += i
    time_passed = datetime.datetime.now() - start
    time_per_doc = (time_passed.days * (24*3600) + time_passed.seconds) / float(indexed)
    time_remaining = (count_remaining-i) * time_per_doc
    print "Indexed %s documents in %s (%ss/doc, %s remaining)" % (indexed, time_passed, time_per_doc, datetime.timedelta(seconds=int(time_remaining)))
    # Allow overlap because the index granularity is only second-wise, that's what the "seen" filter is for to counter.
    last = last_modified - 0.001
    print last, i
    transaction.commit()
    if i == 0:
        break


print "Forcing synchronisation with LMS"
site.portal_linkchecker.database.sync()

transaction.commit()
