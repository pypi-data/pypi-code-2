# This is the library !

import common, preproc, parse, output, evaluate
import sys
from cStringIO import StringIO
import string

from jinja2 import Environment, FileSystemLoader, Template
from jinja2.loaders import split_template_path, open_if_exists

from jinjaext import filters, AbspathExtension

from os import path, getcwd, symlink, remove, chdir
from os.path import abspath, dirname, expanduser

class PwilangLoader (FileSystemLoader):
    def __init__ (self, *args, **kwargs):
        self.with_pwilang = kwargs.pop ('with_pwilang', True)
        super (PwilangLoader, self).__init__ (*args, **kwargs)

    def get_source(self, environment, template):
        pieces = split_template_path(template)
        for searchpath in self.searchpath:
            filename = path.join(searchpath, *pieces)
            f = open_if_exists(filename)
            if f is None:
                continue

            try:
                contents = f.read().decode(self.encoding)
            finally:
                f.close()

            if self.with_pwilang:
                lines = preproc.get_lines_from_string (contents)

                root = None
                if lines:
                    root = evaluate.eval_tree (parse.parselines (lines))
                    buf = StringIO ()
                    output.output_indented (root, buf)
                    contents = buf.getvalue ()
                    buf.close ()

                    error = common.error_flag
                    errors = StringIO ()

                    common.flush_errors (errors)
                    err = errors.getvalue ()
                    errors.close ()

                    if error:
                        raise Exception (err)

            mtime = path.getmtime(filename)
            def uptodate():
                try:
                    return path.getmtime(filename) == mtime
                except OSError:
                    return False
            return contents, filename, uptodate
        raise TemplateNotFound(template)

here = abspath (dirname (__file__))
default_dirs = [getcwd (), path.join (getcwd (), 'templates'), expanduser ("~/.pwilang/templates"), path.join (here, 'templates')]

jinja_env = None
def set_env (dirs=default_dirs):
    global jinja_env
    loader = PwilangLoader (default_dirs)
    jinja_env = Environment (loader=loader, extensions=[AbspathExtension])

def process (iterable, out=sys.stdout, ctx={}, with_pwilang=True, with_jinja2=True):
    if isinstance (iterable, str) or isinstance (iterable, unicode):
        iterable = iterable.split ('\n')

    contents = ""

    # PWILANG PART
    if with_pwilang:
        lines = preproc.get_lines_from_iterable (iterable)

        root = None
        if lines:
            root = evaluate.eval_tree (parse.parselines (lines))
            buf = StringIO ()
            output.output_indented (root, buf)
            contents = buf.getvalue ()
            buf.close ()

            error = common.error_flag
            errors = StringIO ()

            if out == sys.stdout:
                common.flush_errors ()
            else:
                common.flush_errors (errors)
                err = errors.getvalue ()
                errors.close ()

            if error:
                raise Exception (err)
    else:
        contents = string.join (iterable) # \n ?

    if with_jinja2:
        if not jinja_env:
            set_env ()
        env = jinja_env

        if not with_pwilang:
            loader = FileSystemLoader (default_dirs)
            env = Environment (loader=loader, extensions=[AbspathExtension])

        for key, value in filters.items ():
            env.filters[key] = value

        contents = unicode (contents, 'utf-8')
        tmpl = env.from_string (contents)
        contents = tmpl.render (ctx)

    out.write (contents.encode ('utf-8'))

### PDF SECTION

import re
re_wkhtmloptions = re.compile ("<!--wkhtmltopdf (?P<options>.*?)-->")
wkhtmltopdf = "wkhtmltopdf"
from subprocess import call
import shlex

def create_pdf (filename, pdfname, headers=True):
    """ Creates a PDF file using shlex """
    f = open (filename, 'r')
    htmlcontents = f.read ()
    f.close ()
    match = re_wkhtmloptions.search (htmlcontents)

    options = ""
    if match:
        options = match.group ('options')

    header_path = abspath ('%s_header.html' % (filename))
    try:
        symlink (abspath (filename), header_path)
    except:
        pass

    footer_path = abspath ('%s_footer.html' % (filename))
    try:
        symlink (abspath (filename), footer_path)
    except:
        pass

    if headers:
        cmd = "%(wkhtmltopdf)s %(options)s %(source)s --header-html %(header)s --footer-html %(footer)s %(pdfname)s" % dict (wkhtmltopdf=wkhtmltopdf, options=options, source=filename, pdfname=pdfname, header=header_path, footer=footer_path)
    else:
        cmd = "%(wkhtmltopdf)s %(options)s %(source)s %(pdfname)s" % dict (wkhtmltopdf=wkhtmltopdf, options=options, source=filename, pdfname=pdfname, header=header_path, footer=footer_path)

    args = shlex.split (cmd.encode ('utf-8'))
    call (args)

    remove (header_path)
    remove (footer_path)
