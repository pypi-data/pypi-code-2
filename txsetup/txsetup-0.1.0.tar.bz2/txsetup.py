"""
Copyright (c) 2005 Divmod Inc.

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Source: http://divmod.org/trac/browser/trunk/Epsilon/epsilon/setuphelper.py
Notice: With minor motifications by Silas Sewell (silas@sewell.ch).
"""

# For great justice, take off every zig.
import sys, os, pprint, traceback

from distutils.core import setup as core_setup

def pluginModules(moduleNames):
    from twisted.python.reflect import namedAny
    for moduleName in moduleNames:
        try:
            yield namedAny(moduleName)
        except ImportError:
            pass
        except ValueError, ve:
            if ve.args[0] != 'Empty module name':
                traceback.print_exc()
        except:
            traceback.print_exc()

def _regeneratePluginCache(pluginPackages):
    print 'Regenerating cache with path: ',
    pprint.pprint(sys.path)
    from twisted import plugin
    for pluginModule in pluginModules([
        p + ".plugins" for p in pluginPackages]):
        # Not just *some* zigs, mind you - *every* zig:
        print 'Full plugin list for %r: ' % (pluginModule.__name__)
        pprint.pprint(list(plugin.getPlugins(plugin.IPlugin, pluginModule)))

def regeneratePluginCache(dist, pluginPackages):
    if 'install' in dist.commands:
        sys.path.insert(0, os.path.abspath(dist.command_obj['install'].install_lib))
        _regeneratePluginCache(pluginPackages)

def setup(**kw):
    packages = []
    datafiles = {}
    pluginPackages = []

    for (dirpath, dirnames, filenames) in os.walk(os.curdir):
        dirnames[:] = [p for p in dirnames if not p.startswith('.')]
        pkgName = dirpath[2:].replace('/', '.')
        if '__init__.py' in filenames:
            # The current directory is a Python package
            packages.append(pkgName)
        elif 'plugins' in dirnames:
            # The current directory is for the Twisted plugin system
            pluginPackages.append(pkgName)
            packages.append(pkgName)

    for package in packages:
        if '.' in package:
            continue
        D = datafiles[package] = []
        print 'Files in package %r:' % (package,)
        pprint.pprint(os.listdir(package))
        for (dirpath, dirnames, filenames) in os.walk(package):
            dirnames[:] = [p for p in dirnames if not p.startswith('.')]
            for filename in filenames:
                if filename == 'dropin.cache':
                    continue
                if (os.path.splitext(filename)[1] not in ('.py', '.pyc', '.pyo')
                    or '__init__.py' not in filenames):
                    D.append(os.path.join(dirpath[len(package)+1:], filename))
    autoresult = {
        'packages': packages,
        'package_data': datafiles,
        }
    print 'Automatically determined setup() args:'
    pprint.pprint(autoresult, indent=4)
    assert 'packages' not in kw
    assert 'package_data' not in kw
    kw.update(autoresult)
    distobj = core_setup(**kw)
    regeneratePluginCache(distobj, pluginPackages)
    return distobj
