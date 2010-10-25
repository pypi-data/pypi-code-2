from StringIO import StringIO

def set_related_items(self):
    """ this fixes schema of old documents """
    out = StringIO()
    fp = open('%s/Extensions/related_items.txt' % INSTANCE_HOME)
    for line in fp:
        items = line.strip().split()
        obj = [ self.restrictedTraverse(i) for i in items ]
        set1 = set(obj[0].getRelatedItems())
        set2 = set(obj[1:])
        if set1 != set2:
            obj[0].setRelatedItems(obj[1:])
            print >> out, 'Changed', items[0], 'had', set1, 'now', set2
    return out.getvalue()

def show_related_items(self, ptype):
    """ this fixes schema of old documents """
    out = StringIO()
    pc = self.portal_catalog
    res = pc(portal_type=ptype)
    for o1 in res:
        try:
            o1 = o1.getObject()
        except AttributeError:
            continue
        items = o1.getRelatedItems()
        if items:
            print >> out, '/'.join(o1.getPhysicalPath()),
            for i in items: print >> out, '/'.join(i.getPhysicalPath()), 
            print >> out
    return out.getvalue()


