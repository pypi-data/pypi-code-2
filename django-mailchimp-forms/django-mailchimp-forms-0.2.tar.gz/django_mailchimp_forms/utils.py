import chimpy
from django.conf import settings
from django_mailchimp_forms.models import MailingList

MAILCHIMP_API_KEY = getattr(settings, 'MAILCHIMP_API_KEY', None)
MAILCHIMP_LIST_NAME = getattr(settings, 'MAILCHIMP_LIST_NAME', None)
SECURE = True

connection = None
default_list = None

def require_connection(fn):
    def ret_fn(*args, **kwargs):
        global connection
        connection = connection or chimpy.Connection(apikey=MAILCHIMP_API_KEY,
                                                     secure=SECURE)
        global default_list
        if not default_list:
            for mlist in connection.lists():
                if mlist['name'] == MAILCHIMP_LIST_NAME:
                    default_list = mlist['id']
                    break
        return fn(*args, **kwargs)
    return ret_fn

@require_connection
def register_user(user):
    try:
        if user.mailinglist.confirmed:
            return
    except MailingList.DoesNotExist, e:
        pass
    global connection
    global default_list
    merge_vars = {'FNAME' : user.first_name,
                  'LNAME' : user.last_name,
                  'INTERESTS' : '',}
    ml = MailingList.objects.get_or_create(user=user)[0]
    connection.list_subscribe(default_list, user.email, merge_vars=merge_vars,
                              email_type='html', double_optin=False)
    ml.confirmed = True
    ml.save()

@require_connection
def unregister_user(user):
    try:
        if not user.mailinglist.confirmed:
            user.mailinglist.delete()
            return
    except MailingList.DoesNotExist, e:
        return
    global connection
    global default_list
    connection.list_unsubscribe(default_list, user.email, delete_member=True,
                                send_goodbye=True, send_notify=True)
    user.mailinglist.delete()

@require_connection
def retry_unconfirmed_registrations():
    global connection
    global default_list
    for ml in MailingList.objects.filter(confirmed=False):
        register_user(ml.user)
