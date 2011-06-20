#mgmgmgmgmgmg tranchitella.recipe.i18n
# Copyright (C) 2008-2010 Tranchitella Kft. <http://tranchtella.eu>

import fnmatch
import optparse
import os
import pkg_resources
import string
import sys
import time
import tokenize

from chameleon.core.etree import parse
from chameleon.core.utils import escape, htmlescape
from chameleon.zpt.interfaces import IExpressionTranslator
from chameleon.zpt.language import Parser

from pygettext import safe_eval, normalize, make_escapes

try:
    from quipu.publisher.configuration import hook_registry, unhook_registry
    from quipu.publisher.registry import Registry
    from quipu.publisher.threadlocal import manager
except ImportError:
    manager = None

from zope.component import getSiteManager
from zope.i18nmessageid import Message


POT_HEADER = """msgid ""
msgstr ""
"Project-Id-Version: %(version)s\\n"
"POT-Creation-Date: %(time)s\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: LANGUAGE TEAM <EMAIL@ADDRESS>\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=%(charset)s\\n"
"Content-Transfer-Encoding: %(encoding)s\\n"
"Generated-By: trannchitella.recipe.i18n\\n"
"""

class POTMaker(object):
    """This class inserts sets of strings into a POT file."""

    def __init__ (self, output_fn, path):
        self._output_filename = output_fn
        self.path = path
        self.catalog = {}

    def add(self, strings, base_dir=None):
        for msgid, locations in strings.items():
            if msgid == '':
                continue
            if msgid not in self.catalog:
                self.catalog[msgid] = POTEntry(msgid)

            for filename, lineno in locations:
                if base_dir is not None:
                    filename = filename.replace(base_dir, '')
                self.catalog[msgid].addLocationComment(filename, lineno)

    def write(self):
        file = open(self._output_filename, 'w')
        file.write(POT_HEADER % {'time': time.ctime(), 'version': '0',
            'charset': 'UTF-8', 'encoding': '8bit'})
        # sort the catalog entries by filename
        catalog = self.catalog.values()
        catalog.sort()
        # write each entry to the file
        for entry in catalog:
            entry.write(file)
        file.close()


class POTEntry(object):
    """This class represents a single message entry in the POT file."""

    def __init__(self, msgid, comments=None):
        self.msgid = msgid
        self.comments = comments or ''
        self.position = None

    def addComment(self, comment):
        self.comments += comment + '\n'

    def addLocationComment(self, filename, line):
        if self.position is None:
            self.position = (filename.split('/'), line)
        self.comments += '#: %s:%s\n' % (
            filename.replace(os.sep, '/'), line)

    def write(self, file):
        file.write('\n')
        if self.comments:
            file.write(self.comments)
        if (isinstance(self.msgid, Message) and
            self.msgid.default is not None):
            default = self.msgid.default.strip().encode('utf-8')
            lines = normalize(default).split("\n")
            if lines[0] != '""':
                lines[0] = "#. Default: %s\n" % lines[0]
                for i in range(1, len(lines)):
                    lines[i] = "#.  %s\n" % lines[i]
                file.write("".join(lines))
        file.write('msgid %s\n' % normalize(self.msgid.encode('utf-8')))
        file.write('msgstr ""\n')

    def __cmp__(self, other):
        return cmp(self.position, other.position)


class TokenEater(object):
    """This is almost 100% taken from `pygettext.py`, except that I removed all
    option handling and output a dictionary."""

    def __init__(self):
        self.__messages = {}
        self.__state = self.__waiting
        self.__data = []
        self.__lineno = -1
        self.__freshmodule = 1
        self.__curfile = None

    def __call__(self, ttype, tstring, stup, etup, line):
        self.__state(ttype, tstring, stup[0])

    def __waiting(self, ttype, tstring, lineno):
        if ttype == tokenize.NAME and tstring in ['_']:
            self.__state = self.__keywordseen

    def __suiteseen(self, ttype, tstring, lineno):
        # ignore anything until we see the colon
        if ttype == tokenize.OP and tstring == ':':
            self.__state = self.__suitedocstring

    def __suitedocstring(self, ttype, tstring, lineno):
        # ignore any intervening noise
        if ttype == tokenize.STRING:
            self.__addentry(safe_eval(tstring), lineno, isdocstring=1)
            self.__state = self.__waiting
        elif ttype not in (tokenize.NEWLINE, tokenize.INDENT,
            tokenize.COMMENT):
            # there was no class docstring
            self.__state = self.__waiting

    def __keywordseen(self, ttype, tstring, lineno):
        if ttype == tokenize.OP and tstring == '(':
            self.__data = []
            self.__msgid = ''
            self.__default = ''
            self.__lineno = lineno
            self.__state = self.__openseen
        else:
            self.__state = self.__waiting

    def __openseen(self, ttype, tstring, lineno):
        if ((ttype == tokenize.OP and tstring == ')') or
           (ttype == tokenize.NAME and tstring == 'mapping')):
            # We've seen the last of the translatable strings.  Record the line
            # number of the first line of the strings and update the list of
            # messages seen.  Reset state for the next batch.  If there were no
            # strings inside _(), then just ignore this entry.
            if self.__data or self.__msgid:
                if self.__default:
                    msgid = self.__msgid
                    default = self.__default
                elif self.__msgid:
                    msgid = self.__msgid
                    default = ''.join(self.__data)
                else:
                    msgid = ''.join(self.__data)
                    default = None
                self.__addentry(msgid, default)
            self.__state = self.__waiting
        elif ttype == tokenize.OP and tstring == ',':
            if not self.__msgid:
                self.__msgid = ''.join(self.__data)
            elif not self.__default:
                self.__default = ''.join(self.__data)
            self.__data = []
        elif ttype == tokenize.STRING:
            self.__data.append(safe_eval(tstring))

    def __addentry(self, msg, default=None, lineno=None, isdocstring=0):
        if lineno is None:
            lineno = self.__lineno

        if default is not None:
            default = unicode(default)
        if isinstance(msg, str):
            msg = msg.decode('utf-8')
        msg = Message(msg, default=default)
        entry = (self.__curfile, lineno)
        self.__messages.setdefault(msg, {})[entry] = isdocstring

    def set_filename(self, filename):
        self.__curfile = filename
        self.__freshmodule = 1

    def getCatalog(self):
        catalog = {}
        # Sort the entries.  First sort each particular entry's keys, then sort
        # all the entries by their first item.
        reverse = {}
        for k, v in self.__messages.items():
            keys = v.keys()
            keys.sort()
            reverse.setdefault(tuple(keys), []).append((k, v))
        rkeys = reverse.keys()
        rkeys.sort()
        for rkey in rkeys:
            rentries = reverse[rkey]
            rentries.sort()
            for msgid, locations in rentries:
                catalog[msgid] = []
                locations = locations.keys()
                locations.sort()
                for filename, lineno in locations:
                    catalog[msgid].append((filename, lineno))
        return catalog


def module_from_filename(filename, sys_path=None):
    if sys_path is None:
        sys_path = sys.path
    filename = os.path.abspath(filename)
    common_path_lengths = [
        len(os.path.commonprefix([filename, os.path.abspath(path)]))
        for path in sys_path]
    s = max(common_path_lengths) + 1
    # a path in sys.path ends with a separator
    if filename[s-2] == os.path.sep:
        s -= 1
    # remove .py ending from filenames
    return filename[s:-3].replace(os.path.sep, ".").replace(".__init__", "")


def py_strings(dir, domain, exclude=(), verify_domain=False):
    """Retrieve all Python messages from `dir` that are in the `domain`."""
    eater = TokenEater()
    for filename in find_files(dir, '*.py', exclude=exclude):
        if verify_domain:
            module_name = module_from_filename(filename)
            try:
                module = __import__(module_name, {}, {}, ("*",))
            except ImportError, e:
                print >> sys.stderr, ("Cannot import %s, assuming i18n "
                    "domain OK" % module_name)
            else:
                mf = getattr(module, '_', None)
                if hasattr(mf, '_domain'):
                    if mf._domain != domain:
                        continue
                elif mf:
                    print >>sys.stderr, ("Cannot figure out the i18n domain "
                        "for module %s, assuming it is OK" % module_name)
        fp = open(filename)
        try:
            eater.set_filename(filename)
            try:
                tokenize.tokenize(fp.readline, eater)
            except tokenize.TokenError, e:
                print >> sys.stderr, '%s: %s, line %d, column %d' % (e[0],
                    filename, e[1][0], e[1][1])
        finally:
            fp.close()
    return eater.getCatalog()


def zcml_strings(zcml, domain):
    from zope.configuration import xmlconfig
    from zope.configuration.config import ConfigurationMachine
    package, filename = zcml.rsplit(':', 1)
    package = __import__(package, {}, {}, ['*'])
    context = ConfigurationMachine()
    context.package = package
    xmlconfig.registerCommonDirectives(context)
    xmlconfig.include(context, filename, package)
    context.execute_actions(clear=False)
    return context.i18n_strings.get(domain, {})


def serialize(element, encoding='utf-8', omit=False):
    name = element.tag.rsplit('}', 1)[-1]
    yield "<%s" % name
    for key, value in element.attrib.items():
        if not key.startswith('{'):
            yield ' %s="%s"' % (key, escape(value, encoding=encoding))
    if element.text is None and len(element) == 0:
        yield ' />'
    else:
        yield '>'
        if element.text is not None:
            yield htmlescape(element.text)
        for child in element:
            for string in serialize(child, encoding=encoding, omit=False):
                yield string
        if omit is False:
            yield '</%s>' % name


pos = 0

def zpt_strings(directory, domain, exclude=()):
    """Retrieve all ZPT messages from `dir` that are in the `domain`."""
    global pos
    catalog = {}
    def extract_zpt_strings(element, i18n_domain=None):
        global pos
        # i18n:domain
        if getattr(element, 'i18n_domain', None):
            i18n_domain = element.i18n_domain
        # i18n:attributes
        if getattr(element, 'i18n_attributes', None) is not None and \
           i18n_domain == domain:
            for attribute, msgid in element.i18n_attributes:
                if attribute not in element.attrib:
                    continue
                msg = element.attrib[attribute]
                if msgid:
                    msg = Message(msgid, default=msg)
                else:
                    msg = Message(msg)
                pos += 1
                catalog.setdefault(msg, []).append((filename, pos))
        # i18n:translate
        if getattr(element, 'i18n_translate', None) is not None and \
           i18n_domain == domain and element.tal_content is None and \
           element.tal_replace is None:
            msg = ''
            if element.text:
                msg += element.text
            for i in element.getchildren():
                if i.i18n_name:
                    msg += u'${%s}' % i.i18n_name
                    extract_zpt_strings(i, i18n_domain=i18n_domain)
                else:
                    msg += u''.join(serialize(i))
                if i.tail:
                    msg += i.tail
            msg = u' '.join(msg.split())
            if element.i18n_translate:
                msg = Message(element.i18n_translate, default=msg)
            else:
                msg = Message(msg)
            pos += 1
            catalog.setdefault(msg, []).append((filename, pos))
            return
        # recursion on the children
        for i in element.getchildren():
            extract_zpt_strings(i, i18n_domain)
    parser = Parser()
    for filename in find_files(directory, '*.pt', exclude=exclude):
        data = open(filename, 'r').read()
        doc = parser.parse(data)
        pos = 0
        root = doc.getroot()
        extract_zpt_strings(root)
    return catalog


def find_files(dir, pattern, exclude=()):
    files = []
    def visit(files, dirname, names):
        names[:] = filter(lambda x: x not in exclude and \
            not x.endswith('.pt.py'), names)
        files += [os.path.join(dirname, name)
            for name in fnmatch.filter(names, pattern)
            if name not in exclude]
    os.path.walk(dir, visit, files)
    return files


def extract(path, locales, options):
    output_file = os.path.join(path, locales, options.domain + '.pot')
    maker = POTMaker(output_file, path)
    make_escapes(0)
    maker.add(py_strings(path, options.domain, exclude=options.exclude,
        verify_domain=options.verify_domain), path + '/')
    if options.zcml:
        try:
            if manager is not None:
                manager.push(registry=Registry())
                hook_registry()
            maker.add(zcml_strings(options.zcml, options.domain), path + '/')
        finally:
            if manager is not None:
                unhook_registry()
                manager.pop()
    registry = getSiteManager()
    for expression in options.expressions:
        name, component = map(string.strip, expression.split('=', 1))
        component = get_global(component)
        if IExpressionTranslator.implementedBy(component):
            component = component()
        registry.registerUtility(component, IExpressionTranslator, name)
    maker.add(zpt_strings(path, options.domain, exclude=()), path + '/')
    maker.write()


def get_global(attr):
    if ':' not in attr:
        raise ValueError("No ':' in global name", attr)
    mod, attr = attr.split(':', 1)
    mod = _import(mod)
    return eval(attr, mod.__dict__)


def _import(module_name):
    return __import__(module_name, {}, {}, ['*'])


def main(argv=sys.argv):
    parser = optparse.OptionParser(usage='%prog [options]')
    parser.add_option("-p", "--package", action="store", dest="package",
        help="python package to work on")
    parser.add_option("-l", "--locales", action="store", dest="locales",
        help="directory where the locales are stored")
    parser.add_option("-z", "--zcml", action="store", dest="zcml",
        help="read strings from the specified ZCML file")
    parser.add_option("", "--zcml-begin", action="store", dest="zcml_begin",
        help="function to be called before parsing the ZCML file")
    parser.add_option("", "--zcml-end", action="store", dest="zcml_end",
        help="function to be called after parsing the ZCML file")
    parser.add_option("-d", "--domain", action="store", dest="domain",
        help="translation domain")
    parser.add_option("-v", "--verify-domain", action="store_true",
        default=False, dest="verify_domain",
        help="verify the i18n domain for the Python files, defaults to False")
    parser.add_option("-e", "--exclude", action="append", default=[],
        dest="exclude", help="exclude a file from the extraction")
    parser.add_option("", "--expression", action="append", default=[],
        dest="expressions", help="Chameleon expression, `name=dotted.path:component'")
    options, args = parser.parse_args(argv)
    if options.package is None or options.locales is None:
        parser.print_help()
        sys.exit(1)
    path = pkg_resources.get_distribution(options.package).location
    locales = pkg_resources.resource_filename(options.package, options.locales)
    extract(path, locales, options)


if __name__ == '__main__':
    main()
