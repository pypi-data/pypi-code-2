import os, sys
from urlparse import urlparse, urlunparse
from ConfigParser import ConfigParser
from svnlog import *

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'svnpoller.ini')

MAIL_TEMPLATE = """\
* Revision: %(rev)s
* Author: %(auth)s
* Date: %(date)s
* Message:
%(msg)s

* Paths:
%(paths)s

* Diff:
%(diff)s
"""

def build_message(rev, auth, date, msg, paths, diff):
    return MAIL_TEMPLATE % locals()


def main(config_file, sender):
    conf = ConfigParser()
    conf.read(config_file)

    mail_data = dict(
        smtpserver = conf.get('mail','smtpserver'),
        fromaddr = conf.get('mail','fromaddr'),
    )

    for sect in conf.sections():
        if sect == 'mail':
            continue

        opts = dict(conf.items(sect))

        newest_rev = opts.get('newest_rev', '0')
        next_rev = int(newest_rev)+1
        urls = filter(None, opts.get('url').splitlines())
        base_path = os.path.commonprefix([urlparse(x)[2].split('/')
                                          for x in urls])
        base_url = list(urlparse(urls[0]))
        base_url[2] = '/'.join(base_path)
        base_url = urlunparse(base_url)
        revs = get_revisions(urls, next_rev)
        logs = (get_log(base_url, rev) for rev in revs)

        for log in logs:
            text = build_message(
                    log.rev, log.author, log.date, log.msg,
                    '\n'.join(" %s %s" % x for x in log.paths),
                    log.diff)

            rev = log.rev
            subject = '[%(sect)s: %(rev)s]' % locals()

            sender(
                mail_data['fromaddr'],
                opts.get('address'),
                subject,
                text,
                smtpserver=mail_data['smtpserver'])

            conf.set(sect, 'newest_rev', rev)

    conf.write(open(config_file, 'wt'))


def dry_run_sender(fromaddr, toaddrs, subject, message_text,
                   smtpserver='localhost', charset='utf-8', sender=None):

    def storage(fromaddr, toaddrs, msg, smtpserver):
        print msg

    from sendmail import send
    send(fromaddr, toaddrs, subject, message_text,
         smtpserver=smtpserver, charset=charset, sender=storage)


def run():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-n', '--dry-run',
                      action='store_true', default=False,
                      dest='dry_run')
    options, args = parser.parse_args()


    if len(args) > 0:
        config_file = args[0]
    else:
        config_file = CONFIG_PATH

    if options.dry_run:
        sender = dry_run_sender
    else:
        import sendmail
        sender = sendmail.send

    main(config_file, sender)


if __name__ == '__main__':
    run()

