from zope.interface import Interface

class IUsers(Interface):
    """ The user source """
    def get(userid=None, login=None):
        """ Return a user dictionary or None based on user id or login """

    def add(userid, login, cleartext_password=None, groups=None,
            encrypted_password=None):
        """ Add a user.  If ``groups`` is non-None, it must be a
        sequence of group names.  One of cleartext_password or
        encrypted_password needs to be supplied."""

    def remove(userid):
        """ Remove a user given a user id."""

    def change_password(userid, password):
        """ Change the password for a user given a user id and an
        (unencrypted) password."""

    def change_login(userid, login):
        """ Change the login name for a user given a user id and an
        new login name."""

    def add_user_to_group(userid, group):
        """ Add a user to a group given a user id and a group name. """

    def remove_user_from_group(userid, group):
        """ Remove a user from a group given a user id and a group name. """

    def member_of_group(userid, group):
        """ Return True if the user implied by the userid belongs to
        the group implied by the group name"""

    def delete_group(group):
        """ Remove any trace of group name from all user records """

    def users_in_group(group):
        """ Return a set of userids in the group """
    
