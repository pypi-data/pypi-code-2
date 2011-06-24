"""Provide useful base classes for testing in Plone."""
# Little hack to avoid this module be recognized as a test module.
__path__ = tuple()

import os.path
from tempfile import gettempdir

from Testing.ZopeTestCase.ZopeTestCase import user_name as DEFAULT_USER_NAME

from Products.PloneTestCase import PloneTestCase as ptc 
from Products.PloneTestCase.setup import portal_owner, default_password
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.Five.testbrowser import Browser

from prdg.util.testing import UtilTestCaseMixin
from prdg.zope.permissions import get_permission_info
from prdg.plone.util.utils import (get_workflow_state, get_workflow_info, 
    sanity_check_workflow)

class IntegrationTestCase(ptc.PloneTestCase):
    """Base class for integration unit tests."""    
    default_user_name = DEFAULT_USER_NAME
    default_password = default_password

    def afterSetUp(self):
        self.portal_url = self.portal.absolute_url()
        self.folder_url = self.folder.absolute_url()
        self.acl_users = self.portal.acl_users
        self.workflow = self.portal.acl_users.portal_workflow
        self.error_log = self.portal.error_log        
        self.css = self.portal.portal_css        
        self.skins = self.portal.portal_skins
        self.types = self.portal.portal_types
        self.factory = self.portal.portal_factory
        self.workflow = self.portal.portal_workflow
        self.properties = self.portal.portal_properties
        self.mail_host = self.portal.MailHost
        self.qi = self.portal.portal_quickinstaller
        self.putils = self.portal.plone_utils
        self.registration = self.portal.portal_registration   
        self.membership = self.portal.portal_membership
        
        # This tool is not present on Plone 4
        self.kupu = getattr(self.portal, 'kupu_library_tool', None)
            
    def login_as_default_user(self):
        self.login(self.default_user_name)
    
    def fail_if_errors_in_error_log(self):
        entries = self.error_log.getLogEntries()
        if not entries:
            return
        
        entries_str = [
            '%s: %s' % (e['type'], e['value'][:70])
            for e in entries
        ]
         
        msg = 'Error log entries:\n' + '\n'.join(entries_str)        
        self.fail(msg)
        
    def add_user(self, userid, roles=['Member'], password=default_password):
        """Add an user to the portal."""
        self.acl_users.userFolderAddUser(userid, password, roles, [])        
        
class FunctionalTestCase(ptc.FunctionalTestCase):
    """
    You can subclass this class or mix with another base class to add
    functional test support. Make sure afterSetUp() is called in your base
    class.
    """
    
    def afterSetUp(self):
        self.browser = Browser()
    
    def login_browser(self, name=portal_owner, password=default_password):
        """Login an user in self.browser."""
        self.browser.open(self.portal_url + '/login_form')
        self.browser.getControl(name='__ac_name').value = name
        self.browser.getControl(name='__ac_password').value = password
        self.browser.getControl(name='submit').click()
            
    def add_user(self, userid, roles=['Member'], password=default_password):
        """Add an user to the portal."""
        self.acl_users.userFolderAddUser(userid, password, roles, [])
        
    def test_login(self):
        """
        Login in the site to see if the front page is rendered without 
        errors.
        """
        self.login_browser()
        self.failUnless('Plone' in self.browser.contents)        
        self.fail_if_errors_in_error_log()    
    
    def publish_object(self, obj):
        """Publish the given object using ptc.FunctionalTestCase.publish()."""
        return self.publish(obj.virtual_url_path())
        
    def dump_browser_contents(self, filename='a.html'):
        """
        Create a file inside the default temp directory with the contents
        of the current page.
        """
        path = os.path.join(gettempdir(), filename)
        f = open(path, 'w')
        f.write(self.browser.contents)
        f.close()           
           
    def fill_form(self, data):
        """
        Given a dict mapping from input control names to values fill a form.
        List-like controls accept sequences as values.
        """
        for (name, value) in data.iteritems():            
            control = self.browser.getControl(name=name)
            if name.endswith('_options'):
                for v in value:
                    sub_control = control.getControl(value=v)
                    sub_control.selected = True
            else:                            
                control.value = value        
        
class InstallationTestCase(IntegrationTestCase, UtilTestCaseMixin):
    """
    Ensure a product or package is properly installed. Subclass it and provide 
    the required attributes (the first declarations) to test your product.
    
    Based on testSetup.py from RichDocument.
    """
    
    meta_types = set()
    """
    Set containing the meta types names of the types provided by the product.
    """
    
    skin_layers = set()
    """Set containing the names of the skin layers provided by the product."""
    
    default_skin_name = None
    """Name of the default skin set by the product, if any."""
    
    portal_properties = []
    """
    Test properties in the portal_properties tool.
    
    Sequence containing (sheet_id, property_id, value) tuples. For each
    tuple will be checked if the property value matches the given value. 
    See: lines_portal_properties, to test "lines" properties.
    """     
    
    lines_portal_properties = []
    """
    Same as portal_properties but to test properties of the type "lines".
    
    The tuple has one more element: (sheet_id, property_id, values, exact).
    values must be a set. exact is a boolean. If it is true then the values
    in the sheet must be the same as in values. Otherwise the values must be
    in the sheet, but it can have additional values.
    """
    
    plone_site_properties = []
    """
    Test properties in the root of the site (Plone Site) object.        
    
    Sequence containing (property_id, value) tuples.
    
    Interesting properties:
    title, validate_email, default_page.
    """
        
    default_workflow_chain = None
    """
    The default workflow chanin set by the product as a tuple of IDs if any.
    """
    
    workflows = set()
    """Set of workflow IDs to be checked for existence at portal_workflow.""" 
    
    mail_settings = {}
    """
    Dict containing mail settings to test. Keys can be: smtp_host, 
    smtp_port, smtp_uid, smtp_pwd. Only the present keys will be tested.
    """
    
    permissions = []
    """
    Sequence of (permission, roles, acquire) tuples. Types must be 
    (str, set, bool).
    """
    
    style_sheets = set()
    """Set containing the IDs of the stylesheets provided by the product."""
    
    dependency_products = set()
    """
    Set containing the names of the products that this packeg depends on.
    It will be checked if these products are installed.
    """
    
    tools = set()
    """Set containing IDs of tools."""
    
    def getSelectedSkinLayers(self):
        """
        Return: a sequence of skin layer names corresponding to the default
        skin selection.
        """
        return [
            l.strip() 
            for l 
            in self.skins.getSkinPath(self.skins.getDefaultSkin()).split(',')
        ]
        
    def testTypesInstalled(self):
        meta_types = set(self.types.objectIds())
        self.failUnless(self.meta_types.issubset(meta_types))

    def testPortalFactorySetup(self):
        factory_types = set(self.factory.getFactoryTypes())
        self.failUnless(
            self.meta_types.issubset(factory_types),
            'Types registered on portal_factory: %s.\n'
                'Types that should be registered: %s' 
                % (factory_types, self.meta_types)
        )
        
        # Make sure the product did not erase the factory types set by default.
        self.failUnless('Link' in factory_types)

    def testLinesPortalProperties(self):
        properties = self.lines_portal_properties
        for (sheet_id, property_id, values, exact) in properties:
            sheet = getattr(self.properties, sheet_id)
            actual_values = set(sheet.getProperty(property_id))
            
            if exact:
                self.assertEqual(values, actual_values)
            else:
                self.failUnless(values.issubset(actual_values))
    
    def testPortalProperties(self):
        for (sheet_id, property_id, value) in self.portal_properties:
            sheet = getattr(self.properties, sheet_id)
            actual_value = sheet.getProperty(property_id)
            self.assertEqual(value, actual_value)            
    
    def testPloneSiteProperties(self):
        for (property_id, value) in self.plone_site_properties:
            self.assertEqual(self.portal.getProperty(property_id), value)
    
    def testSkinLayersInstalled(self):
        # Check if the skin layers are present on portal_skins (i.e, if they're
        # in the "content" tab.
        skin_layers = set(self.skins.objectIds())        
        self.failUnless(
            self.skin_layers.issubset(skin_layers),
            'Skin layers are not installed: %s' % self.skin_layers 
        )
        
        # Check if the layers are present on the default skin selection.
        selected_skin_layers = self.getSelectedSkinLayers()
        self.failUnless(
            self.skin_layers.issubset(set(selected_skin_layers)),
            'Skin layers are not present in the default skin selection: %s' 
                % self.skin_layers
        )
        
        # Check if the layers are on top of the Plone default layers. Normally
        # it's what you want.
        index = selected_skin_layers.index('plone_templates')
        layers_above_plone = set(selected_skin_layers[:index])
        self.failUnless(
            self.skin_layers.issubset(layers_above_plone),
            'Skin layers are bellow the Plone layers in the default '\
                'selection: %s' % self.skin_layers  
        )    
    
    def testCustomLayerIsFirst(self):
        """
        This is a sanity check. Override it if you don't want the custom
        skin layer to be the first.
        """
        self.assertEqual(
            self.getSelectedSkinLayers()[0], 'custom', 
            'the "custom" skin layer is not the first.'
        )
    
    def testDefaultSkin(self):
        if self.default_skin_name:
            self.assertEqual(
                self.skins.getDefaultSkin(), self.default_skin_name,
                'Default skin is not set correctly.'
            )
    
    def testDefaultWorkflow(self):
        if self.default_workflow_chain != None:
            self.assertEqual(
                self.workflow.getDefaultChain(), self.default_workflow_chain,
                'Default workflow chain is wrong.'
            )
    
    def testWorkflows(self):
        existent_workflows = set(self.workflow.objectIds())
        self.failUnless(self.workflows.issubset(existent_workflows))
    
    def testMailSettings(self):
        self.assertAttributes(self.mail_host, self.mail_settings)
    
    def testPermissions(self):
        for (permission, roles, acquire) in self.permissions:
            (actual_roles, actual_acquire) = \
                get_permission_info(self.portal, permission)            
            self.failUnlessEqual(roles, set(actual_roles))
            self.failUnlessEqual(acquire, actual_acquire) 
                
    def testStyleSheets(self):
        actual_style_sheets = set(self.css.getResourceIds())
        self.failUnless(self.style_sheets.issubset(actual_style_sheets))
    
    def testProductsInstalled(self):        
        for p in self.dependency_products:
            self.failUnless(
                self.qi.isProductInstalled(p), 
                '%s is not installed.' % p
            )
    
    def testToolsInstalled(self):
        for t in self.tools:
            self.failUnless(
                getattr(self.portal, t, None), 
                'Tool %s not installed.' % t
            )
        
class ContentTypeTestCase(IntegrationTestCase):
    
    portal_type = None
    """Portal type to test."""
    
    sample_id_template = 'sample_id_%s' 
    """
    A template for the sample ID. The template will be formatted with the
    type name.
    """
    
    sample_field_values = {}
    """
    A dict mapping from field names to values. These will be used when
    creating sample objects.
    """
    
    @property
    def sample_id(self):
        return self.sample_id_template % self.portal_type    
    
    def create_object(self, container=None, id=None, field_values=None):
        """
        Create an object of the tested type.
        
        Arguments:
        id -- Object ID. If not given then self.sample_id_template is used.
        field_values -- A dict mapping from field names to values. If not given
            then self.sample_field_values will be used.
        container -- Folder where to create the object. If not given 
            self.folder is used.
        
        Return:
        The created object.
        """
        if id == None:
            id = self.sample_id
        
        if field_values == None:
            field_values = self.sample_field_values
        
        if container == None:
            container = self.folder
        
        container.invokeFactory(
            type_name=self.portal_type, 
            id=id, 
            **field_values
        )
        
        return getattr(container, id)
    
    def test_create(self):
        """Test object creation."""
        self.login_as_default_user()
        obj = self.create_object()
        self.assertEqual(obj.getId(), self.sample_id)

class WorkflowTestCase(IntegrationTestCase):
    # TODO: document this !
    
    # Overridable attributes.
    
    workflow_id = None
    
    users = {}
    """Maps from role names to user IDs"""
    
    initial_state = None
    
    object_creator_role = None
    """Role of the user to create sample objects. Eg.: 'Contributor'."""
    
    object_portal_type = 'Document'
    """
    The type of the sample objects to be created. The worfflow of the type
    is adjusted in the test set up.
    """
    
    ignored_messages_set = set()
    
    # The following attributes the subclass does not need to provide. 
    
    _obj = None
    
        
    def afterSetUp(self):
        IntegrationTestCase.afterSetUp(self)
        
        self.workflow.setChainForPortalTypes(
            [self.object_portal_type], 
            self.workflow_id
        )
                
        self._create_users()
        
        self.login(self.users[self.object_creator_role])        
        self._obj = self._create_sample_obj('99')
        
    def _create_users(self):
        default_roles = ['Member']
        for (role, userid) in self.users.iteritems():
            self.add_user(userid, default_roles + [role], self.default_password)
    
    def _create_sample_obj(self, id_suffix=''):        
        obj_id = 'anobj' + id_suffix
        self.folder.invokeFactory(
            type_name=self.object_portal_type, 
            id=obj_id,        
        )

        return self.folder[obj_id]

    def _exercise_workflow(self, obj, expected_current_state, path, users):
        
        def check_state(expected):
            actual = get_workflow_state(obj)
            self.failUnlessEqual(
                actual, 
                expected,
                'Current state is %s, expected %s' % (actual, expected)
            )                               
        
        check_state(expected_current_state)
        
        for (transition, dest_state, role) in path: 
            user_id = users[role]
            self.login(user_id)
            self.workflow.doActionFor(obj, transition)
            check_state(dest_state)
    
    def _test_workflow_path(self, path):
        try:
            self._exercise_workflow(
                self._obj, 
                self.initial_state, 
                path, 
                self.users
            )
        except WorkflowException, e:
            self.fail((str(e), get_workflow_info(self._obj)))
    
    def test_sanity_check(self):
        messages = set(sanity_check_workflow(self.workflow[self.workflow_id]))
        messages -= self.ignored_messages_set
        self.failIf(messages, '\n'.join(messages))
        
