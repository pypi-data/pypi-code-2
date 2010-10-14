import sys
from os import listdir, path as osp

from cubicweb import Binary



def import_directory(cw, directory, mapfolders=True, bfss=False,
                     fsencoding=sys.stdout.encoding or 'utf-8', quiet=False,
                     _parent=None, _indent='', _alreadyimported=None):
    cw.set_pool()
    assert bfss, 'not implemented'
    if bfss:
        cw.transaction_data['fs_importing'] = True
    if _parent is None:
        directory = osp.abspath(osp.normpath(directory))
    # getting directory content will check it's validity, do it before creating
    # any Folder entity
    dirfiles = listdir(directory)
    # XXX what if not bfss
    if mapfolders:
        _parent = folder_entity(cw, directory, parent=_parent, fsencoding=fsencoding)
        _alreadyimported = set(x.getvalue() for x, in cw.execute(
            "Any fspath(D) WHERE X data D, X filed_under F, F eid %(f)s",
            {'f': _parent.eid}))
    elif _alreadyimported is None:
        _alreadyimported = set(x.getvalue() for x, in cw.execute(
            "Any fspath(D) WHERE X data D, X is File"))
    if not quiet:
        print _indent + '** importing directory', directory
    for fname in dirfiles:
        fpath = osp.join(directory, fname)
        if osp.isdir(fpath):
            import_directory(cw, fname, mapfolders, bfss, fsencoding, quiet,
                             _parent=_parent, _indent=_indent + '  ')
        else:
            # XXX check file already imported when not mapping
            if fpath in _alreadyimported:
                if not quiet:
                    print _indent + '  skipping already imported', fname
                continue
            if not quiet:
                print _indent + '  importing', fname
            if isinstance(fname, str):
                fname = unicode(fname, fsencoding)
            if bfss:
                efile = cw.create_entity('File', data_name=fname,
                                         data=Binary(fpath))
            else:
                stream = open(fpath, 'rb')
                efile = cw.create_entity('File', data_name=fname,
                                         data=Binary(stream.read()))
                stream.close()
            if mapfolders:
                efile.set_relations(filed_under=_parent)


def folder_entity(cw, directory, parent=None, fsencoding='utf-8'):
    if isinstance(directory, str):
        directory = unicode(directory, fsencoding)
    if parent is None:
        rset = cw.execute('Folder X WHERE X name %(name)s', {'name': directory})
    else:
        rset = cw.execute('Folder X WHERE X name %(name)s, X filed_under P, P eid %(p)s',
                          {'name': osp.dirname(directory), 'p': parent.eid})
    if rset:
        return rset.get_entity(0, 0)
    # create the folder
    if parent is None:
        return cw.create_entity('Folder', name=directory)
    return cw.create_entity('Folder', name=directory, filed_under=parent)
