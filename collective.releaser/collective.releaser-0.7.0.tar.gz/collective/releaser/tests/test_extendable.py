import unittest
from collective.releaser.commands.extendable import ExtensibleCommand
from pkg_resources import Distribution as Dist
from setuptools.dist import Distribution

class ExtendableTest(unittest.TestCase):

    def setUp(self):
        Dist.old_metadata = Dist._get_metadata
        root = 'collective.releaser.tests.test_extendable:ExtendableTest'
        new_points = ['[distutils.MyCmd.manifest_makers]',
                      'svn = %s._svn' % root,
                      'template = %s._template' % root,
                      'hg = %s._hg' % root]

        def patched_metadata(self, name):
            metadata = self.old_metadata(name)
            for m in metadata:
                yield m
            if name == 'entry_points.txt':
                for m in new_points:
                    yield m
        Dist._get_metadata = patched_metadata

    def tearDown(self):
        Dist._get_metadata = Dist.old_metadata

    @staticmethod
    def _svn(cmd, name):
        cmd.files.append('svn')

    @staticmethod
    def _hg(cmd, name):
        cmd.files.append('hg')

    @staticmethod
    def _template(cmd, name):
        cmd.files.append('more')

    def test_extendable(self):
        #
        # this is a command using extensible options
        #
        class MyCmd(ExtensibleCommand):

            user_options = [('manifest-makers', None,
                             'Plugins to build the manifest file')]

            extensible_options = ['manifest_makers']

            def initialize_options(self):
                # this is a regular user option
                self.manifest_makers = ['svn', 'template', 'hg']
                self.files = []

            def finalize_options(self):
                pass

            def run(self):
                # this will build the filelist by running the plugins
                self.run_extension('manifest_makers')


        dist = Distribution()
        cmd = MyCmd(dist)
        cmd.ensure_finalized()
        cmd.run()

        # make sure the plugins have filled the files attribute
        self.assertEquals(cmd.files, ['svn', 'hg', 'more'])

def test_suite():
    """returns the test suite"""
    return unittest.makeSuite(ExtendableTest)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

