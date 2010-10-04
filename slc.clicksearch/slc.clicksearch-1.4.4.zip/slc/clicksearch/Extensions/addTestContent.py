# Method to prepopulate some testing material to play with
import feedparser, random, pprint

TYP = {'Link': 'http://osha.europa.eu/osha/portal/search_rss?Subject=accident_prevention&Language=en&review_state=published&sort_on=effective',
         'Document': 'http://osha.europa.eu/search_rss?portal_type=PressRelease&Language=en&review_state=published&sort_on=effective',
         'File': 'http://osha.europa.eu/search_rss?portal_type=File&Language=en&review_state=published&sort_on=effective&object_provides=slc.publications.interfaces.IPublicationEnhanced',
         'News Item': 'http://osha.europa.eu/search_rss?portal_type=News%20Item&Language=en&review_state=published&sort_on=effective',
         'Event': 'http://osha.europa.eu/search_rss?portal_type=Event&Language=en&review_state=published&sort_on=start'
            }

SUBJECTS = ['msd', 'accident_prevention', 'young_workers']

def addTestContent(self):
    log = []

    wftool = self.portal_workflow

    FOLDERS = {'good_practice':None, 'topics': None, 'sector':None}
    for f in FOLDERS.keys():
        if not hasattr(self, f):
            self.invokeFactory('Folder', f)
        F = getattr(self, f)
        F.setTitle(f.upper())
        FOLDERS[f] = F

    for T in TYP.keys():
        log.append(T)
        data = feedparser.parse(TYP[T])
        for item in data['entries']:
            log.append("  > "+item['title'])
            F = random.choice(FOLDERS.values())
            id = item['id']
            if '?' in id:
                id = id.split('?')[0]
            id = id.split('/')[-1]
            if id in F.objectIds():
                # there may be identical ids from the feeds. We only need testdata so we simply skip here
                continue
            F.invokeFactory(T, id)
            ITEM = getattr(F, id)
            ITEM.setTitle(item['title'])
            ITEM.setDescription(item['summary'])

            # randomly publish items, but not for image, which has no workflow.
            if random.choice([True, False]) and T not in ['File', 'Image']:
                wftool.doActionFor(ITEM, 'publish')

            ITEM.setSubject([random.choice(SUBJECTS)])
            ITEM.reindexObject()

    self.REQUEST.RESPONSE.setHeader('Content-type', 'text/plain')
    return "\n".join(log)


