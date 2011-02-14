import re

from socialtext.resources.base import Resource, Manager, get_id
from socialtext.urls import make_data_url

class Signal(Resource):
    def __repr__(self):
        return "<Signal: %s>" % self.signal_id

    def delete(self):
        """
        Delete this signal.
        
        .. warning::
            This will permanently delete the Signal from the database. Only Business Administrators
            can delete signals.
        """
        return self.manager.delete(self)

    def get_id(self):
        """
        Get the ID that represents this signal. The signal_id attribute is required.

        :rtype: string
        """
        assert hasattr(self, 'signal_id'), "The signal does not have a 'signal_id' attribute."
        return self.signal_id

    def get_mentioned_user_ids(self):
        """
        Get a list of User IDs that are mentioned in the Signal.

        :rtype: list of string User IDs
        """
        regex = re.compile(r'{user: (\d+)}')
        user_ids = []
        for m in regex.finditer(self.body):
            user_ids.append(m.groups(1)[0])
        return user_ids

    def is_user_mentioned(self, user_id):
        """
        Determines if a user with the provided user_id is mentioned
        in this signal's body.

        :rtype: boolean if the user_id is mentioned
        """
        if self.body.find("{user: %s}" % user_id) >= 0:
            return True
        return False
        
class SignalManager(Manager):
    """
    Manage :class:`Signal` resources.
    """
    resource_class = Signal
    
    def list(self):
        """
        Get a list of all signals.
        
        :rtype: list of :class:`Signal`
        """
        return self._list(make_data_url("signals"))
        
    def get(self, signal):
        """
        Get a specific signal.
        
        :param signal: The :class:`Signal` (or ID of the Signal) to get
        :rtype: :class:`Signal`
        """
        url = make_data_url("signal", arguments_dict={ "signal_id" : get_id(signal) })
        return self._get(url)
        
    def create(self, body, in_reply_to=None, group_ids=[]):
        """
        Create a signal in Socialtext.
        
        :param body: The body of the signal.
        :param in_reply_to: The ID of the signal to reply to.
        :param group_ids: A list of Group ID's to post the signal to. Otherwise,
                          the sgianl will be posted to the user's primary account.
        
        :rtype: :class:`Signal`
        """
        signal = { "signal" : body }
        if in_reply_to:
            signal["in_reply_to"] = { "signal_id" : in_reply_to }
        if group_ids:
            signal["group_ids"] = group_ids
        url = make_data_url("signals")
        resp, body = self.api.client.post(url, body=signal)
        signal_id = resp.get('x-signal-id', None)
        return self.get(signal_id)
        
    def delete(self, signal):
        """
        Delete a signal.
        
        .. warning::
            This will permanently delete the Signal from the database. Only Business Administrators
            can delete signals.

        :param signal: The :class:`Signal` (or ID of the Signal) to delete
        """
        url = make_data_url("signal", arguments_dict={ "signal_id" : get_id(signal) })
        self._delete(url)