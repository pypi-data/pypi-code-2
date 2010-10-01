import sys
import time
import random
import itertools
import traceback
import shutil
from os.path import dirname, join, isfile, isdir, realpath
from os import getcwd, chdir
from ConfigParser import ConfigParser

from handcrank import version
from handcrank import generator
from handcrank.dirchange import Monitor

ascii_header = r"""
__               .--------.
   `.      ______|        |\
    |     / ```` |        | |
    |     |  ,---|        |/      
    |_____|  |   `--------'         
    | ````   |                    
    |~~~~~~~/ 
___.'"""


class MissingConfigFile(Exception):
    """
    Raised when the configuration file for a site cannot be found or could not
    be opened
    """
    pass


class Runner(object):
    """
    Responsible for doing a majority of the work in the system.  It's the
    clearing house of activity, passing control to a generator or building a
    new site from a template.
    """
    # Little messages that occur whenever the handle is cranked
    crank_list = ('click click click', 'squeak spueak spueak',
        'crank crank crank', 'erkkk erkkk', 'round it goes',
        'cranking the handle', 'is that smoke?', 'chugga chugga',
        'zzzzzzzzrrrrrazzz', 'scratchy clicky erkkkk',)
    rotated_cranks = random.sample(crank_list, len(crank_list))

    def __init__(self, options):
        self.options = options

        print ascii_header
        print "\n\nHandcrank version %s" % version.number

    def begin(self):
        """
        Performs the action specified and begins the actual work

        This can be any of the `actions` parser arguments.  See
        handcrank/__init__.py for a list of what those can be.
        """
        getattr(self, self.options.actions)()

    def get_delegate_class(self, delegate_cls, from_dir):
        """
        A delegate is able to alter the behavior of the generator.

        This method tries to import delegate_cls from the `delegate` module
        within from_dir (meaning there needs to be a delegate.py in there), if
        it can't succeed it returns a class that essentially does nothing but
        provides all the necessary methods.

        Some of the things it can do:
            * Change the order of the source files so they appear in the
              generated output in a different order
            * Add extra context to the Template when it renders (for example,
              adding a variable called 'last10tweets' that are...well I'm sure
              you can figure out what that is.
        """
        try:
            if from_dir not in sys.path:
                sys.path.append(from_dir)
            dlg = __import__('delegate', globals(), locals(), [delegate_cls])
            return getattr(dlg, delegate_cls)
        except ImportError as ie:
            return generator.DelegateBase

    def build_generator_options(self, config_file):
        """
        When the generate command is called, this takes a ConfigParser object
        and generates the options for our Generator.

        The reason that this is necessary is that our config file has relative
        paths inside of it.  So an important step is to expand those relative
        paths into real paths so the generator doesn't have to it.

        This returns a dictionary that is suitable for creating a Generator
        object using the **gen_options syntax.
        """
        config = ConfigParser()
        try:
            config.readfp(open(config_file))
        except IOError:
            raise MissingConfigFile('Could not find %s' % config_file)

        options = {
            'from_dir': config.get('source', 'directory'),
            'tmp_dir': config.get('template', 'directory'),
            'out_dir': config.get('output', 'directory')}

        for d in options:
            dir = options[d]
            if not dir.startswith('/'):
                options[d] = realpath(join(dirname(config_file), dir))

        options.update({
            'template_file': config.get('template', 'name'),
            'output_file': config.get('output', 'name')})

        return options

    def generate(self):
        """
        This command is used when the user has a site directory with
        source files and a template that they wish to create a generated
        output.

        The basic idea is that a set of reStructuredText files become HTML
        files with possibly Javascript and CSS to go along with it.

        The generated output can then be opened in a browser locally and
        reviewed.
        """
        if self.options.site_dir:
            try:
                chdir(self.options.site_dir)
            except OSError:
                print("Cannot access %s" % self.options.site_dir)
                print("Do you mean to run `handcrank --sitedir %s "
                      "startsite`?" % self.options.site_dir)
                sys.exit(1)

        self.config_file = join(getcwd(), 'config.cfg')

        gen_options = self.build_generator_options(self.config_file)

        if 'delegate' in gen_options:
            cls_str = gen_options['delegate']
        else:
            cls_str = 'Delegate'

        delegate_cls = self.get_delegate_class(cls_str,
            dirname(self.config_file))

        def inner_run(gen_options):
            """
            Used by both the single run generate and the daemon mode to generate
            the site, it uses the generator class and the options that were
            assembled from the config file to create a output directory that
            represents the generated site.

            After it successfully runs, it prints a report letting the user
            know some information about what was generated and where it ended
            up.
            """
            gen = generator.OnePageGenerator(**gen_options)
            gen.delegate = delegate_cls()

            report = gen.turn_handle()
            print ' %s' % messages.next()
            report.dump()

        def inner_loop(gen_options):
            """
            This loop continually runs until the user breaks it with a CTRL-C
            or other KeyboardInterrupt raising event.

            This acts similar to a daemon.  It will continually monitor the
            source and template directories and a change in those files will
            result in the inner_run being called.
            """
            while True:
                try:
                    if has_changed():
                        inner_run(gen_options)
                    time.sleep(0.5)
                except KeyboardInterrupt:
                    sys.exit(0)
                except Exception as e:
                    print traceback.format_exc()

        def has_changed():
            """
            We need to monitor the template directory and the source
            directories for change.  If either one of these do, we return True
            and that can let the generator then re-generate the site content to
            the output directory.
            """
            return from_monitor.has_changed() or tmp_monitor.has_changed()

        messages = itertools.cycle(self.rotated_cranks)

        inner_run(gen_options)

        if self.options.daemon:
            print "Running in daemon mode, hit <CTRL-C> to exit"
            from_monitor = Monitor(gen_options['from_dir'],
                ignore_directory=[gen_options['out_dir']])
            tmp_monitor = Monitor(gen_options['tmp_dir'],
                ignore_directory=[gen_options['out_dir']])
            inner_loop(gen_options)

    def startsite(self):
        """
        Creates a site directory out of an internal template that handcrank
        has.  This saves the user some time as they do not have to create the
        files manully.  It's only argument, which is required, is the site_dir
        in which it will create the new directory.

        If the directory exists, this command will fail as it would be very
        uncommon to want to overwrite an existing directory.

        This command is handy for beginning a new project, but not much use
        after that.
        """
        site_dir = self.options.site_dir

        if not site_dir:
            print('Whoops, specify --sitedir to tell us where '
                'to create your new site')
            sys.exit(1)

        if isdir(site_dir):
            print('Whoa there, this directory already exists; refusing to '
                'clobber it because it\'s most likely not what you want. '
                'You delete it if that\'s what you really need.')
            sys.exit(1)

        skeleton = join(dirname(__file__), 'skeleton')
        shutil.copytree(skeleton, site_dir)

        print 'Created site here: %s' % site_dir
        print 'Run `handbrack --sitedir %s generate` to get cranking' % site_dir

        sys.exit(0)
