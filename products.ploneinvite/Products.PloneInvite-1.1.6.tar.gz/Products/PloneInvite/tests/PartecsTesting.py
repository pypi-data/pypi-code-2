import pdb
from Testing import ZopeTestCase 
from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.setup import setupPloneSite

from Acquisition import aq_base
from AccessControl.SecurityManagement import newSecurityManager


# Test user configuration
test_users = [
    dict(id='test_member',
         password='testmember',
         roles=['Member']),

    dict(id='test_authuser',
         password='testmember',
         roles=['Member', 'Authorised User']),

    dict(id='test_authuser2',
         password='testmember',
         roles=['Member', 'Authorised User']),

    dict(id='test_dda_administrator',
         password='testmember',
         roles=['DDA Administrator','Member']),

    dict(id='test_dda_member',
         password='testddamember',
         roles=['Member','DDA Member']),

    dict(id='test_dda_member1',
         password='testddamember',
         roles=['Member','DDA Member']),

    dict(id='test_dda_member2',
         password='testddamember',
         roles=['Member','DDA Member']), 

    dict(id='test_pkb_member1',
         password='testpkbmember',
         roles=['Member','PKB Member']),

    dict(id='test_pkb_member2',
         password='testpkbmember',
         roles=['Member','PKB Member']),    

    dict(id='test_manager',
         password='testmanager',
         roles=['Member', 'Manager']),

    dict(id='test_another_manager',
         password='testpassword',
         roles=['Member', 'Manager']),
    
    dict(id='partecs_messaging_user1',
         password='testpassword',
         roles=['Member']),

    dict(id='partecs_messaging_user2',
         password='testpassword',
         roles=['Member']),

    dict(id='partecs_messaging_user3',
         password='testpassword',
         roles=['Member']),
  
    ]

class PartecsTestCase(PloneTestCase):
    # To be fixed to test non-DDA Partecs products 
    """Contains facilities to test Partecs products.
    For instance, a simple 'add' method to add Partecs objects
    to folderish objects."""

    def afterSetUp(self):
        """
        Basic configuration for PartecsTestCase.
        """
        # Create some users. We already have "portal_owner" from PloneTestCase.

        uf = self.app.plone.acl_users
        for user in test_users:
            uf.userFolderAddUser(user['id'], user['password'], user['roles'], [])
        self.switchUser('test_member')

    def beforeTearDown(self):
        pass

    def switchUser(self, username):
        """
        Switches to the specified user. Raises unspecified error if the
        user does not exist. Error is likely to be KeyError (unverified).
        """
        uf = self.app.plone.acl_users
        user = uf.getUserById(username).__of__(uf)
        newSecurityManager(None, user)

    def add(self, typename, foldername, id = None):
        """Adds a new typename object to foldername and returns the
        newly created object. By default, uses 'aTypename' as id.
        Also works if typename is a folderish object."""
        folder = getattr(self, foldername)
        id = id or ("a" + typename)
        folder.invokeFactory(type_name=typename, id=id) 
        return getattr(folder, id)

    def _addProperty(self, obj, PROPERTY={}):
        PROPERTY = PROPERTY.copy()
        if hasattr(PROPERTY, 'id'): PROPERTY.pop('id')
        for field_name in PROPERTY.keys():
            fields = obj.Schema().fields()
            field = [field for field in fields if field.getName() == field_name]
            if not field: continue
            field = field[0]
            mutator_name = field.mutator
            mutator = getattr(obj, mutator_name)
            mutator(PROPERTY[field_name])

        self.plone.portal_catalog.reindexObject(obj)

    def _addObject(self, parent, type_name, id):
        parent.invokeFactory(type_name=type_name, id=id)
        return getattr(parent, id)

    def addObject(self, parent, obj_url, object_hirarchy):
        obj_path = obj_url.split('/')
        if len(obj_path) == 1:
            try:
                if not parent.unrestrictedTraverse(obj_path, None):
                    return self._addObject(parent, object_hirarchy[obj_url], obj_path[-1])
                else:
                    return parent.unrestrictedTraverse(obj_path, None)
            except KeyError:
                pass
        elif not parent.unrestrictedTraverse(obj_path, None):
            url = '/'.join(obj_path[:-1])
            return self._addObject(self.addObject(parent, url, object_hirarchy)
                                   , object_hirarchy[obj_url]
                                   , obj_path[-1]
                                   )
        else:
            return parent.unrestrictedTraverse(obj_path, None)
        
    def createObjectHirarchy(self, parent, object_hirarchy):
        for obj_url, type_name in object_hirarchy.iteritems():
            self.addObject(parent, obj_url, object_hirarchy)

    def uploadContent(self, parent, object_hirarchy, OBJECTS):
        """Upload content in parent object.

        object_hirarch and OBJECTS should be in the same format as that of
        {checkout_path}/code/partecs/support/ContentUploader/content.py file.
        """
        self.createObjectHirarchy(parent, object_hirarchy)
        for obj_url, PROPERTY in OBJECTS.iteritems():
            obj_path = obj_url.split('/')
            obj = parent.unrestrictedTraverse(obj_path, None)
            if obj:  self._addProperty(obj, PROPERTY)

# Make a partecs plone site.

setupPloneSite(id='plone', policy="Partecs Portal site")


# For Automated build Process
import sys
sys.stderr.write("TESTSTART\n")
