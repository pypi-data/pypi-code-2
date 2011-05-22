import zc.buildout
import subprocess
import shutil
import base64
import zlib
import sys
import os


def initialize_pip():
    import get_pip
    if sys.version_info >= (3,0):
        import pickle
        sources = get_pip.sources.encode("ascii") # ensure bytes
        sources = pickle.loads(zlib.decompress(base64.decodebytes(sources)))
    else:
        import cPickle as pickle
        sources = pickle.loads(zlib.decompress(base64.decodestring(get_pip.sources)))
    temp_dir = get_pip.unpack(sources)
    sys.path.insert(0, temp_dir)

    import pip, pip.req, pip.vcs

    pip.version_control()
    pip.logger.consumers.append((pip.logger.INFO, sys.stdout))
    schemes = pip.vcs.vcs.schemes[:]
    if 'svn' not in schemes:
        schemes.append('svn')

    shutil.rmtree(temp_dir)
    return pip.req, schemes

def asbool(buildout, name, default='true'):
    value = buildout['buildout'].get(name, default)
    value = value.lower()
    if value == 'false':
        return False
    return value

def has_setup(dirname):
    if os.path.isfile(os.path.join(dirname, 'setup.py')):
        return True
    return False

def popen(args, dirname=None):
    cwd = os.getcwd()
    if dirname:
        os.chdir(dirname)
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    print(p.stdout.read())
    os.chdir(cwd)

def install(buildout=None):

    pip_req, schemes = initialize_pip()

    offline = asbool(buildout, 'offline', 'false')
    newest = asbool(buildout, 'newest', 'false')
    update = asbool(buildout, 'vcsdevelop-update', 'false')
    if not update:
        update = asbool(buildout, 'vcs-update', 'false')
    else:
        print('Warning: vcsdevelop-update option has been renamed to vcs-update')

    develop_dir = buildout['buildout'].get('develop-dir', os.getcwd())
    if develop_dir.startswith('~'):
        develop_dir = os.path.expanduser(develop_dir)

    if not os.path.isdir(develop_dir):
        os.makedirs(develop_dir)

    develop = buildout['buildout'].get('develop', '')
    develop = [d.strip() for d in develop.split('\n') if d.strip()]

    vcs_extend = buildout['buildout'].get('vcs-extend-develop', '')
    vcs_extend = [d.strip() for d in vcs_extend.split('\n') if d.strip()]

    if vcs_extend:
        for url in vcs_extend:
            dummy, package = url.split('#egg=')
            if not [p for p in develop if p.endswith(package)]:
                develop.append(url)
            else:
                print(('Skipping %r. Package is already in the develop option' % url))

    new_develop = []
    for url in develop:
        if '+' in url and len([s for s in schemes if url.startswith(s+'+')]):
            if '#egg=' in url:
                dummy, package = url.split('#egg=')
            elif has_setup(url, 'setup.py'):
                new_develop.append(url)
                continue
            else:
                raise ValueError('Invalid url %s. You must add #egg=packagename' % url)
            source_dir = os.path.join(develop_dir, package.strip())
            if os.path.isdir(source_dir) and (not offline and update == 'always'):
                print(('Removing %s' % source_dir))
                shutil.rmtree(source_dir)
            if not os.path.isdir(source_dir) or update:
                if not offline:
                    req = pip_req.InstallRequirement.from_editable(url)
                    req.source_dir = source_dir
                    req.update_editable()
                    if os.path.isfile(os.path.join(source_dir, '.gitmodules')):
                        popen(['git', 'submodule', 'init'], dirname=source_dir)
                        popen(['git', 'submodule', 'update'], dirname=source_dir)
            if has_setup(source_dir):
                new_develop.append(source_dir)
            else:
                print(('Warning: %s is not a python package' % source_dir))
        else:
            new_develop.append(os.path.abspath(url))

    if len(new_develop):
        buildout['buildout']['develop'] = '\n'.join(new_develop)

