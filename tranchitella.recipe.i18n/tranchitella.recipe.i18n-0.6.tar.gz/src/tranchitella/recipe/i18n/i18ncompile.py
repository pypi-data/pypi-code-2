# tranchitella.recipe.i18n
# Copyright (C) 2008-2010 Tranchitella Kft. <http://tranchtella.eu>

import os
import optparse
import pkg_resources
import sys


def compile(path):
    for language in os.listdir(path):
        lc_messages_path = os.path.join(path, language, 'LC_MESSAGES')
        if not os.path.isdir(lc_messages_path):
            continue
        msgs = []
        for domain_file in os.listdir(lc_messages_path):
            if not domain_file.endswith('.po'):
                continue
            domain_path = os.path.join(lc_messages_path, domain_file)
            domain = domain_file.split('.')[0]
            mo_path = domain_path[:-3] + '.mo'
            print 'Compiling language "%s", domain "%s"' % (language, domain)
            os.system('msgfmt "%s" -o "%s"' % (domain_path, mo_path))


def main(argv=sys.argv):
    parser = optparse.OptionParser(usage='%prog [options]')
    parser.add_option("-p", "--package", action="store", dest="package",
        help="python package to work on")
    parser.add_option("-l", "--locales", action="store", dest="locales",
        help="directory where the locales are stored")
    options, args = parser.parse_args(argv)
    if options.package is None or options.locales is None:
        parser.print_help()
        sys.exit(1)
    locales = pkg_resources.resource_filename(options.package, options.locales)
    compile(locales)


if __name__ == '__main__':
    main()
