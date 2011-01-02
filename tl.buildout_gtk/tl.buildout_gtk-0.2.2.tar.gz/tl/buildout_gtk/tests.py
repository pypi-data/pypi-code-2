# Copyright (c) 2010 Thomas Lotze
# See also LICENSE.txt

from zc.buildout.testing import *
import StringIO
import hashlib
import os
import tarfile
import unittest

join = os.path.join


def setUp(test):
    test.globs = {}
    buildoutSetUp(test)
    install('zc.recipe.cmmi', test)
    install_develop('tl.buildout_gtk', test)
    tmpdir = test.globs['tmpdir']
    test.globs['cache'] = tmpdir('cache')
    distros = test.globs['distros'] = tmpdir('distros')

    tarpath = join(distros, 'null.tgz')
    tar = tarfile.open(tarpath, 'w:gz')
    configure = configure_template % sys.executable
    info = tarfile.TarInfo('configure')
    info.size = len(configure)
    info.mode = 0755
    tar.addfile(info, StringIO.StringIO(configure))
    tar.close()
    test.globs['md5_null'] = hashlib.md5(open(tarpath).read()).hexdigest()

    for name in ('pycairo', 'pygobject', 'pygtk', 'pywebkitgtk'):
        os.symlink(join(distros, 'null.tgz'), join(distros, name + '.tgz'))


configure_template = """#!%s
import sys
print "configuring foo", ' '.join(sys.argv[1:])

Makefile_template = '''
all:
\techo building foo

install:
\techo installing foo
'''

open('Makefile', 'w').write(Makefile_template)

"""


def looks_like_sha1sum(line):
    return len(line) == 40 and all(x in '0123456789abcdef' for x in line)


class TestPart(unittest.TestCase):

    def setUp(self):
        setUp(self)
        write('buildout.cfg', """\
[buildout]
parts = gtk
download-cache = %(cache)s

[gtk]
recipe = tl.buildout_gtk
pywebkitgtk = true
pycairo-url = file://%(distros)s/pycairo.tgz
pygobject-url = file://%(distros)s/pygtk.tgz
pygtk-url = file://%(distros)s/pygobject.tgz
pywebkitgtk-url = file://%(distros)s/pywebkitgtk.tgz
pycairo-md5sum = %(md5_null)s
pygobject-md5sum = %(md5_null)s
pygtk-md5sum = %(md5_null)s
pywebkitgtk-md5sum = %(md5_null)s
""" % self.globs)

    tearDown = buildoutTearDown

    def test_part_holds_symlinks_to_build_locations(self):
        system('bin/buildout')
        part = join('parts', 'gtk')

        # we have exactly 4 symlinks, one for each project
        self.assertEqual(['pycairo', 'pygobject', 'pygtk', 'pywebkitgtk'],
                         sorted(os.listdir(part)))

        # all symlinks are different
        self.assertEqual(4, len(set(os.readlink(join(part, name))
                                    for name in os.listdir(part))))

        # each symlink points to a place inside the cmmi cache that looks like
        # a state hash
        build = join(self.globs['cache'], 'cmmi', 'build')
        self.assertEquals(
            build, os.path.dirname(os.readlink(join(part, 'pycairo'))))
        self.assert_(looks_like_sha1sum(os.path.basename(
                    os.readlink(join(part, 'pycairo')))))
        self.assertEquals(
            build, os.path.dirname(os.readlink(join(part, 'pygobject'))))
        self.assert_(looks_like_sha1sum(os.path.basename(
                    os.readlink(join(part, 'pygobject')))))
        self.assertEquals(
            build, os.path.dirname(os.readlink(join(part, 'pygtk'))))
        self.assert_(looks_like_sha1sum(os.path.basename(
                    os.readlink(join(part, 'pygtk')))))
        self.assertEquals(
            build, os.path.dirname(os.readlink(join(part, 'pywebkitgtk'))))
        self.assert_(looks_like_sha1sum(os.path.basename(
                    os.readlink(join(part, 'pywebkitgtk')))))

        # each symlink target is an existing directory
        self.assert_(os.path.isdir(os.readlink(join(part, 'pycairo'))))
        self.assert_(os.path.isdir(os.readlink(join(part, 'pygobject'))))
        self.assert_(os.path.isdir(os.readlink(join(part, 'pygtk'))))
        self.assert_(os.path.isdir(os.readlink(join(part, 'pywebkitgtk'))))

    def test_part_isnt_created_if_any_project_cannot_be_built(self):
        remove(self.globs['distros'], 'pywebkitgtk.tgz')
        system('bin/buildout')
        self.assert_(not os.path.exists(join('parts', 'gtk')))

    def test_deleted_cached_build_is_rebuilt(self):
        build = join(self.globs['cache'], 'cmmi', 'build')
        system('bin/buildout')
        self.assertEqual(4, len(os.listdir(build)))
        shutil.rmtree(os.path.join(build, os.listdir(build)[0]))
        system('bin/buildout')
        self.assertEqual(4, len(os.listdir(build)))

    def test_shared_builds_are_never_deleted(self):
        # fixed in tl.buildout_gtk 0.2.2
        build = join(self.globs['cache'], 'cmmi', 'build')
        assert not os.path.exists(build)
        system('bin/buildout')
        self.assertEqual(4, len(os.listdir(build)))
        write('buildout.cfg', """\
[buildout]
parts = 
download-cache = %(cache)s
""" % self.globs)
        system('bin/buildout')
        self.assertEqual(4, len(os.listdir(build)))
