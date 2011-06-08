import sys
import os
import re

import pkg_resources
from argparse import ArgumentParser
from string import Template
import zipfile
if sys.version_info[0] < 3:
    from urllib2 import urlopen
    from StringIO import StringIO
    def prompt(name, default=None):
        if default is None:
            return raw_input("%s: " % name)
        else:
            value = raw_input("%s [%s]: " % (name, default))
            if not value:
                return default
            return value
else:
    from urllib.request import urlopen
    from io import BytesIO as StringIO
    def prompt(name, default=None):
        if default is None:
            return input("%s: " % name).strip()
        else:
            value = input("%s [%s]: " % (name, default)).strip()
            if not value:
                return default
            return value

ENTRY_POINT = "aodag.scaffold.scaffold"

user_home = os.path.expanduser('~')
default_scaffolds_directory = os.path.join(user_home, '.scaffolds')

tmpl_dir_pattern = re.compile(r"^\+(?P<name>\w+)\+$")
scaffold_name_pattern = re.compile(r"^[a-zA-Z]\w*(\.[a-zA-Z]\w*)*$")


def create_parser():
    parser = ArgumentParser()
    parser.add_argument('-d', '--scaffolds-drectory',
        dest="base_dir",
        default=default_scaffolds_directory)
    subparsers = parser.add_subparsers()
    list_parser = subparsers.add_parser('list')
    list_parser.set_defaults(func=cmd_list)
    create_parser = subparsers.add_parser('create')
    create_parser.add_argument('-d', '--dest', dest="dest",
        default=os.getcwd())
    create_parser.add_argument('scaffold')
    create_parser.set_defaults(func=cmd_create)
    install_parser = subparsers.add_parser('install')
    install_parser.add_argument('scaffold_file', help="scaffold zip archive file")
    install_parser.add_argument('scaffold', help="name of scaffold")
    install_parser.set_defaults(func=cmd_install)

    return parser

def prepare(args):
    """ """
    if not os.path.isdir(args.base_dir):
        os.mkdir(args.base_dir)

def cmd_list(args):
    """ list scaffold templates"""

    for s in os.listdir(args.base_dir):
        print(s)

class Namespace(dict):
    def __init__(self):
        self._inner = dict()

    def __getitem__(self, key):
        if key not in self._inner:
            value = prompt(str(key), os.environ.get(key))
            self._inner[key] = value
        else:
            value = self._inner[key]
        return value

    def __setitem__(self, key, value):
        self._inner[key] = value

    def iter(self):
        return self._inner.keys()

namespace = Namespace()

def fill_dirname(dirname, namespace=namespace):
    """
    >>> namespace = {'namespace': 'aodag', 'package': 'scaffold'}
    >>> fill_dirname('+namespace+/+package+', namespace)
    'aodag/scaffold'
    """

    segments = []
    for e in dirname.split(os.sep):

        m = tmpl_dir_pattern.match(e)
        if m is not None:
            name = m.groupdict()['name']
            segments.append(namespace[name])
        else:
            segments.append(e)

    return os.path.join(*segments)

def cmd_create(args):
    """ extend template """
    scaffold = args.scaffold
    dest = os.path.expanduser(args.dest)
    if not os.path.exists(dest):
        os.mkdir(dest)

    s_root = os.path.join(args.base_dir, scaffold)
    if not os.path.isdir(s_root):
        print("%s is not scaffold" % scaffold)
        sys.exit(1)

    for root, dirs, files in os.walk(s_root):
        for d in dirs:
            from_ = os.path.join(root, d)
            to_ = os.path.join(dest, fill_dirname(os.path.join(root, d)[len(s_root):].strip(os.sep)))
            print(from_, "->", to_)
            if os.path.exists(to_):
                print("%s already exists." % to_)
            else:
                os.mkdir(to_)

        for f in files:
            from_ = os.path.join(root, f)
            if f.endswith('_tmpl'):
                tmpl = Template(open(os.path.join(root, f)).read())
                dest_filename = f[:-1*len('_tmpl')]
                src = tmpl.substitute(namespace)
            else:
                dest_filename = f
                src = open(from_).read()

            to_ = os.path.join(dest, fill_dirname(os.path.join(root, dest_filename)[len(s_root):].strip(os.sep)))
            fd = open(to_, "w")
            fd.write(src)
            fd.close()
            print(from_, "->", to_)


def cmd_install(args):
    """ install scaffold """
    file = args.scaffold_file
    scaffold = args.scaffold
    if not scaffold_name_pattern.match(scaffold):
        print("invalid scaffold name")
        sys.exit(1)

    s_root = os.path.join(args.base_dir, scaffold)
    if not os.path.exists(s_root):
        os.mkdir(s_root)

    if any(file.startswith(prefix) for prefix in ["http://", "https://"]):
        _install_remote_scaffold(s_root, file)
    else:
        _install_local_scaffold(s_root, file)

def _install_remote_scaffold(s_root, url):
    print("remote: %s" % url)
    content = urlopen(url)
    file = StringIO(content.read())
    _install_local_scaffold(s_root, file)

def _install_local_scaffold(s_root, file):
    z = zipfile.ZipFile(file)
    for info in z.infolist():
        print(info.filename)
        if info.filename.endswith('/'):
            d = os.path.join(s_root, os.path.dirname(info.filename))
            if not os.path.exists(d):
                os.makedirs(d)
        else:
            z.extract(info, s_root)


def main():
    parser = create_parser()
    args = parser.parse_args()
    prepare(args)

    if hasattr(args, "func"):
        args.func(args)
