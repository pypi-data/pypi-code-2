"""document specific class for Document entities

:organization: Logilab
:copyright: 2008-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.entities import fetch_config
from cubicweb.selectors import is_instance
from cubicweb.entities.adapters import ITreeAdapter

from cubes.vcsfile import entities as vcsentities

from cubes.document.entities import req_branch_scope


class Repository(vcsentities.Repository):

    def default_branch(self):
        if hasattr(self._cw, 'get_cookie'):
            return req_branch_scope(self._cw)
        return {'subversion': None, 'mercurial': u'default'}[self.type]

class VersionedFileITreeAdapter(ITreeAdapter):
    __select__ = is_instance('VersionedFile')
    tree_relation = "filed_under"

    def is_leaf(self):
        return True

    def children(self, entities=True, sametype=False):
        return []

    #1424467: strange overriding of entity attributes/methods over its adapter
    # we have to copy path method from cubicweb.entities.adapters
    # because of name clashing with path attribute
    # XXX (syt) fixed in cw 3.10.8
    def path(self):
        """Returns the list of eids from the root object to this object."""
        path = []
        adapter = self
        entity = adapter.entity
        while entity is not None:
            if entity.eid in path:
                self.error('loop in %s tree: %s', entity.__regid__.lower(), entity)
                break
            path.append(entity.eid)
            try:
                # check we are not jumping to another tree
                if (adapter.tree_relation != self.tree_relation or
                    adapter.child_role != self.child_role):
                    break
                entity = adapter.parent()
                adapter = entity.cw_adapt_to('ITree')
            except AttributeError:
                break
        path.reverse()
        return path


class VersionedFile(vcsentities.VersionedFile):
    fetch_attrs, fetch_order = fetch_config(['name', 'lang', 'pivot_lang'])

    @property
    def abspath(self):
        """omit the root folder, which is fake and whose purpose
        is to group (by filed_under) relation
        """
        return '%s/%s' % (self.filed_under[0].abspath, self.name)

    # edition

    def mark_downloaded_for_edition_by(self, usereid):
        self._cw.execute('SET U might_edit X '
                         'WHERE X eid %(x)s, U eid %(u)s, NOT U might_edit X',
                         {'x': self.eid, 'u' : usereid})

    def unmark_user_for_edition(self, usereid):
        self._cw.execute('DELETE U might_edit X '
                         'WHERE X eid %(x)s, U eid %(u)s',
                         {'x': self.eid, 'u' : usereid})

    #/edition

    # versioning

    def exists_under_branch_scope(self):
        """does not exists in the branch scope"""
        return self.branch_head() is not None

    def up_to_revision(self):
        """return the revision number of the master document where this one has
        been last updated.
        """
        assert not self.pivot_lang
        return self.branch_head() and self.branch_head().up_to_master_revision

    #/versioning

    # i18n

    def dc_language(self):
        lang = self.language
        if lang is None:
            return self._cw._('undefined')
        return self._cw._(lang.name)

    @property
    def untranslated_langs(self):
        rql = self._cw.execute
        used_langs = [trans.lang[0].eid for trans in self.translations]
        if self.lang:
            used_langs.append(self.lang[0].eid)
        if used_langs:
            return rql('Any L,C,N WHERE NOT L eid in (%s), L is Language, '
                       'L code C, L name N' % ','.join(str(eid) for eid in used_langs))
        else:
            return rql('Any L,C,N WHERE L is Language, L code C, L name N')

    # /i18n

class VersionContent(vcsentities.VersionContent):

    @property
    def up_to_master_revision(self):
        """return the revision number of the master document where this one has
        been last updated.
        """
        # take care to rev num == 0...
        if  self.up_to_revision:
            return self.up_to_revision[0].revision
        return None


    def set_up_to_master_revision(self, uptorev):
        """mark a revision of this document as up to the given revision of the
        master document.

        If given `vcentity` should be the VersionContent entity which will hold
        the up_to_revision relation, else the latest revision will be used.
        """
        master = self.file.master_document
        assert self._cw.execute(
            'SET VC1 up_to_revision VC2 '
            'WHERE VC1 eid %(svc)s, VC2 content_for VF2, '
            'VC2 from_revision REV, REV revision %(rev)s, VC1 is VersionContent, '
            'VC2 is VersionContent, VF2 eid %(meid)s',
            {'svc': self.eid, 'rev': uptorev, 'meid' : master.eid})
