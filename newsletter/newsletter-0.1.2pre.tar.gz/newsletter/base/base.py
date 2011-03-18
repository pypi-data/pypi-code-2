"""

The interface for the Newsletter.

"""


"""

* actions
  - create, update, delete newsletters.
  - select people to send email to.
    - everyone on the list.
    - select categories of people.
  - unsubscribe through url.  Given an email, and a secret code.
  - unsubscribe through admin section.  Given an email.
  - subscription form
    - 
  - confirmation email, for double opt in.  Sends them a url with a secret to click on.

"""

import uuid

class Newsletter(object):
    """

    >>> n = Newsletter()
    >>> n.subscribers()
    []

    >>> n.subscribe("bla@example.com")
    True
    >>> n.subscribers(unconfirmed = True)
    [{'secret': '...', 'email': 'bla@example.com', 'subscribed': False}]

    We add the same subscriber again, and we should not overwrite details.
    >>> n.subscribe("bla@example.com")
    True
    >>> n.subscribers(unconfirmed = True)
    [{'secret': '...', 'email': 'bla@example.com', 'subscribed': False}]




    >>> secret = n.subscribers(unconfirmed = True)[0]['secret']
    >>> n.confirm_subscribe(email = 'bla@example.com', secret = secret)
    True

    >>> n.subscribers()
    [{'secret': '...', 'email': 'bla@example.com', 'subscribed': True}]


    >>> n.unsubscribe(email = 'bla@example.com')
    True

    Let us unsubscribe someone who is not subscribed.  Returns True anyway,
      because otherwise it could leak subscribers.
    >>> n.unsubscribe(email = 'notsubbed@example.com')
    True
    

    >>> n.confirm_unsubscribe(email = 'bla@example.com', secret = secret)
    True

    >>> n.subscribers()
    []

    >>> n.subscribers(unconfirmed = True)
    []
    """

    def __init__(self):
        """
        """
        # keyed by unique id, valued by a dict of info.
        self._subscribers = {}
    

    def subscribe(self, email, info = {}):
        """
        """
        user = {"email": email}
        user.update(info)
        user['secret'] = self._make_secret()
        user['subscribed'] = False

        u = [u for u in self._subscribers.values() if u['email'] == email]
        if u:
            # If we are already subscribed, do not overwrite their details.
            pass
        else:
            u_id = self._make_uid()
            self._subscribers[u_id] = user
            # TODO: send subscribe confirmation email

        return True


    def confirm_subscribe(self, email, secret):
        """
        """
        # get the user with this email and secret.
        u = [u for u in self._subscribers.values() if u['email'] == email and u['secret'] == secret]
        if u:
            u[0]['subscribed'] = True
            return True
        else:
            return False



    def unsubscribe(self, email):
        """
        """
        # unsubscribes have to use confirm_unsubscribe afterwards.

        u = [u for u in self._subscribers.items() if u[1]['email'] == email]
        if u:
            # TODO: send unsubscribe email
            return True
        else:
            return True



    def confirm_unsubscribe(self, email, secret):
        """
        """
        # get the user with this email.
        u = [u for u in self._subscribers.items() if u[1]['email'] == email and u[1]['secret'] == secret]
        if u:
            u[0][1]['subscribed'] = False
            uid = u[0][0]
            del self._subscribers[uid]
            return True
        else:
            return False

    def subscribers(self, unconfirmed = False):
        """
        """
        if unconfirmed:
            return [u for u in self._subscribers.values() if u['subscribed'] == False]
        else:
            return [u for u in self._subscribers.values() if u['subscribed'] == True]

    def _make_uid(self):
        return str(uuid.uuid4())

    def _make_secret(self):
        return str(uuid.uuid4())





class NewsletterSend(object):
    """
    """

    def create(self, subject, body):
        """
        """

    def update(self, subject, body):
        """
        """

    def delete(self):
        """
        """

    def send(self):
        """
        """

    def add_users(self, users):
        """ users - the users to be sent emails.
            [{"email":"", "full_name":"", "user_id": ""}, ...]
        """



if __name__ == "__main__":
    import doctest
    doctest.testmod(optionflags = doctest.ELLIPSIS)
    
