import getpass, poplib
import logging

from tools.email.errors import EmailNotFound, AbuseError


def connect(host, user, password):
    logging.debug('POP3: open mailbox %s:%s' % (user, host))
    m = poplib.POP3(host)
    m.user(user)
    m.pass_(password)
    return m


def find_message(host, user, password, anchor, delete=False):
    """
    Search for message contains acnhor text.
    """

    m = connect(host, user, password)
    ids = m.list()[1]
    logging.debug('%d mails in box' % len(ids))
    #import pdb; pdb.set_trace()

    msg = None

    for id in ids[::-1]:
        num = id.split()[0]
        msg = '\n'.join(m.retr(num)[1])
        if anchor in msg:
            if delete:
                m.dele(num)
                m.quit()
            return msg
    m.quit()
    raise EmailNotFound()


#def clear_mailbox():
    #"""
    #Delete all mails from mailbox.
    #"""

    #m = connect()
    #ids = m.list()[1]
    #for id in ids[::-1]:
        #num = id.split()[0]
        #m.dele(num)
        #print 'Deleting %s' % num
    #m.quit()


#def dump_mailbox(server, username, password):
    #"""
    #Search for message contains acnhor text.
    #"""

    #m = connect(server, username, password)
    #ids = m.list()[1]
    #logging.debug('%d mails in box' % len(ids))

    #msg = None
    #for id in ids[::-1]:
        #num = id.split()[0]
        #msg = '\n'.join(m.retr(num)[1])
        #print 'Message #%s' % num
        #print msg
        #print '\n'
    #m.quit()


#if __name__ == '__main__':
    #logging.basicConfig(level=logging.DEBUG)
    ##print find_message('netlog')
    #dump_mailbox('pop3.rambler.ru', 'ujunahyqejar', 'wL1vCbix')
    ##clear_mailbox()
