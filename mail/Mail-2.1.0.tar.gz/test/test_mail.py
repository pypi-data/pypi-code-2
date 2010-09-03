#!/usr/bin/env python

"""\
Test program to send mail to recipients.

Note: If you don't have the ``sendmail`` program on your computer you'll need
to install Postfix or similar and choose ``Internet Site`` during the
installation.

This will test:

1. Construction of plain text emails
2. Construction of multi-part emails: html and attachment
3. Construction of multi-part emails: plain text and attachment

All sent by sendmail

Then it will test:

4. Sending an email with two CCs by sendmail then SMTP
5. Sending an email with two BCCs by sendmail then SMTP
6. Sending an email with a CC and BCC 

It is assumed that if the last four tests work then the first three tests sent
by SMTP instead of sendmail would also have worked.

These tests result in 18 emails being sent and recieved (8 to the first address
and 5 each to the other two you give). If they arrive you can be confident
about:

* ``send_sendmail()``
* ``send_smtp()``
* ``plain()``
* ``multi()`` and ``part()``

The ``prepare()`` helper is used by ``multi()`` and ``plain()`` so is tested
implicitly by their use.

.. caution ::

   Make sure you specify different email addresses which end up in different
   mailboxes, otherwise there's a chance some of the mail software en route might
   be clever and only deliver one copy of the message, leading to less emails
   being recieved than you'd anticipate.

.. tip ::

   You can customise the subject to make the sending of emails easier by
   changing the ``subject`` variable. For verbose output choose ``verbose=True``.

.. tip ::

   If you run these tests a lot it becomes tedious typing the values in each
   time. Instead write them to a text file once and paste them all onto the
   command line in one go each time you want to run them.

"""

#
# Config
#

verbose = False
subject = 'Mail Test'

#
# Start
#


import sys; sys.path.append('../')
import getpass
import mail.helper

address = raw_input('Email address to recieve tests: ')
ccaddress = raw_input('Email another address to recieve tests: ')
bccaddress = raw_input('Email another address to recieve tests: ')
smtp = raw_input('SMTP Server: ')
username = raw_input('Username: ')
password = getpass.getpass()
sendmail = raw_input('Path to sendmail: ')

message_1 = """Hi,

This is from the test_build_email() function.
It is plain text.
It is sent by sendmail to %s.
The To: recipient doesn't have a name.
The From name should be James Gardner 
The From address should be address %s

James"""%(address, address)

message_2 = """Hi,

This is from the test_build_email() function.
It is a plain text message with a JPEG attachment.
It is sent by sendmail to %s.
The To: recipient should show up as "Test Address".
The From name should be James Gardner 
The From address should be address %s

James"""%(address, address)

message_3 = """Hi,

This is from the test_build_email() function.
It is an <b>HTML</b> message with a JPEG attachment.
It is sent by sendmail to %s.
The To: recipient doesn't have a name.
The From name should be James Gardner 
The From address should be address %s

James"""%(address, address)

message_to_and_cc = """Hi,

This is from the test_send_email() function.
It is an <b>HTML</b> message with a JPEG attachment.
The From name should be James Gardner 
The From address should be address %s

This message is sent to:
%s

It is CCd to:
%s <%s>
%s

James"""%(address, address, 'CC_Address', ccaddress, ccaddress)

message_to_and_bcc = """Hi,

This is from the test_send_email() function.
It is an <b>HTML</b> message with a JPEG attachment.
The From name should be James Gardner 
The From address should be address %s

This message is sent to:
%s

It is BCCd to these (they should not appear in the message)
%s <%s>
%s

James"""%(address, address, 'BCC_Address', bccaddress, bccaddress)

message_6 = """Hi,

This is from the test_to_cc_bcc() function.
It is plain text.
The To, Cc and Bcc fields are all used and an attachment is sent.

James"""

def test_build_email():
    
    plain_text_email = mail.helper.plain(
        message_1,
        from_name = 'James Gardner',
        from_email = address,
        to=[address], 
        subject=subject+' 1. (x1)',
    )
    multi_plain_email = mail.helper.multi(
        parts = [
            mail.helper.part(message_2, content_type="text/plain", attach=False),
            mail.helper.part(filename='attachment.jpg'),
        ],
        from_name = 'James Gardner',
        from_email = address,
        to=['Test Address <'+address+'>'], 
        subject=subject+' 2. (x1)',
    )
    multi_html_email = mail.helper.multi(
        parts = [
            # One part has to have attach=False
            mail.helper.part(message_3, content_type="text/html", attach=False),
            mail.helper.part(filename='attachment.jpg'),
        ],
        from_name = 'James Gardner',
        from_email = address,
        to=[address], 
        subject=subject+' 3. (x1)',
    )
    for email in [plain_text_email, multi_plain_email, multi_html_email]:
        mail.helper.send_sendmail(
            email,
            sendmail=sendmail,
            verbose=verbose,
        )

def test_send_email():
    cc_email = mail.helper.multi(
        parts = [
            # One part has to have attach=False
            mail.helper.part(message_to_and_cc, content_type="text/html", attach=False),
            mail.helper.part(filename='attachment.jpg'),
        ],
        from_name = 'James Gardner',
        from_email = address,
        to=[address], 
        cc=['CC_Address <%s>'%ccaddress, bccaddress],
        subject=subject+' 4. (x6)',
    )
    mail.helper.send_smtp(
        cc_email,
        verbose=verbose,
        host=smtp,
        username=username,
        password=password,
        starttls=True,
    )
    mail.helper.send_sendmail(
        cc_email,
        sendmail=sendmail,
        verbose=verbose,
    )
    bcc_email = mail.helper.multi(
        parts = [
            # One part has to have attach=False
            mail.helper.part(message_to_and_bcc, content_type="text/html", attach=False),
            mail.helper.part(filename='attachment.jpg'),
        ],
        from_name = 'James Gardner',
        from_email = address,
        to=[address], 
        bcc=['BCC_Address <%s>'%ccaddress, bccaddress],
        subject=subject+' 5. (x6)',
    )
    mail.helper.send_smtp(
        bcc_email,
        verbose=verbose,
        host=smtp,
        username=username,
        password=password,
        starttls=True,
    )
    mail.helper.send_sendmail(
        bcc_email,
        sendmail=sendmail,
        verbose=verbose
    )

def test_to_cc_bcc():
    mail.helper.send_smtp(
        mail.helper.multi(
            parts = [
                mail.helper.part(message_6, content_type="text/plain", attach=False),
                mail.helper.part(filename='attachment.jpg'),
            ],
            from_name = 'James Gardner',
            from_email = address,
            to=['Test Address <'+address+'>'], 
            cc=['Test Address CC <'+ccaddress+'>'], 
            bcc=['Test Address BCC <'+bccaddress+'>'], 
            subject=subject+' 6. (x3)',
        ),
        host=smtp,
        username=username,
        password=password,
        verbose=verbose,
        starttls=True
    ) 

if __name__ == '__main__':
    test_build_email()
    test_send_email()
    test_to_cc_bcc()

