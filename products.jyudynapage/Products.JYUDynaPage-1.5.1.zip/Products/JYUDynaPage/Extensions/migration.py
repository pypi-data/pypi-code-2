from Products.CMFCore.utils import getToolByName
from StringIO import StringIO

try:
    from Products.ATContentTypes.migration.walker import CatalogWalker
    from Products.ATContentTypes.migration.migrator import CMFItemMigrator
except:
    from Products.contentmigration.basemigrator.walker import CatalogWalker
    from Products.contentmigration.basemigrator.migrator import CMFItemMigrator
    
#class DynaPageMigrator(CMFItemMigrator):
#    """Base class to migrate to DynaPage or a derivative.
#    """

class DynamicPageMigrator(CMFItemMigrator):
    walkerClass = CatalogWalker
    src_meta_type = 'Dynamic Page'
    src_portal_type = 'DynamicPage'
    dst_meta_type = 'DynaPage'
    dst_portal_type = 'DynaPage'
    map = {
        'title'              : 'setTitle',
        'text'               : 'setText',
        'first_list_title'   : 'first_list_title',
        'first_list_enabled' : 'first_list_active',
        #'first_list_type'    : 'first_list_types',
        'first_list_n_items' : 'first_list_items',
        'first_list_sort_order' : 'first_list_order',
        'first_list_subjects' : 'first_list_keywords',
        'second_list_title'   : 'second_list_title',
        'second_list_enabled' : 'second_list_active',
        #'second_list_type'    : 'second_list_types',
        'second_list_n_items' : 'second_list_items',
        'second_list_sort_order' : 'second_list_order',
        'second_list_subjects' : 'second_list_keywords',
        'third_list_title'   : 'third_list_title',
        'third_list_enabled' : 'third_list_active',
        #'third_list_type'    : 'third_list_types',
        'third_list_n_items' : 'third_list_items',
        'third_list_sort_order' : 'third_list_order',
        'third_list_subjects' : 'third_list_keywords',
        'fourth_list_title'   : 'fourth_list_title',
        'fourth_list_enabled' : 'fourth_list_active',
        #'fourth_list_type'    : 'fourth_list_types',
        'fourth_list_n_items' : 'fourth_list_items',
        'fourth_list_sort_order' : 'fourth_list_order',
        'fourth_list_subjects' : 'fourth_list_keywords',
    }

    def findAvailableList(self):
        """ Finds available list which is not active """
        if self.old.first_list_enabled:
            return 'first_list'
        elif self.old.second_list_enabled:
            return 'second_list'
        elif self.old.third_list_enabled:
            return 'thrid_list'
        elif self.old.fourth_list_enabled:
            return 'fourth_list'
        else:
            return False


    def migrate_localRoles(self):
        
        local_roles = {}
        valid_roles = [i for i in self.old.validRoles()]
        for role in valid_roles:
            users = self.old.users_with_local_role(role)
            if users:
                local_roles[role] = users
        
        roles = local_roles
        
        try:
            for role in roles.keys():
                users = roles[role]
                if users:
                    for user in users:
                        self.new.manage_setLocalRoles(user, [role])
        except Exception, e:
            print "Error while setting local roles up: %s. Passing still..." % e
            pass
    
    def last_migrate_creator(self):
        self.new.setCreators(self.old.Creator())
    
    def migrate_filters(self):
        """ migrates filters to new content type """
        
        first_list_filters = [type.split(':')[1] for type in self.old.first_list_filter]
        second_list_filters = [type.split(':')[1] for type in self.old.second_list_filter]
        third_list_filters = [type.split(':')[1] for type in self.old.third_list_filter]
        fourth_list_filters = [type.split(':')[1] for type in self.old.fourth_list_filter]
        
        print self.old.Title()
        print first_list_filters
        print second_list_filters
        print third_list_filters
        print fourth_list_filters
        print "\n"
        
        if first_list_filters:
            self.new.first_list_types = tuple(first_list_filters)
        if second_list_filters:
            self.new.second_list_types = tuple(second_list_filters)
        if third_list_filters:
            self.new.third_list_types = tuple(third_list_filters)
        if fourth_list_filters:
            self.new.fourth_list_types = tuple(fourth_list_filters)

    def migrate_etusivu_image(self):
        """ Migrates etusivu.jpg images from parent to inside the object """

        pc = getToolByName(self.old, 'portal_catalog')
        parent = self.old.aq_parent
        parentContents = pc.searchResults(portal_type="DynamicPage", path = {'query' : '/'.join(parent.getPhysicalPath()), 'depth' : 1})

        if len(parentContents) > 1:
            if 'etusivu.jpg' in parent.objectIds():
                print "Found etusivu.jpg from %s" % parent.absolute_url()
                self.new.manage_pasteObjects(parent.manage_copyObjects(['etusivu.jpg']))
                obj = self.new['etusivu.jpg']
                obj.reindexObject()

        else:
            if 'etusivu.jpg' in parent.objectIds():
                print "Found etusivu.jpg from %s" % parent.absolute_url()
                self.new.manage_pasteObjects(parent.manage_cutObjects(['etusivu.jpg']))
                obj = self.new['etusivu.jpg']
                obj.reindexObject()

    def beforeChange_migrate_fifth_list(self):
        """ Adds fifth list mapping to available nonactive list number """

        if not self.old.fifth_list_enabled:
            pass
        else:
            available_list = self.findAvailableList()

            mapping = {
                'fifth_list_title'   : '%s_title' % available_list,
                'fifth_list_enabled' : '%s_active' % available_list,
                'fifth_list_n_items' : '%s_items' % available_list,
                'fifth_list_sort_order' : '%s_order' % available_list,
                'fifth_list_subjects' : '%s_keywords' % available_list,
            }

            self.map.update(mapping)



# Change owner
# context.changeOwnership(context.portal_membership.getMemberById('jutaojan'))

def migrate(self):
    """Run the migration"""

    out = StringIO()
    print >> out, "Starting migration"

    portal_url = getToolByName(self, 'portal_url')
    portal = portal_url.getPortalObject()

    migrators = (DynamicPageMigrator,)

    for migrator in migrators:
        walker = migrator.walkerClass(portal, migrator)
        walker.go(out=out)
        print >> out, walker.getOutput()

    print >> out, "Migration finished"
    return out.getvalue()
