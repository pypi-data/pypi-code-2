"""i18ncontent component

provides entities and relations to support multilingual entities

:organization: Logilab
:copyright: 2008-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"


from cubicweb.mixins import MI_REL_TRIGGERS

class I18NContentMixIn(object):
    """base mixin providing a better dc_language implementation for translatable
    entities
    """

    def dc_language(self):
        """return language used by this entity (translated)"""
        if self.language is None:
            # site wide language
            return super(I18NContentMixIn, self).dc_language()
        return self._cw._(self.language.name)

    @property
    def language(self):
        """return the Language entity defining the language of this entity"""
        return self.lang and self.lang[0] or None

    @property
    def master_document(self):
        """if this entity is a translation of another one, return it"""
        if self.pivot_lang:
            return None
        try:
            return self.translation_of[0]
        except IndexError:
            return None

    @property
    def translations(self):
        """return entities which are a translation of this entity"""
        if not self.pivot_lang:
            return ()
        return self.reverse_translation_of

    def set_language(self, langcode):
        """self the language for this entity (mainly for test purpose)"""
        self._cw.execute('SET X lang Y WHERE X eid %(x)s, Y code %(langcode)s',
                         {'x': self.eid, 'langcode': langcode})
        self.cw_clear_relation_cache('lang', 'subject')


MI_REL_TRIGGERS[('lang', 'subject')] = I18NContentMixIn
