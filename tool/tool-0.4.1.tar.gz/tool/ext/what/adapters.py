from repoze.what.adapters import BaseSourceAdapter

class DocuGroupSourceAdapter(BaseSourceAdapter):
    """Docu group source adapter"""

    def _get_all_sections(self):
        return Group.objects(db)

    def _get_section_items(self, section):
        return Member.objects(db).where(groups__contains=section)

    def _find_sections(self, credentials):
        userid = credentials['repoze.what.userid']
        return Member.object(db, userid)

    def _include_items(self, section, items):
        for item in items:
            if not section in item.groups:
                item.groups.append(section)
                item.save()

    def _exclude_items(self, section, items):
        for item in items:
            item.groups.pop(section)
            item.save()

    def _item_is_included(self, section, item):
        return item in self.get_section_items(section)

    def _create_section(self, section):
        self.fake_sections[section] = set()

    def _edit_section(self, section, new_section):
        self.fake_sections[new_section] = self.fake_sections[section]
        del self.fake_sections[section]

    def _delete_section(self, section):
        Group.objects(db, section).delete()

    def _section_exists(self, section):
        section in Group.objects(db)


class FakeGroupSourceAdapter(BaseSourceAdapter):
    """Mock group source adapter"""

    def __init__(self, *args, **kwargs):
        super(FakeGroupSourceAdapter, self).__init__(*args, **kwargs)
        self.fake_sections = {
            u'admins': set([u'andy', u'rms']),
            u'developers': set([u'rms', u'linus']),
            u'trolls': set([u'sballmer']),
            u'python': set(),
            u'php': set()
            }

    def _get_all_sections(self):
        return self.fake_sections

    def _get_section_items(self, section):
        return self.fake_sections[section]

    def _find_sections(self, credentials):
        username = credentials['repoze.what.userid']
        return set([n for (n, g) in self.fake_sections.items()
                    if username in g])

    def _include_items(self, section, items):
        self.fake_sections[section] |= items

    def _exclude_items(self, section, items):
        for item in items:
            self.fake_sections[section].remove(item)

    def _item_is_included(self, section, item):
        return item in self.fake_sections[section]

    def _create_section(self, section):
        self.fake_sections[section] = set()

    def _edit_section(self, section, new_section):
        self.fake_sections[new_section] = self.fake_sections[section]
        del self.fake_sections[section]

    def _delete_section(self, section):
        del self.fake_sections[section]

    def _section_exists(self, section):
        return self.fake_sections.has_key(section)

class FakePermissionSourceAdapter(BaseSourceAdapter):
    """Mock permissions source adapter"""

    def __init__(self, *args, **kwargs):
        super(FakePermissionSourceAdapter, self).__init__(*args, **kwargs)
        self.fake_sections = {
            u'see-site': set([u'trolls']),
            u'edit-site': set([u'admins', u'developers']),
            u'commit': set([u'developers'])
            }

    def _get_all_sections(self):
        return self.fake_sections

    def _get_section_items(self, section):
        return self.fake_sections[section]

    def _find_sections(self, group_name):
        return set([n for (n, p) in self.fake_sections.items()
                    if group_name in p])

    def _include_items(self, section, items):
        self.fake_sections[section] |= items

    def _exclude_items(self, section, items):
        for item in items:
            self.fake_sections[section].remove(item)

    def _item_is_included(self, section, item):
        return item in self.fake_sections[section]

    def _create_section(self, section):
        self.fake_sections[section] = set()

    def _edit_section(self, section, new_section):
        self.fake_sections[new_section] = self.fake_sections[section]
        del self.fake_sections[section]

    def _delete_section(self, section):
        del self.fake_sections[section]

    def _section_exists(self, section):
        return self.fake_sections.has_key(section)

'''
from repoze.what.adapters import BaseSourceAdapter

class _DocuAdapter(BaseSourceAdapter):
    """Base class for Docu adapters."""

    schema = NotImplemented

    def __init__(self, storage):
        """
        Instantiates the Docu source adapter.

        :param storage:
            the Docu storage adapter instance.

        """
        super(_DocuAdapter, self).__init__(writable=True)
        self.storage = storage

    def _where(self, **kwargs):
        return self.schema.objects(self.storage).where(**kwargs)

    def _get_sections_of_item(self, item):
        sections = []
#        filter = {'items': {'$in':[item]}}
#        sections_of_item = self.db[self.collection].find(filter)
        sections_of_item = self._where(groups__contains=[item])

        for section in sections_of_item:
            sections.append(section['section'])

        return set(sections)

    def _get_section_ref(self, section, items = None, fields = None):
        d = {'section':section}
        if items is not None:
            d.update({'items': items})

        return self.db[self.collection].find_one(d, fields = fields)

    # Sections

    def _get_all_sections(self):
        sections = {}
        try:
            all_sections = self.db[self.collection].find()
        except:
            msg = ('There was a problem with the source while retrieving the'
                            ' sections')
            raise adapters.SourceError(msg)

        for section in all_sections:
            sections.update({section['section']: set(section['items'])})
        return sections

    def _create_section(self, section):
        try:
            what = {'section': section, 'items': [] }
            self.db[self.collection].save(what)
        except:
            msg = "The %r section could not be added" % section
            raise adapters.SourceError(msg)

    def _edit_section(self, section, new_section):
        section_ref = self._get_section_ref(section)

        try:
            section_ref['section'] = new_section
            self.db[self.collection].save(section_ref)
        except:
            msg = "The %r section could not be edited" % section
            raise adapters.SourceError(msg)

    def _delete_section(self, section):
        try:
            section_ref = self._get_section_ref(section)
            self.db[self.collection].remove(section_ref)
        except:
            msg = "The %r section could not be deleted" % section
            raise adapters.SourceError(msg)

    def _section_exists(self, section):
        try:
            value = self._get_section_ref(section, fields = ['_id'])
        except:
            msg = 'There was a problem with the source'
            raise adapters.SourceError(msg)

        if value is not None:
            return True
        else:
            return False

    # Items

    def _get_section_items(self, section):
        section_ref = self._get_section_ref(section)
        print section, section_ref
        try:
            # Gets all members of the set.
            items = set(section_ref['items'])
        except:
            msg = ("There was a problem with the source while retrieving the"
                    " %r section") % section
            raise adapters.SourceError(msg)

        return items

    def _include_items(self, section, items):
        try:
            section_ref = self._get_section_ref(section)
            section_ref['items'] += items
            self.db[self.collection].save(section_ref)
        except:
            msg = "The %r items could not be added to the %r section" % \
                      (items, section)
            raise adapters.SourceError(msg)

    def _exclude_items(self, section, items):
        section_ref = self._get_section_ref(section)

        for value in items:
            section_ref['items'].remove(value)

        try:
            self.db[self.collection].save(section_ref)
        except:
            msg = "The %r items could not be removed from the %r section" % \
                      (items, section)
            raise adapters.SourceError(msg)

    def _item_is_included(self, section, item):
        section_ref = self._get_section_ref(section)

        if item in section_ref['items']:
            return True
        else:
            return False

# Source adapters

class mongodbGroupSourceAdapter(_mongodbAdapter):
    collection = 'groups'

    def _find_sections(self, credentials):
        """Return group names the authenticated user belongs to."""

        userid = credentials['repoze.what.userid']
        return self._get_sections_of_item(userid)


class mongodbPermissionSourceAdapter(_mongodbAdapter):
    collection = 'permissions'

    def _find_sections(self, group):
        """Return permission names granted to the group."""
        return self._get_sections_of_item(group)
'''
