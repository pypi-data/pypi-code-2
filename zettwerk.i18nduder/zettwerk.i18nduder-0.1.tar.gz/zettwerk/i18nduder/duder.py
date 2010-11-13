# -*- coding: utf-8 -*-
import i18ndude.script
import sys
import os
import os.path
import optparse
import subprocess
from StringIO import StringIO


class UnformatedDescriptionFormatter(optparse.IndentedHelpFormatter):
    """ formater class to have unformated description output """

    def format_description(self, description):
        return description


def main():
    usage = 'usage: %prog command -p package.name or --help for details'
    description = u'''Available commands:
  create\t\tCreate the locales folder and/or add given languages
  update\t\tCall rebuild-pot and sync
  mo\t\t\tCall msgfmt to build the mo files
  find\t\t\tFind untranslated strings
'''
    parser = optparse.OptionParser(usage=usage,
                                   description=description,
                                   formatter=UnformatedDescriptionFormatter())

    parser.add_option('-p', '--package',
                      help="Name of the package")
    parser.add_option('-l', '--languages',
                      help="List of comma-separated names of language strings. Only used for create command. For example: -l en,de")

    options, args = parser.parse_args()
    if not args:
        parser.error('no commands given')

    if not options.package:
        parser.error('no package given')

    package_name = options.package
    try:
        __import__(package_name)
        package_path = sys.modules[package_name].__path__[0]
    except:
        parser.error('Invalid package name given')

    locales_path = os.path.join(package_path,
                                'locales')
    working_dir = os.getcwd()

    for command in args:
        os.chdir(working_dir)
        if command == 'create':
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
                        if not os.path.exists(os.path.join(locales_path, lang)):
                            os.mkdir(os.path.join(locales_path, lang))
                            os.mkdir(os.path.join(locales_path, lang, 'LC_MESSAGES'))
                            empty = file(os.path.join(locales_path, lang, 'LC_MESSAGES', '%s.po' % (package_name)), 'w').close()
                            print "- %s language added" % (lang)
                        else:
                            print "- %s language already exists" % (lang)
            else:
                print "No languages given - skipping creation"

        if command == 'update':
            if not os.path.exists(locales_path):
                parser.error('locales directory not found - run create command first')
            os.chdir(locales_path)

            dude_command = 'rebuild-pot'
            dude_opts = ['--pot',
                         '%s.pot' % (package_name),

                         '--create',
                         package_name,
                         os.path.join('.', '..')]
            sys.argv[1:] = [dude_command] + dude_opts
            i18ndude.script.main()

            dude_command = 'sync'
            for lang in os.listdir('.'):
                if os.path.isdir(os.path.join('.', lang)) and \
                        'LC_MESSAGES' in os.listdir(os.path.join('.', lang)):
                    dude_opts = ['--pot',
                                 '%s.pot' % (package_name),
                                 '%s/LC_MESSAGES/%s.po' % (lang, package_name)]
                    sys.argv[1:] = [dude_command] + dude_opts
                    i18ndude.script.main()

        if command == 'find':
            os.chdir(package_path)

            output_file = os.path.join(working_dir,
                                       '%s-untranslated' % (package_name))
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

        if command == 'mo':
            if not os.path.exists(locales_path):
                parser.error('locales directory not found - run create command first')

            os.chdir(locales_path)

            for lang in os.listdir('.'):
                if os.path.isdir(os.path.join('.', lang)) and \
                        'LC_MESSAGES' in os.listdir(os.path.join('.', lang)):
                    args = ['msgfmt',
                            '%s/LC_MESSAGES/%s.po' % (lang,
                                                      package_name),
                            '-o',
                            '%s/LC_MESSAGES/%s.mo' % (lang,
                                                      package_name)]
                    subprocess.call(args)
