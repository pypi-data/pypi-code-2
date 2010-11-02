# Copyright (c) 2010, Yaco Sistemas <lgs@yaco.es>.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE.

import os
import ConfigParser

from repoze.what.adapters import BaseSourceAdapter, SourceError


def U(text, encoding='utf8'):
    """Simple function to convert a string into a unicode object"""
    return unicode(text, encoding)


class CommonAdapter(BaseSourceAdapter):
    """Abstract base class for the group and permission adapters"""

    def __init__(self, authz_file):
        """Base constructor.

        Reads the groups or permission information from the authz_file

        Arguments:

          authz_file: is a init style file with information about
                      groups and permissions
        """
        super(CommonAdapter, self).__init__(writable=False)

        if not os.path.exists(authz_file):
            raise SourceError('Unable to find the authorization file "%s"'
                              % authz_file)

        self._data = ConfigParser.ConfigParser()
        self._data.read(authz_file)

        self._sections = self._load_sections()

    def _load_sections(self):
        """Subclasses should implement this"""
        raise SourceError("This is implemented in the groups and "
                          "permissions adapter")

    def _find_sections(self, hint):
        """Subclasses should implement this"""
        raise SourceError("This is implemented in the groups and "
                          "permissions adapter")

    def _get_all_sections(self):
        """Return all sections in this source adapter"""
        return self._sections

    def _get_section_items(self, section):
        """Return the items of the given section"""
        return self._sections[section]

    def _item_is_included(self, section, item):
        """True if the given item is included in the given section"""
        return item in self._sections[section]

    def _section_exists(self, section):
        """True if the section is included in this source adapter"""
        return section in self._sections.keys()


class HgwebdirGroupsAdapter(CommonAdapter):
    """Source adapter for groups"""

    def _load_sections(self):
        """Construct the sections and items information of this source.

        The ini file with the information should have been read before.

        The groups can be found in two places:

          - Inside the [groups] section, every option is a group and its
            members are the comma/space separate items in the value.
          - Inside the other sections a line like 'user = rw' is handled
            by creating a group with just an item. The name of the group
            is the same as its only item.
        """
        sections = {}

        for section in self._data.sections():
            if section == 'groups':
                for group, items in self._data.items(section):
                    members = [U(it).strip(u",") for it in items.split()]
                    sections[U(group)] = set(members)
            else:
                for name in self._data.options(section):
                    if not name.startswith(u"@") and name != u'*':
                        group = U(name)
                        if group in sections.keys():
                            raise SourceError('There is already a group named '
                                              '"%s". Maybe you forgot an @'
                                              % group)
                        sections[group] = set((group, ))

        return sections

    def _find_sections(self, hint):
        """Return a set of groups (sections) the user belongs to.

        Arguments:
          hint: a repoze credentials dictionary. The userid is in the
                repoze.what.userid key
        """
        userid = hint['repoze.what.userid']
        answer = set()
        for section, items in self._sections.items():
            if userid in items:
                answer.add(section)
        return answer


class HgwebdirPermissionsAdapter(CommonAdapter):
    """Source adapter for permissions"""

    def _load_sections(self):
        """Construct the sections and items information of this source.

        The ini file with the information should have been read before.

        The permissions are built from the sections of the ini file.
        The 'groups' section is special and ignored. From all the other
        sections, two permissions are created, one for read access and
        one for write access. The groups that have these permissions
        are built from the options and values of such sections.
        """

        sections = {}

        for section in self._data.sections():
            if section == 'groups':
                continue

            read_permission = U(section) + u'-read'
            write_permission = U(section) + u'-write'
            sections[read_permission] = set()
            sections[write_permission] = set()

            for name, value in self._data.items(section):
                if name == u'*':
                    continue

                if name.startswith(u"@"):
                    group = U(name[1:])
                else:
                    group = U(name)

                if 'r' in value:
                    sections[read_permission].add(group)

                if 'w' in value:
                    sections[write_permission].add(group)

        return sections

    def _find_sections(self, hint):
        """Return the set of permission that has the group.

        Arguments:
          hint: the group name
        """
        groupid = hint
        answer = set()
        for section, items in self._sections.items():
            if groupid in items:
                answer.add(section)
        return answer


def get_public_repositories(authz_file):
    """Returns a list of repositories that should not be protected.

    These repositories have a special line inside their section:
      * = r
    that means that everybody (*) can read them.
    """
    if not os.path.exists(authz_file):
        raise ValueError('Unable to find the authorization file "%s"'
                         % authz_file)

    data = ConfigParser.ConfigParser()
    data.read(authz_file)

    public_repositories = []

    for section in data.sections():
        if section == 'groups':
            continue

        for name, value in data.items(section):
            if name == u'*' and value == u'r':
                public_repositories.append(U(section))
                break

    return public_repositories
