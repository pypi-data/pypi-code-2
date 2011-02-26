from StringIO import StringIO
from ZODB.POSException import POSKeyError

def get_favorites(self):
    out = StringIO()
    pc = self.portal_catalog
    res = pc(meta_type='ATFavorite')
    for r in res:
        print >> out, r.getPath()
        o = r.getObject()
        if o:
            o.getParentNode().manage_delObjects(ids=[o.getId()])
    return out.getvalue()

def get_blogs(self, delete=False):
    out = StringIO()
    pc = self.portal_catalog
    res = pc(meta_type='Blog')
    for r in res:
        path = r.getPath()
        if delete:
            o = r.getObject()
            if o:
                o.getParentNode().manage_delObjects(ids=[o.getId()])
                print >> out, 'Deleted',
        print >> out, path
    return out.getvalue()

    
def move_blogs(self):
    out = StringIO()
    fp = open('%s/Extensions/blogs.txt' % INSTANCE_HOME)
    blogs_dir = self.restrictedTraverse('SimpleBlogs')
    for line in fp:
        line = line.strip()
        paths = line.split('/')
        if len(paths) != 3 or paths[0] != 'Members':
            print >> out, 'Bad blog', line
            continue
        if getattr(blogs_dir, paths[1], None) == None:
            new_id = blogs_dir.invokeFactory('Folder', paths[1])
        else:
            new_id = paths[1]
        obj = self.restrictedTraverse(line)
        parent = obj.getParentNode()
        new_parent = blogs_dir[new_id]
        cp = parent.manage_cutObjects(ids=obj.getId())
        new_parent.manage_pasteObjects(cp)
    print >> out, 'Done moving blogs'

def get_images(self):
    out = StringIO()
    pc = self.portal_catalog
    new_parent = self.Members.sureshvv.ZEROIMAGES
    res = pc(portal_type='Image')
    for r in res:
        try:
            o = r.getObject()
        except AttributeError:
            continue
        if o:
            try:
                sz = o.getSize()
            except AttributeError:
		sz = -100
            except POSKeyError:
                print >> out, 'Deleting', o.getId()
                o.getParentNode().manage_delObjects(ids=[o.getId()])
                continue
            if not sz:
                parent = o.getParentNode()
                print >> out, 'Moving', '/'.join(o.getPhysicalPath()), sz
                cp = parent.manage_cutObjects(ids=o.getId())
                new_parent.manage_pasteObjects(cp)
                continue
            elif sz == -100:
                print >> out, '/'.join(o.getPhysicalPath()), sz
            else:
                print >> out, '/'.join(o.getPhysicalPath())
    print >> out, 'Done'
    return out.getvalue()

def get_toprated(self):
    out = StringIO()
    cat=self.portal_catalog
    crit = dict(portal_type='FeedFeederItem', sort_on='Date', sort_order='descending')
    results = cat(crit)
    for o in results:
        try:
            o = o.getObject()
        except AttributeError:
            continue
        rating = o.editorial_rating()
        print >> out, '/'.join(o.getPhysicalPath()), rating
        
    return out.getvalue()
