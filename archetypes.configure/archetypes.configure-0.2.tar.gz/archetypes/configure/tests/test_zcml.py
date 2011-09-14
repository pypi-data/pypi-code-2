from Products.Archetypes.tests.atsitetestcase import ATSiteTestCase


class ConfigurationTest(ATSiteTestCase):
    example = '''
    <configure
        xmlns="http://namespaces.zope.org/zope"
        xmlns:five="http://namespaces.zope.org/five"
        xmlns:at="http://namespaces.plone.org/archetypes"
        package="archetypes.configure.tests"
        i18n_domain="test">

      <include package="archetypes.configure" file="meta.zcml" />

      <five:registerPackage package="." />

      <permission id="dummy.Add" title="Add dummy" />

      <at:register
          class=".content.Dummy"
          permission="dummy.Add"
          />

    </configure>
    '''

    def afterSetUp(self):
        from Products.Archetypes.tests.test_classgen import gen_dummy
        gen_dummy()

    def test_example(self):
        from zope.configuration.xmlconfig import xmlconfig
        from StringIO import StringIO
        xmlconfig(StringIO(self.example))

        from OFS.Application import install_products
        from archetypes.configure import tests as module
        install_products(module)

        from Products import meta_types

        for fti in meta_types:
            if fti['name'] == 'archetypes.configure.tests: Dummy':
                break
        else:
            self.fail("Registration failed.")

        self.assertEqual(fti['product'], 'archetypes.configure.tests')
        self.assertEqual(fti['permission'], u'Add dummy')
