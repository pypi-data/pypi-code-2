import sys
import shutil
import itertools
from os import listdir
from os.path import isfile, isdir, join
from docutils.core import publish_parts

from jinja2 import Template

from handcrank.report import Report

# Imported to support additional directives and rolls
from handcrank import directives
from handcrank import roles

# OrderedDict import
try:
    # Python >= 2.7 / 3.1
    from collections import OrderedDict
except ImportError:
    # Python < 2.7
    from ordereddict import OrderedDict


class GeneratorError(Exception):
    pass


class DelegateBase(object):
    """
    Used along side Generator classes to alter the behavior of the generated
    content
    """
    def items_place_first(self, source_list, *args):
        """
        Allows you to place the keys specified by *args first in the source
        list.

        For example if you had this:
            source_list = [
                ('john', 'cleese'), ('eric', 'idle'), ('terry', 'jones')]

        Calling items_place_first(source_list, 'terry') would result in:
            source_list = [
                ('terry', 'jones'), ('john', 'cleese'), ('eric', 'idle')]
        """
        sldict = OrderedDict() 
        for basename, source in source_list:
            sldict[basename] = source

        od = OrderedDict()
        for item in args:
            try:
                od[item] = sldict.pop(item)
            except KeyError:
                available = sldict.keys()
                available.sort()
                raise GeneratorError('Item %s not found, available are: %s' %
                    (item, ', '.join(available)))

        for item in sldict:
            od[item] = sldict[item]

        return od.items()

    def items_sort_alpha(self, source_list):
        """
        Alphabetizes the source_list by key
        """
        source_list = list(source_list)
        source_list.sort(lambda x, y: cmp(x[0].lower(), y[0].lower()))
        return source_list

    def provide_extra_context(self):
        """
        Specify, by returning a dictionary, any extra context variables you
        need to render this site
        """
        return {}

    def sort_source_list(self, source_list):
        """
        Allows the list or source files to be sorted differently
        """
        return self.items_sort_alpha(source_list)


class SourceList():
    """
    Converts a directory of files into a dictionary of::

        { 'FILENAME': 'FILE CONTENTS' }
    """
    def __init__(self, dir, filter_extension='rst'):
        self.dir = dir
        self.extension = filter_extension

    def __iter__(self):
        return iter(self.open())

    def open(self):
        if not isdir(self.dir):
            raise GeneratorError('%s is not a directory' % self.dir)

        for path in listdir(self.dir):
            filename = join(self.dir, path)
            if not isfile(filename):
                continue
            if not path.endswith(self.extension):
                continue
            with open(filename) as fh:
                yield path, fh.read()


class OnePageGenerator():
    """
    Takes a directory ``from_dir`` of rST files and creates a single page
    website from it into ``out_dir`` using the template in ``tmp_dir``

        from_dir      The directory that contans the rST files
        out_dir       Where you want the generator to create the site
        tmp_dir       The template directory, usually called 'template'
    """
    delegate = DelegateBase()

    def __init__(self, **options):
        """
        Required parameters: from_dir, out_dir, tmp_dir
        """
        self.options = options

        try:
            assert self.options['from_dir']
            assert self.options['out_dir']
            assert self.options['tmp_dir']
        except (AssertionError, KeyError):
            raise GeneratorError(self.__init__.__doc__)

        for f in ('template_file', 'output_file',):
            if not f in self.options:
                self.options[f] = 'index.html'

        self.source_list = SourceList(options['from_dir'])
        self.indicator = None

    def tick(self):
        """
        Writes an indicator to sys.out that lets the user know something is
        happening
        """
        if not self.indicator:
            self.indicator = itertools.cycle('-_')

        sys.stdout.write(self.indicator.next())
        sys.stdout.flush()

    def turn_handle(self):
        """
        Runs through all the rST files and creates the output files based on
        the template in tmp_dir
        """
        gathering, source_count = self.convert_to_html()

        shutil.rmtree(self.options['out_dir'], ignore_errors=True)
        shutil.copytree(self.options['tmp_dir'], self.options['out_dir'])

        context = {
            'gathering': gathering}

        context.update(self.delegate.provide_extra_context())

        generated_count = 0
        
        with open(join(self.options['tmp_dir'],
            self.options['template_file'])) as fh:
            template = Template(fh.read())

            with open(join(self.options['out_dir'],
                self.options['output_file']), 'w') as wfh:
                generated_count += 1
                wfh.write(template.render(**context))

        return Report(
            from_dir=self.options['from_dir'],
            out_dir=self.options['out_dir'],
            tmp_dir=self.options['tmp_dir'],
            generated_count=generated_count,
            source_count=source_count,
            entry_point=None)

    def convert_to_html(self, docutils_settings={}):
        """
        Converts the source rST files to HTML.

        Return a tuple of dictiory, integer where the dictionary has the title
        as it's key and the HTML source as it's value.  The second element in
        the tuple is an integer representing the number of source files
        rendered.
        """
        source_count = 0
        gathering = OrderedDict()

        sl_srt = self.delegate.sort_source_list

        for basename, source in sl_srt(self.source_list):
            parts = publish_parts(
                source=source,
                writer_name="html4css1",
                settings_overrides=docutils_settings)

            parts['basename'] = basename

            if parts['title'] in gathering:
                raise GeneratorError(
                    'Title %s already present for %s' % (
                         parts['title'], basename))

            gathering[parts['title']] = parts
            self.tick()
            source_count += 1

        return gathering, source_count
