#!/usr/bin/python
import csv
import logging
import os


def migrate():
    """ Migrate csv files to po
    """
    logging.info('migration started')
    languages = ['es', 'cs', 'da', 'de', 'et', 'el', 'en', 'fr', 'it', 'lv', 'lt', 
                 'hu', 'mt', 'nl', 'pl', 'pt', 'sk', 'sl', 'fi', 'sv', 'ro', 'bg'] 

    fieldnames = ['message_id'] + languages

    docs_path = './napo/'
    for file_path in ['napo7.csv', 'napo8.csv', 'napo9.csv']:
        logging.info(file_path)
        name = os.path.join(docs_path, file_path)
        f = open(name, 'r').read().split('\n')
        for l in f:
            l.strip(',')

        reader = csv.DictReader(f, fieldnames, delimiter=',')
        for row in reader:
            for l in languages:
                if not row['message_id']:
                    continue
                po_docs_path = '../i18n'
                po_filename = 'osha-napo.%s.po' % l
                fname = os.path.join(po_docs_path, po_filename)
                pofile = open(fname, 'a')
                pofile.write('msgid "%s" \n' % row['message_id'])
                pofile.write('msgstr "%s" \n\n' % row[l])
                pofile.close()

        logging.info('fertig!')


if __name__ == '__main__':
    migrate()
