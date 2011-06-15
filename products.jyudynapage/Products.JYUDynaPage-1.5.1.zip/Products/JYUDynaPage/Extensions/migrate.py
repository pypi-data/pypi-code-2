from Products.CMFCore.utils import getToolByName
from StringIO import StringIO

from Products.contentmigration.basemigrator.walker import CatalogWalker
from Products.contentmigration.migrator import InlineFieldActionMigrator

from types import StringType, UnicodeType

class JYUDynaPageMigrator(InlineFieldActionMigrator):
    """ Removes empty list items when an empty StringField has been converted to LinesField """
    src_portal_type = 'DynaPage'
    src_meta_type = 'DynaPage'
    dst_portal_type = 'DynaPage' # Optional
    dst_meta_type = 'DynaPage' # Optional

    @staticmethod
    def migrateStringFieldToLinesField(val):
        if type(val) in [StringType, UnicodeType]:
            try:
                val = eval(val)
            except:
                # value couldn't be evaluated -> return it as a single value in a tuple
                return (val,)
        try:
            # return a tuple without any empty values
            return tuple([i for i in val if i or i in [0, False]])
        except:
            # value was not iterable -> return it as a single value in a tuple
            return (val,)

    fieldActions = (
        { 'fieldName'   : 'first_list_types',
          'newFieldName': 'first_list_types',
          'transform'   : lambda obj, val, **kw: JYUDynaPageMigrator.migrateStringFieldToLinesField(val) },
        { 'fieldName'   : 'first_list_state',
          'newFieldName': 'first_list_state',
          'transform'   : lambda obj, val, **kw: JYUDynaPageMigrator.migrateStringFieldToLinesField(val) },
        { 'fieldName'   : 'first_list_custom_view_fields',
          'newFieldName': 'first_list_custom_view_fields',
          'transform'   : lambda obj, val, **kw: JYUDynaPageMigrator.migrateStringFieldToLinesField(val) },
        { 'fieldName'   : 'first_list_keywords',
          'newFieldName': 'first_list_keywords',
          'transform'   : lambda obj, val, **kw: JYUDynaPageMigrator.migrateStringFieldToLinesField(val) },
        { 'fieldName'   : 'second_list_types',
          'newFieldName': 'second_list_types',
          'transform'   : lambda obj, val, **kw: JYUDynaPageMigrator.migrateStringFieldToLinesField(val) },
        { 'fieldName'   : 'second_list_state',
          'newFieldName': 'second_list_state',
          'transform'   : lambda obj, val, **kw: JYUDynaPageMigrator.migrateStringFieldToLinesField(val) },
        { 'fieldName'   : 'second_list_custom_view_fields',
          'newFieldName': 'second_list_custom_view_fields',
          'transform'   : lambda obj, val, **kw: JYUDynaPageMigrator.migrateStringFieldToLinesField(val) },
        { 'fieldName'   : 'second_list_keywords',
          'newFieldName': 'second_list_keywords',
          'transform'   : lambda obj, val, **kw: JYUDynaPageMigrator.migrateStringFieldToLinesField(val) },
        { 'fieldName'   : 'third_list_types',
          'newFieldName': 'third_list_types',
          'transform'   : lambda obj, val, **kw: JYUDynaPageMigrator.migrateStringFieldToLinesField(val) },
        { 'fieldName'   : 'third_list_state',
          'newFieldName': 'third_list_state',
          'transform'   : lambda obj, val, **kw: JYUDynaPageMigrator.migrateStringFieldToLinesField(val) },
        { 'fieldName'   : 'third_list_custom_view_fields',
          'newFieldName': 'third_list_custom_view_fields',
          'transform'   : lambda obj, val, **kw: JYUDynaPageMigrator.migrateStringFieldToLinesField(val) },
        { 'fieldName'   : 'third_list_keywords',
          'newFieldName': 'third_list_keywords',
          'transform'   : lambda obj, val, **kw: JYUDynaPageMigrator.migrateStringFieldToLinesField(val) },
        { 'fieldName'   : 'fourth_list_types',
          'newFieldName': 'fourth_list_types',
          'transform'   : lambda obj, val, **kw: JYUDynaPageMigrator.migrateStringFieldToLinesField(val) },
        { 'fieldName'   : 'fourth_list_state',
          'newFieldName': 'fourth_list_state',
          'transform'   : lambda obj, val, **kw: JYUDynaPageMigrator.migrateStringFieldToLinesField(val) },
        { 'fieldName'   : 'fourth_list_custom_view_fields',
          'newFieldName': 'fourth_list_custom_view_fields',
          'transform'   : lambda obj, val, **kw: JYUDynaPageMigrator.migrateStringFieldToLinesField(val) },
        { 'fieldName'   : 'fourth_list_keywords',
          'newFieldName': 'fourth_list_keywords',
          'transform'   : lambda obj, val, **kw: JYUDynaPageMigrator.migrateStringFieldToLinesField(val) },
        )

def migrate(self):
    """Run the migration"""

    out = StringIO()

    print >> out, "Starting migration"

    portal_url = getToolByName(self, 'portal_url')
    portal = portal_url.getPortalObject()

    walker = CatalogWalker(portal, JYUDynaPageMigrator)
    walker.go(out=out)

    print >> out, walker.getOutput()
    print >> out, "Migration removed empty list items from LinesFields"
    print >> out, "Migration finished"

    return out.getvalue()
