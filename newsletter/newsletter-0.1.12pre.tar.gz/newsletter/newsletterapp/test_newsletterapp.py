"""

Testing the newsletterapp

    >>> import newsletterapp
    >>> import os, shutil

Temp directory creation.

    >>> TMP_DIR = "/tmp/newsletterapp_test_tmp"
    >>> if os.path.exists(TMP_DIR):
    ...     shutil.rmtree(TMP_DIR)
    >>> os.mkdir(TMP_DIR)
    >>> os.mkdir(os.path.join(TMP_DIR, 'db'))



    >>> cfg = {'/': {'tools.staticdir.root': os.path.join(os.path.abspath('.'), 'static')},
    ...           '/admin': {'tools.basic_auth.encrypt': newsletterapp.encrypt_pwd,
    ...                      'tools.basic_auth.on': True,
    ...                      'tools.basic_auth.realm': 'Please Enter User/Password',
    ...                      'tools.basic_auth.users': {'admin': newsletterapp.encrypt_pwd("admin")}},
    ...           '/css': {'tools.staticdir.dir': 'css', 'tools.staticdir.on': True},
    ...           '/images': {'tools.staticdir.dir': 'images', 'tools.staticdir.on': True},
    ...           '/js': {'tools.staticdir.dir': 'js', 'tools.staticdir.on': True},
    ...           '/tiny_mce': {'tools.staticdir.dir': 'tiny_mce', 'tools.staticdir.on': True},
    ...           'newsletter': {'base_url': "http://localhost:9999/",
    ...                          'db_dir': os.path.join(TMP_DIR, 'db'),
    ...                          'smtp_host': 'localhost',
    ...                          'smtp_password': '',
    ...                          'smtp_sleep_between_sends': 1.0,
    ...                          'smtp_username': '',
    ...                          'static_dir': 'static'}}


    >>> wnl = newsletterapp.WebNewsletter()
    >>> wnl.load(cfg)

Mock out the sendmail function.

    >>> _sendmail_log = []
    >>> def sendmail_log(*args, **kwargs):
    ...     _sendmail_log.append((args, kwargs))
    >>> newsletterapp.sendmail = sendmail_log

    >>> newsletterapp.sendmail("blabla", ok = True)
    >>> _sendmail_log
    [(('blabla',), {'ok': True})]
    >>> _sendmail_log = []


Subscribe a user.

    >>> wnl.subscribe("joe@example.com", "Joe Bloggs", wrap_it = False)
    'thank you for subscribing.  We sent you an email to confirm.\\n'

See if confirmation email is send.
    >>> _sendmail_log
    [((None, 'joe@example.com', 'newsletter signup for great justice', 'Hi, \\n\\nsomeone has entered your email address subscribing to a newsletter.  \\nPlease click here if you would like to confirm:\\nhttp://localhost:9999/confirm_subscribe/joe@example.com/...\\n', 'localhost', '', ''), {})]

    >>> "confirm_subscribe" in _sendmail_log[0][0][3]
    True

Confirm the email with the link in the email.

    >>> confirm_id = _sendmail_log[0][0][3].split("joe@example.com")[-1][1:-1]

    >>> len(confirm_id)
    36

    >>> wnl.confirm_subscribe('joe@example.com', confirm_id, wrap_it = False)
    'thank you for confirming your subscription\\n'


Admin section.


Create a newsletter send.
    >>> wnl.admin.create("", "this is a subject", "this is the body of the email for %FULL_NAME% unsublink:%base_url%:  secret:%secret%: end.")
    "...newsletter send created..."


Add subscribers to send.

  Get the send id.
    >>> send_id = wnl.admin._ns.newsletter_send_ids()[0]
  
    >>> wnl.admin.add_all_subscribers_to_send(send_id)
    "...Added all subscribers to send..."


Send the newsletter send.

    >>> wnl.admin.send(send_id)
    u'sent...'

Make sure that it sent the email out ok.
    >>> _sendmail_log[1][0][1]
    'joe@example.com'
    >>> _sendmail_log[1][0][2]
    'this is a subject'
    >>> _sendmail_log[1][0][3]
    'this is the body of the email for Joe Bloggs unsublink:http://localhost:9999/:  secret:...: end.'



"""



if __name__ == "__main__":
    def _test():
        import doctest
        doctest.testmod(optionflags=doctest.ELLIPSIS)
    _test()


