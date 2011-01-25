# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import logging

import grok
import zope.app.appsetup.product
import zope.app.container.interfaces
import zope.component
import zope.sendmail.interfaces

import gocept.lms.interfaces


log = logging.getLogger(__name__)


# XXX we actually would like to get the texts out of here

# When a client gets disabled, we send a mail:
MAIL_DISABLED = """\
To: %(client_name)s <%(client_email)s>
From: Link Monitoring Server <%(lms_email)s>
Subject: lms disabled notifications for client id %(client_id)s

Dear %(client_name)s

Your site is registered with our Link Monitoring Server (lms) at %(lms_name)s.

The lms will not send you any further notifications, because it could not send
out notifications for several times. To enable notifications again, visit your
Link Management configuration (from CMFLinkChecker 1.9.2 on).

Information stored on the lms:

    Client-Id   : %(client_id)s
    Callback URL: %(client_callback)s
    Contact     : %(client_name)s <%(client_email)s>

"""

# When a client is registered we send this mail:
MAIL_REGISTRATION = """\
To: %(client_name)s <%(client_email)s>
From: Link Monitoring Server <%(lms_email)s>
Subject: Registration of client id "%(client_id)s"

Dear %(client_name)s

Your client id "%(client_id)s" has been registered with the lms %(lms_name)s.

Thanks for trying out CMFLinkChecker and the Link Monitoring Server. If you
have not done so already, please subscribe to the CMFLinkChecker and lms
mailing list at linkchecker@lists.gocept.com (with subscribe as subject).

If you have any problems using CMFLinkChecker feel free to contact us at
mail@gocept.com or the CMFLinkChecker mailing list.

Information stored on the lms:

    Client-Id   : %(client_id)s
    Password    : %(client_password)s
    Callback URL: %(client_callback)s
    Contact     : %(client_name)s <%(client_email)s>

The address of the lms is <%(lms_address)s>.

"""

# When a client is registered we send this mail:
MAIL_UNREGISTRATION = """\
To: %(client_name)s <%(client_email)s>
From: Link Monitoring Server <%(lms_email)s>
Subject: Removal of client id "%(client_id)s"

Dear %(client_name)s

Your client id "%(client_id)s" was registered with the lms
%(lms_name)s. Due to a request for removal, it was now removed from
our database again.

We thank you for using CMFLinkChecker and the Link Monitoring Server and hope
to hear from you in the future again.

If you have further questions feel free to contact us at mail@gocept.com or the
CMFLinkChecker mailing list.

Information removed from the lms:

    Client-Id   : %(client_id)s
    Callback URL: %(client_callback)s
    Contact     : %(client_name)s <%(client_email)s>

Please note that you still might receive notifications or link checks
for another few hours.

"""


def send_mail_to_client(client, body_template):
    mailer = zope.component.queryUtility(
        zope.sendmail.interfaces.IMailDelivery)
    if mailer is None:
        log.error("Could not send mail because not mail delivery utility "
                  "is registered.")
        return

    config = zope.app.appsetup.product.getProductConfiguration('gocept.lms')
    body = body_template % dict(
        client_id=client.id,
        client_password=client.password,
        client_callback=client.callback,
        client_name=client.contact_name,
        client_email=client.contact_email,
        lms_email=config['lms-email-address'],
        lms_name=config['lms-name'],
        lms_address=config['lms-xmlrpc-address'],
    )

    rcpt = [client.contact_email]
    cc = config.get('lms-send-cc-to')
    if cc:
        rcpt.extend(cc.split())

    mailer.send(config['lms-email-address'], rcpt, body)


@grok.subscribe(
    gocept.lms.interfaces.IClient,
    zope.app.container.interfaces.IObjectAddedEvent)
def on_registration(client, event):
    send_mail_to_client(client, MAIL_REGISTRATION)
