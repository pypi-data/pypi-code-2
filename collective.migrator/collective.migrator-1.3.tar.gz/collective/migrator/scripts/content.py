from StringIO import StringIO
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
