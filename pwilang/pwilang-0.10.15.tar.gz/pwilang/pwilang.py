# This is the library !

import common, preproc, parse, output, evaluate
import sys
from cStringIO import StringIO
import string

from jinja2 import Environment, FileSystemLoader, Template
from jinja2.loaders import split_template_path, open_if_exists, TemplateNotFound
from jinja2.ext import loopcontrols, do

from jinjaext import filters, AbspathExtension, SassExtension

from os import path, getcwd, remove, chdir
from os.path import abspath, dirname, expanduser
from shutil import copy

try:
    import parsetab # Do that to force inclusion in the setup.py
except:
    pass

class PwilangLoader (FileSystemLoader):
    def __init__ (self, *args, **kwargs):
        self.with_pwilang = kwargs.pop ('with_pwilang', True)
        super (PwilangLoader, self).__init__ (*args, **kwargs)

    def get_source(self, environment, template):
        pieces = split_template_path (template)

        for searchpath in self.searchpath:
            filename = path.join (searchpath, *pieces)
            f = open_if_exists (filename)

            if f is None:
                continue
            try:
                contents = preproc.force_unicode (f.read ())
            finally:
                f.close ()

            mtime = path.getmtime (filename)
            def uptodate ():
                try:
                    return path.getmtime (filename) == mtime
                except OSError:
                    return False

            if self.with_pwilang:
                lines = preproc.get_lines_from_string (contents)

                root = None
                if lines:
                    root = evaluate.eval_tree (parse.parselines (lines))
                    buf = StringIO ()
                    output.output_indented (root, buf)
                    contents = buf.getvalue ().decode ('utf-8')
                    buf.close ()

                    error = common.error_flag
                    errors = StringIO ()

                    common.flush_errors (errors)
                    err = errors.getvalue ()
                    errors.close ()

                    if error:
                        raise Exception (err)

            return contents, filename, uptodate
        raise TemplateNotFound (template)

here = abspath (dirname (__file__))
default_dirs = ['.', path.join (getcwd (), 'templates'), expanduser ("~/.pwilang/templates"), path.join (here, 'templates')]

def get_env (dirs):
    loader = PwilangLoader (dirs)
    environment = Environment (loader=loader, line_statement_prefix="%", extensions=[AbspathExtension, SassExtension, loopcontrols, do])
    return environment

def process (iterable, output_fname, ctx={}, with_pwilang=True, with_jinja2=True, env=None):
    if not env:
        env = get_env (default_dirs)

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

            common.flush_errors (errors)
            err = errors.getvalue ()
            errors.close ()

            if error:
                raise Exception (err)
    else:
        contents = string.join (iterable) # \n ?

    contents = unicode (contents, 'utf-8')
    if with_jinja2:

        tmpl = env.from_string (contents)
        contents = tmpl.render (ctx)

    out = sys.stdout if output_fname == "-" else open (output_fname, "w")
    try:
        out.write (contents.encode ('utf-8'))
    finally:
        if out != sys.stdout:
            out.close ()

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
        copy (abspath (filename), header_path)
    except:
        pass

    footer_path = abspath ('%s_footer.html' % (filename))
    try:
        copy (abspath (filename), footer_path)
    except:
        pass

    if headers:
        cmd = "%(wkhtmltopdf)s %(options)s %(source)s --header-html %(header)s --footer-html %(footer)s %(pdfname)s" % dict (wkhtmltopdf=wkhtmltopdf, options=options, source=filename, pdfname=pdfname, header=header_path, footer=footer_path)
    else:
        cmd = "%(wkhtmltopdf)s %(options)s %(source)s %(pdfname)s" % dict (wkhtmltopdf=wkhtmltopdf, options=options, source=filename, pdfname=pdfname, header=header_path, footer=footer_path)
    print cmd

    args = shlex.split (cmd.encode ('utf-8'))
    call (args)

    remove (header_path)
    remove (footer_path)

def compile_pwi (filename, options, ctx):
    # OPENING THE OUTPUT FILES FOR THE HTML

    if options.pdf and options.output == "-":
        # No html output file specified, we need to open a temporary file.
        import tempfile
        out = tempfile.mkstemp ()
        options.output = out[1] + '.html'

    f = open (filename, 'r')
    current = abspath (getcwd ())
    if dirname (filename):
        chdir (dirname (filename))
    process (f, options.output, ctx, with_pwilang=not options.no_pwi, with_jinja2=not options.no_jinja)
    chdir (current)
    f.close ()

    if options.pdf:
        create_pdf (options.output, options.pdf, not options.no_headers)
