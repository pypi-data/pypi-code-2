#!/usr/bin/env python
import sys
import os
import shutil
import base64
import tempfile
from distutils import core
from traduisons import msg_VERSION, b64_images

README = os.path.join(os.path.dirname(__file__), 'README')
LICENSE = os.path.join(os.path.dirname(__file__), 'LICENSE')
CHANGELOG = os.path.join(os.path.dirname(__file__), 'CHANGELOG')
CHANGELOG_WIKI = os.path.join(os.path.dirname(__file__), os.pardir, 'wiki', 'ChangeLog.wiki')

if os.path.isfile(CHANGELOG_WIKI):
    shutil.copy2(CHANGELOG_WIKI, CHANGELOG)

Py2exeCommand = None
py2exe_args = {}
cmdclass_dict = {}
icon_file = None

if 'py2exe' in sys.argv:
    # For side effects!
    import py2exe
    from py2exe import build_exe

    class Py2exeCommand(build_exe.py2exe):
        def get_hidden_imports(self):
            d = build_exe.py2exe.get_hidden_imports(self)
            d.setdefault('gtk._gtk', []).extend([
                    'cairo', 'pango', 'pangocairo', 'atk'])
            return d
    cmdclass_dict['py2exe'] = Py2exeCommand # _After_ class definition
    icon = base64.b64decode(b64_images['ico']['traduisons_icon'])
    f = tempfile.NamedTemporaryFile(delete = False)
    f.write(icon)
    icon_file = f.name
    f.close()
    py2exe_args = {'windows':
                       [{"script": "bin/traduisons",
                         "icon_resources":
                             [(1, icon_file)],
                         }],
                   'options': {'py2exe': {'includes': ['gio']}},
        }

core.setup(
    name = "traduisons",
    description = "A front-end to Google Translate",
    long_description = open(README).read(),
    version = str(msg_VERSION),
    author = 'John Tyree',
    author_email = 'johntyree@gmail.com',
    url = 'http://traduisons.googlecode.com',
    license = open(LICENSE).read(),
    packages = ['traduisons'],
    package_data = { 'traduisons': ['data/traduisons_icon.png']},
    cmdclass = cmdclass_dict,
    scripts = ['bin/traduisons'],
    **py2exe_args
)

if icon_file is not None:
    os.unlink(icon_file)
