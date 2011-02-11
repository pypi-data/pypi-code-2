"""repository abstraction for a mercurial repository

:organization: Logilab
:copyright: 2007-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

from __future__ import with_statement

__docformat__ = "restructuredtext en"

from os import umask, makedirs
from os.path import split, exists, join, dirname
from datetime import datetime

from mercurial import hg, ui, revlog, context, util, commands as hgcmd
from mercurial.node import nullid, short as short_hex

from cubicweb import Binary, QueryError
from cubicweb.server.ssplanner import EditedEntity

from cubes.vcsfile import repo, bridge
from cubes.vcsfile.entities import remove_authinfo

_DELETED = object()

def monkeypatch_mercurial_url():
    from mercurial.url import httphandler
    if hasattr(httphandler, '__del__'):
        del httphandler.__del__
monkeypatch_mercurial_url()


class vcsfile_ui(ui.ui):
    """ redirect output to cubicweb log """
    def __init__(self, loggable):
        ui.ui.__init__(self)
        self.cw_loggable = loggable

    def copy(self):
        return self

    def interactive(self):
        return False

    # XXX beware encoding issues wrt localized outputs ...
    def write(self, *args, **kwargs):
        if self._buffers:
            self._buffers[-1].extend([str(a) for a in args])
        else:
            for a in args:
                self.cw_loggable.debug(str(a).strip())

    def write_err(self, *args, **kwargs):
        for a in args:
            self.cw_loggable.error(str(a).strip())


def bw_nb_revisions(changelog):
    """return the number of revisions in a repository's changelog,
    assuring mercurial < 1.1 compatibility
    """
    try:
        return len(changelog)
    except AttributeError: # hg < 1.1
        return changelog.count()


class HGRepository(repo.VCSRepository):
    type = 'hg'

    def pull_or_clone_cache(self, url):
        if not exists(self.path):
            pdir = dirname(self.path)
            if not exists(pdir):
                makedirs(pdir)
            self.info('cloning %s into %s', url, self.path)
            hgcmd.clone(vcsfile_ui(self), str(url),
                        dest=self.path, stream='compressed', noupdate=True)
        else:
            self.info('pulling from %s into %s', remove_authinfo(url), self.path)
            vui = vcsfile_ui(self)
            hgcmd.pull(vui, hg.repository(vui, self.path), source=str(url))

    def import_content(self, repoentity, commitevery=10):
        """import content from the mercurial repository"""
        assert self.eid == repoentity.eid
        if not exists(self.path):
            self.info('repository %s not accessible in %s',
                      repoentity.dc_title(), self.path)
            return
        try:
            repo = self.hgrepo()
        except Exception, ex:
            self.exception('Impossible to open repository %s (%s)', self, ex)
            return
        # actual rev is the *number* of revision, latest rev the highest
        # revision number while hg revisions start at 0 -> - 1
        actualrev = bw_nb_revisions(repo.changelog) - 1
        session = repoentity._cw
        latestrev = repoentity.latest_known_revision()
        if actualrev < latestrev:
            # striped repo
            # very minimal support, this won't work if local number of
            # revisions has changed due to the strip
            self.warning('%s: strip detected ? latest known revision is %s, '
                         'latest repository revision is %s', self.path,
                         latestrev, actualrev)
            session.execute('DELETE Revision X WHERE X revision > %(rev)s',
                            {'rev': actualrev})
            return
        self.info('hg repo %s: known revisions up to %s, repo revision %s',
                  self.path, latestrev, actualrev)
        for i in xrange(latestrev + 1, actualrev + 1):
            self.info('importing revision %s', i)
            try:
                self.import_revision(repoentity, repo, i)
            except:
                self.critical('error while importing revision %s of %s',
                              i, self.path, exc_info=True)
                raise
            if not i % commitevery:
                # give a change to threads waiting for a pool by freeing it then
                # reacquiring it
                session.commit()
                session.set_pool()

    def import_revision(self, repoentity, repo, i):
        session = repoentity._cw
        execute = session.execute
        node = repo.changelog.node(i)
        changeset = unicode(short_hex(node))
        if execute('Any X WHERE X from_repository R, R eid %(repo)s, X changeset %(cs)s',
                   {'repo': repoentity.eid, 'cs': changeset}):
            self.warning('skip revision %s, seems already imported',
                         changeset)
            return
        ctx = repo.changectx(i)
        date = datetime.fromtimestamp(ctx.date()[0])
        #taglist = ctx.tags() #repo.nodetags(node)
        revdata = {'date': date, 'revision': i,
                   'author': unicode(ctx.user(), self.encoding, 'replace'),
                   'description': unicode(ctx.description(), self.encoding, 'replace'),
                   'changeset': changeset,
                   'branch': unicode(ctx.branch()),
                   }
        self.imported_revision = i # for hooks
        parents = [short_hex(n) for n in repo.changelog.parents(node)
                   if n != nullid]
        if parents:
            if len(parents) == 1:
                parents = execute('Revision X WHERE X changeset %(cs)s, '
                                  'X from_repository R, R eid %(r)s',
                                  {'cs': parents[0], 'r': self.eid})
            else:
                parents = execute('Revision X WHERE X changeset IN (%s), '
                                  'X from_repository R, R eid %%(r)s'
                                  % ','.join("'%s'"%cs for cs in parents),
                                  {'r': self.eid})
        revdata['parents'] = [r[0] for r in parents]
        reveid = bridge.import_revision(session, self.eid, **revdata)
        if not repoentity.import_revision_content:
            return
        changes = repo.status(ctx.parents()[0].node(), ctx.node())[:3]
        modified, added, removed = changes
        path_filter = repoentity.subpath
        for path in modified + added:
            upath = unicode(path, self.encoding, 'replace')
            if not (path_filter is None or upath.startswith(path_filter)):
                continue
            directory, fname = split(path)
            session.transaction_data['vcs_importing'] = self.eid, directory, fname, i
            filectx = ctx[path]
            vcdata = {'data': Binary(filectx.data())}
            renameinfo = filectx.renamed()
            if renameinfo:
                oldfile, fileid = renameinfo
                pfctx = repo.filectx(oldfile, fileid=fileid)
                pcs = short_hex(pfctx.node())
                dir, name = split(unicode(oldfile, self.encoding, 'replace'))
                pvc = execute('VersionContent X WHERE '
                              'X from_revision REV, REV changeset %(cs)s, '
                              'REV from_repository R, R eid %(r)s, '
                              'X content_for VF, VF directory %(dir)s, VF name %(name)s',
                              {'cs':  pcs, 'r': self.eid,
                               'dir': dir, 'name': name})
                if pvc:
                    assert len(pvc) == 1
                    if oldfile in removed:
                        vcdata['vc_rename'] = pvc[0][0]
                    else:
                        vcdata['vc_copy'] = pvc[0][0]
                else:
                    self.error('detected copy or rename of %s@%s but unable'
                               ' to find associated version content',
                               oldfile, pcs)
            bridge.import_version_content(session, self.eid, reveid, upath,
                                          date, **vcdata)
        for path in removed:
            upath = unicode(path, self.encoding, 'replace')
            if not (path_filter is None or upath.startswith(path_filter)):
                continue
            bridge.import_deleted_version_content(session, self.eid, reveid,
                                                  upath, date)
        bridge.set_at_revision(session, reveid)

    def hgrepo(self):
        return hg.repository(ui.ui(), self.path)

    def _file_content(self, path, rev):
        """extract a binary string with the content of the file at `path` for
        revision `rev` in the repository
        """
        ctx = self.hgrepo().changectx(rev)
        return Binary(ctx[path].data())

    def revision_transaction(self, session, entity):
        """open a transaction to create a new revision corresponding to the
        given entity
        """
        return HGTransaction(self, session, entity)

    def add_versioned_file_content(self, session, transaction, vf, entity,
                                   data):
        """add a new revision of a versioned file"""
        vfpath = self.encode(vf.path)
        transaction.changes[vfpath] = context.memfilectx(
            vfpath, data.getvalue(), islink=False, isexec=False, copied=None)
        return vf.path

    def add_versioned_file_deleted_content(self, session, transaction, vf,
                                           entity):
        """add a new revision of a just deleted versioned file"""
        transaction.changes[self.encode(vf.path)] = _DELETED
        return vf.path


class HGTransaction(object):
    def __init__(self, repohdlr, session, revision):
        self.repohdlr = repohdlr
        self.session = session
        self.revision = revision
        self.repo = repohdlr.hgrepo()
        self._wlock = self.repo.wlock()
        self._lock = self.repo.lock()
        self.extra = {}
        self.changes = {}

    @property
    def rev(self):
        """newly created revision number"""
        return bw_nb_revisions(self.repo.changelog)

    def _filectx(self, repo, memctx, path):
        """callable receiving the repository, the current memctx object and the
        normalized path of requested file, relative to repository root. It is
        fired by the commit function for every file in 'files', but calls order
        is undefined. If the file is available in the revision being committed
        (updated or added), filectxfn returns a memfilectx object. If the file
        was removed, filectxfn raises an IOError. Moved files are represented by
        marking the source file removed and the new file added with copy
        information (see memfilectx).
        """
        if self.changes[path] is _DELETED:
            raise IOError()
        return self.changes[path]

    def precommit(self):
        if not self.changes:
            raise QueryError('nothing changed')

    def commit(self):
        # XXX: make umask configurable
        oldumask = umask(022)
        try:
            self._commit()
        finally:
            umask(oldumask)

    def _commit(self):
        # XXX merging branches
        encode = self.repohdlr.encode
        branch = encode(self.revision.cw_attr_cache.get('branch') or u'default')
        if branch != u'default':
            self.extra['branch'] = branch
        author = encode(self.revision.cw_attr_cache.get('author', u''))
        msg = encode(self.revision.cw_attr_cache.get('description', u''))
        try:
            p1 = self.repo.branchtags()[branch]
        except KeyError:
            # new branch
            p1 = self.repo.branchtags().get('default')
        p2 = None
        # ensure mercurial will use configured repo encoding, not locale's
        # encoding
        # XXX modifying module's global is not very nice but I've no other idea
        try:
            # mercurial >= 1.3.1
            from mercurial import encoding
            encoding.encoding = self.repohdlr.encoding
        except ImportError:
            util._encoding = self.repohdlr.encoding
        ctx = context.memctx(self.repo, (p1, p2), msg, self.changes.keys(),
                             self._filectx, author, extra=self.extra)
        try:
            # mercurial < 1.3.1
            node = self.repo._commitctx(ctx, force=True, force_editor=False,
                                        empty_ok=True, use_dirstate=False,
                                        update_dirstate=False)
        except AttributeError:
            node = self.repo.commitctx(ctx)
        # update revision's record to set correct changeset
        #
        # take care, self.repo != self.session.repo (eg mercurial repo instance
        # / rql repository)
        source = self.session.repo.system_source
        # remove previous cached value to only save the changeset
        with setattrcm(self.revision, 'cw_edited', EditedEntity(self.revision)) as rev:
            rev.cw_edited['changeset'] = unicode(short_hex(node))
            source.update_entity(self.session, rev)
        # XXX restore entity's dict?
        self.rollback()

    def rollback(self):
        try:
            # mercurial >= 1.3.1
            self._wlock.release()
            self._lock.release()
        except AttributeError:
            del self._wlock
            del self._lock



class setattrcm(object):
    def __init__(self, obj, attr, value):
        self.obj = obj
        self.attr = attr
        self.value = value

    def __enter__(self):
        self.old = getattr(self.obj, self.attr)
        setattr(self.obj, self.attr, self.value)
        return self.obj

    def __exit__(self, exctype, value, traceback):
        setattr(self.obj, self.attr, self.old)


from logging import getLogger
from cubicweb import set_log_methods
set_log_methods(HGRepository, getLogger('cubicweb.sources.hg'))
