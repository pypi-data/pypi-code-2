import os
import shutil
import tempfile
import urllib2
import json

from fanstatic import Library, Resource, generate_code

YUI_VERSION = '2.8.2'
# argh, download file version isn't actual version
YUI_DOWNLOAD_VERSION = '2.8.2r1'

URL_TEMPLATE = 'http://yuilibrary.com/downloads/yui2/yui_%s.zip'

YUILOADER_URL_TEMPLATE = ('http://yui.yahooapis.com/%s/build/yuiloader'
                         '/yuiloader.js')

def deminize(path):
    rest, ext = os.path.splitext(path)
    if rest.endswith('-min'):
        rest = rest[:-len('-min')]
    return rest + ext

def normalize_name(n):
    return str(n.replace('-', '_'))


def register_modes(inclusion):
    # Try to find the -min and -debug variants.
    # If they are not available and the inclusion defines a supersede
    # situation, register the inclusion for these modes.

    rest, ext = os.path.splitext(inclusion.relpath)
    # minified
    new_name = rest + '-min' + ext
    if os.path.exists(os.path.join(inclusion.library.path, new_name)):
        print inclusion.library, new_name
        inclusion.modes['minified'] = Resource(inclusion.library, new_name)

    # debug
    new_name = rest + '-debug' + ext
    if os.path.exists(os.path.join(inclusion.library.path, new_name)):
        print inclusion.library, new_name
        inclusion.modes['debug'] = Resource(inclusion.library, new_name)


def convert_to_inclusions(d):
    yui = Library('yui', 'resources')
    inclusion_map = {}
    for name, value in d.items():
        name = normalize_name(name)
        inclusion_map[name] = Resource(yui, deminize(value['path']))

    # fix up dependency structure
    for name, value in d.items():
        name = normalize_name(name)
        inclusion = inclusion_map[name]

        for require in value.get('requires', []):
            require = normalize_name(require)
            inclusion.depends.add(inclusion_map[require])

        for supersede_name in value.get('supersedes', []):
            orig_supersede_name = supersede_name
            supersede_name = normalize_name(supersede_name)
            r = inclusion_map[supersede_name]
            # only supersede things that don't supersede themselves
            if not d[orig_supersede_name].get('supersedes'):
                inclusion.supersedes.append(r)

        register_modes(inclusion)

    # add the SAM skin
    sam = Resource(yui, 'assets/skins/sam/skin.css')
    inclusion_map['sam'] = sam
    # base depends on reset.
    inclusion_map['base'].depends.add(inclusion_map['reset'])

    # now generate code
    return generate_code(**inclusion_map)

def load_json(version):
    f = urllib2.urlopen(YUILOADER_URL_TEMPLATE % version)
    data = f.read()
    f.close()
    s = "'moduleInfo': "
    i = data.find(s)
    i = i + len(s)
    j = data.find("'yuitest': {", i)
    j = data.find('}', j)
    j = data.find('}', j + 1)
    text = data[i:j + 1]
    open('/tmp/yui.json', 'w').write(normalize_json(text))
    return json.loads(normalize_json(text))

def normalize_json(text):
    # proper json has double quoted strings
    text = text.replace("'", '"')
    # hacks.
    text = text.replace('supersedes:', '"supersedes":')
    text = text.replace('datemath:', '"datemath":')
    text = text.replace('datemeth', 'datemath')
    result = []
    for line in text.splitlines():
        if '//' in line:
            continue
        result.append(line)
    return '\n'.join(result)

def depend(version):
    d = load_json(version)
    return convert_to_inclusions(d)

def download(version, callback):
    """Download a yui of version.

    When downloaded, call callback with path to directory
    with an extracted YUI. The callback will then be able to copy
    this to the appropriate location.
    """
    download_url = URL_TEMPLATE % version

    f = urllib2.urlopen(download_url)
    file_data = f.read()
    f.close()

    dirpath = tempfile.mkdtemp()
    try:
        yui_path = os.path.join(dirpath, 'yui.zip')
        ex_path = os.path.join(dirpath, 'yui_ex')
        g = open(yui_path, 'wb')
        g.write(file_data)
        g.close()
        os.system('unzip -qq "%s" -d "%s"' % (yui_path, ex_path))
        callback(ex_path)
    finally:
        shutil.rmtree(dirpath, ignore_errors=True)

def prepare(package_dir):
    yui_dest_path = os.path.join(package_dir, 'resources')

    # remove previous yui library
    shutil.rmtree(yui_dest_path, ignore_errors=True)

    def copy_yui(ex_path):
        """Copy YUI to location 'resources' in package."""
        yui_build_path = os.path.join(ex_path, 'yui', 'build')
        shutil.copytree(yui_build_path, yui_dest_path)

    download(YUI_DOWNLOAD_VERSION, copy_yui)

    # get dependency structure and create 'yui.py' into package
    code = depend(YUI_VERSION)
    yui_py_path = os.path.join(package_dir, '__init__.py')
    f = open(yui_py_path, 'w')
    f.write(code)
    f.close()

def main():
    # download YUI library into package
    package_dir = os.path.dirname(__file__)
    prepare(package_dir)
