# tranchitella.recipe.i18n
# Copyright (C) 2008-2010 Tranchitella Kft. <http://tranchtella.eu>

import os
import optparse
import pkg_resources
import sys


SEARCHING = 0
COMMENT = 1
MSGID = 2
MSGSTR = 3
MSGDONE = 4

def getMessageDictionary(file):
    """Simple state machine."""
    msgs = []
    comment = []
    msgid = []
    msgstr = []
    fuzzy = False
    line_counter = 0
    status = SEARCHING
    for line in file.readlines():
        line = line.strip('\n')
        line_counter += 1
        # handle Events
        if line.startswith('#'):
            status = COMMENT
        elif line.startswith('msgid'):
            line = line[6:]
            line_number = line_counter
            status = MSGID
        elif line.startswith('msgstr'):
            line = line[7:]
            status = MSGSTR
        elif line == '':
            status = MSGDONE
        # actions based on status
        if status == MSGID:
            msgid.append(line.strip('"'))
        elif status == MSGSTR:
            msgstr.append(line.strip('"'))
        elif status == COMMENT:
            if line.startswith('#, fuzzy'):
                fuzzy = True
            comment.append(line[1:].strip())
        elif status == MSGDONE:
            status = SEARCHING
            if ''.join(msgid):
                msgs.append((''.join(msgid), ''.join(msgstr), line_number,
                    '\n'.join(comment), fuzzy) )
            comment = []
            msgid = []
            msgstr = []
            fuzzy = False
    return msgs


def stats(path):
    print 'Language    Total    Done    Not Done    Fuzzy      Done %'
    print '=========================================================='
    languages = os.listdir(path)
    languages.sort()
    for language in languages:
        lc_messages_path = os.path.join(path, language, 'LC_MESSAGES')
        if not os.path.isdir(lc_messages_path):
            continue
        msgs = []
        for domain_file in os.listdir(lc_messages_path):
            if domain_file.endswith('.po'):
                domain_path = os.path.join(lc_messages_path, domain_file)
                file = open(domain_path, mode='r')
                msgs += getMessageDictionary(file)
        if len(msgs) == 0:
            continue
        total = len(msgs)
        not_done = len([msg for msg in msgs if msg[1] == ''])
        fuzzy = len([msg for msg in msgs if msg[4] is True])
        done = total - not_done - fuzzy
        percent_done = 100.0 * done/total
        line = language + ' '*(8-len(language))
        line += ' '*(9-len(str(total))) + str(total)
        line += ' '*(8-len(str(done))) + str(done)
        line += ' '*(12-len(str(not_done))) + str(not_done)
        line += ' '*(9-len(str(fuzzy))) + str(fuzzy)
        pd_str = '%0.2f %%' %percent_done
        line += ' '*(12-len(pd_str)) + pd_str
        print line


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
    stats(locales)


if __name__ == '__main__':
    main()
