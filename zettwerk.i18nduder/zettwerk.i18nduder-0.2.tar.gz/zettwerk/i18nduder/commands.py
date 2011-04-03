import i18ndude.script

import os.path
import sys
import subprocess
from StringIO import StringIO


def _get_package_path(options, parser):
    """ helper method to return the path to the package.
    stops if the path not exists. """
    package_name = options.package
    try:
        __import__(package_name)
        package_path = sys.modules[package_name].__path__[0]
    except:
        parser.error('Invalid package name given')
    return package_path


def _get_locales_path(options, parser):
    """ helper method to return the path to the locales
    folder of the package. stops if the package path not
    exists. """
    package_path = _get_package_path(options, parser)
    return os.path.join(package_path,
                        'locales')


def _get_po_name(options):
    if options.domain:
        return options.domain
    return options.package


def create(options, parser):
    locales_path = _get_locales_path(options, parser)
    po_name = _get_po_name(options)

    if not os.path.exists(locales_path):
        os.mkdir(locales_path)
        print "Created locales folder at: %s" % (locales_path)
        print "Don't forget to add this to your configure.zcml:"
        print '<i18n:registerTranslations directory="locales" />'
    else:
        print "Locales folder already exists at: %s" % (locales_path)
    if options.languages:
        for lang in options.languages.split(','):
            lang = lang.strip()
            if lang:
                path_parts = [
                            locales_path,
                            lang,
                            'LC_MESSAGES']
                for p in range(len(path_parts)):
                    target_path = os.path.join(*path_parts[:p + 1])
                    if not os.path.exists(target_path):
                        os.mkdir(target_path)

                path_parts.append('%s.po' % (po_name))
                target_path = os.path.join(*path_parts)
                if not os.path.exists(target_path):
                    file(target_path, 'w').close()
                    print "- language: %s and domain: %s " \
                        "added" % (lang, po_name)
                else:
                    print "- language: %s and domain: %s already " \
                        "exists" % (lang, po_name)
    else:
        print "No languages given - skipping creation"


def update(options, parser):
    locales_path = _get_locales_path(options, parser)
    po_name = _get_po_name(options)

    if not os.path.exists(locales_path):
        parser.error('locales directory not found - run create command first')
    os.chdir(locales_path)

    dude_command = 'rebuild-pot'
    dude_opts = ['--pot',
                 '%s.pot' % (po_name),
                 '--create',
                 po_name,
                 os.path.join('.', '..')]
    sys.argv[1:] = [dude_command] + dude_opts
    i18ndude.script.main()

    dude_command = 'sync'
    for lang in os.listdir('.'):
        if os.path.isdir(os.path.join('.', lang)) and \
                'LC_MESSAGES' in os.listdir(os.path.join('.', lang)):
            dude_opts = ['--pot',
                         '%s.pot' % (po_name),
                         '%s/LC_MESSAGES/%s.po' % (lang, po_name)]
            sys.argv[1:] = [dude_command] + dude_opts
            i18ndude.script.main()


def find(options, parser):
    package_name = options.package
    package_path = _get_package_path(options, parser)
    os.chdir(package_path)
    working_dir = os.getcwd()

    output_file = os.path.join(
        working_dir,
        '%s-untranslated' % (package_name)
        )
    dude_command = 'find-untranslated'
    dude_opts = ['.']
    sys.argv[1:] = [dude_command] + dude_opts

    output = StringIO()
    sys.stdout = output

    i18ndude.script.main()

    sys.stdout = sys.__stdout__

    f = file(output_file, 'w')
    f.write(output.getvalue())
    f.close()

    print "wrote output to: %s" % (output_file)


def mo(options, parser):
    po_name = _get_po_name(options)
    locales_path = _get_locales_path(options, parser)
    if not os.path.exists(locales_path):
        parser.error('locales directory not found - run create command first')

    os.chdir(locales_path)

    for lang in os.listdir('.'):
        if os.path.isdir(os.path.join('.', lang)) and \
                'LC_MESSAGES' in os.listdir(os.path.join('.', lang)):
            args = ['msgfmt',
                    '%s/LC_MESSAGES/%s.po' % (lang,
                                              po_name),
                    '-o',
                    '%s/LC_MESSAGES/%s.mo' % (lang,
                                              po_name)]
            subprocess.call(args)
            print "- language: %s and domain: %s - mo created. " % (lang,
                                                                    po_name)
