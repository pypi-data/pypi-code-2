"""Simple Eventbrite client for the HTTP-based API
"""
import datetime
import httplib
import logging
import urllib
from eventbrite import json_lib

# Input transformations
def _datetime_to_string(incoming_datetime):
    return incoming_datetime.strftime(eventbrite.EventbriteClient.eb_date_string)

def _string_to_datetime(incoming_string):
    return datetime.strptime(incoming_string, eventbrite.EventbriteClient.eb_date_string)

def _boolean_one_or_zero(is_true):
    return (is_true and '1') or '0'

def _boolean_true_or_false(is_true):
    return (is_true and 'true') or 'false'

def _comma_separated_list(input_list):
    return ",".join(input_list)

class EventbriteClient(object):
    """Client for Eventbrite's HTTP-based API"""
    eb_date_string = "%Y-%m-%d %H:%M:%S"
    eventbrite_api_endpoint = 'www.eventbrite.com'
    eventbrite_request_template = 'https://%(host)s/json/%(method)s?%(arguments)s'
    # these method aliases are for backwords compatibility with code
    # that was written before version 0.30 of this client was released
    #  !!WARNING: These calls are being depricated!!
    method_aliases = { 'copy_event': 'event_copy'
                     , 'get_event': 'event_get'
                     , 'get_user': 'user_get'
                     , 'list_event_attendees': 'event_list_attendees'
                     , 'list_event_discounts': 'event_list_discounts'
                     , 'list_organizer_events': 'event_list_organizer'
                     , 'list_user_events': 'user_list_events'
                     , 'list_user_organizers': 'user_list_organizers'
                     , 'list_user_tickets': 'user_list_tickets'
                     , 'list_user_venues': 'user_list_venues'
                     , 'new_discount': 'discount_new'
                     , 'new_event': 'event_new'
                     , 'new_organizer': 'organizer_new'
                     , 'new_ticket': 'ticket_new'
                     , 'new_user': 'user_new'
                     , 'new_venue': 'venue_new'
                     , 'search_events': 'event_search'
                     , 'update_discount': 'discount_update'
                     , 'update_event': 'event_update'
                     , 'update_organizer': 'organizer_update'
                     , 'update_payment': 'payment_update'
                     , 'update_ticket': 'ticket_update'
                     , 'update_user': 'user_update'
                     , 'update_venue': 'venue_update' }

    def __init__(self, tokens=None, user_key=None, password=None):
        """Initialize the client with the given app key and the user key"""
        logger = logging.getLogger(__name__)
        self._https_connection = httplib.HTTPSConnection(self.eventbrite_api_endpoint)
        self._auth_tokens = {}
        # set initialization tokens by name
        if type(tokens) == type(dict()):
            self._auth_tokens.update(tokens)
        # set initialization tokens by order
        else:
            self._auth_tokens['app_key'] = tokens
            # if we get three initialization tokens ( if "password" is set )
            #    use username+password combo for auth
            if password:
                self._auth_tokens['user'] = user_key
                self._auth_tokens['password'] = password
            # else use user_key for authentication
            else:
                self._auth_tokens['user_key'] = user_key

    # dynamic methods handler - call API methods on the local client object
    def __getattr__(self, method):
        # enable backwords compatibility with pre-0.30 API client code
        if method in self.method_aliases:
            method = self.method_aliases[method]
        def _call(*args, **kwargs):
            return self._request(method, args)
        return _call

    #def _execute_api_call(self, method, params):
    def _request(self, method='', params=dict()):
        """Execute an API call on Eventbrite using their HTTP-based API

        method - string  - the API method to call - see https://www.eventbrite.com/doc
        params - dict    - Arguments to pass along as method request parameters

        Returns: A dictionary with a return structure defined at http://developer.eventbrite.com/doc/
        """
        #unpack our params
        if type(params) == type(()) and len(params) > 0: 
            method_arguments = dict(params[0])
        else:
            method_arguments = {}

        # Add authentication tokens
        if 'access_token' not in self._auth_tokens:
            method_arguments.update(self._auth_tokens)

        # urlencode API method parameters
        encoded_params = urllib.urlencode(method_arguments)
        
        # construct our request url
        request_url = self.eventbrite_request_template % dict(host=self.eventbrite_api_endpoint, method=method, arguments=encoded_params)
        self.logger.debug("REQ - %s", request_url)

        # Send a GET request to Eventbrite
        # if using OAuth2.0 for authentication, set additional headers
        if 'access_token' in self._auth_tokens:
            self._https_connection.request('GET', request_url, None, {'Authorization': "Bearer " + self._auth_tokens['access_token']})
        else:
            self._https_connection.request('GET', request_url)

        # Read the JSON response 
        response_data = self._https_connection.getresponse().read()
        self.logger.debug("RES - %s", response_data)

        # decode our response
        response = json_lib.loads(response_data)
        if 'error' in response and 'error_message' in response['error'] :
            raise EnvironmentError( response['error']['error_message'] )
        return response

class EventbriteWidgets:
    @staticmethod
    def ticketWidget(evnt):
        return '<div style="width:100%; text-align:left;" ><iframe src="http://www.eventbrite.com/tickets-external?eid=' + str(evnt['id']) + '&ref=etckt" frameborder="0" height="192" width="100%" vspace="0" hspace="0" marginheight="5" marginwidth="5" scrolling="auto" allowtransparency="true"></iframe><div style="font-family:Helvetica, Arial; font-size:10px; padding:5px 0 5px; margin:2px; width:100%; text-align:left;" ><a style="color:#ddd; text-decoration:none;" target="_blank" href="http://www.eventbrite.com/r/etckt" >Online Ticketing</a><span style="color:#ddd;" > for </span><a style="color:#ddd; text-decoration:none;" target="_blank" href="http://www.eventbrite.com/event/' + str(evnt['id']) + '?ref=etckt" >' + str(evnt['title']) + '</a><span style="color:#ddd;" > powered by </span><a style="color:#ddd; text-decoration:none;" target="_blank" href="http://www.eventbrite.com?ref=etckt" >Eventbrite</a></div></div>'

    @staticmethod
    def registrationWidget(evnt):
        return '<div style="width:100%; text-align:left;" ><iframe src="http://www.eventbrite.com/event/' + str(evnt['id']) + '?ref=eweb" frameborder="0" height="1000" width="100%" vspace="0" hspace="0" marginheight="5" marginwidth="5" scrolling="auto" allowtransparency="true"></iframe><div style="font-family:Helvetica, Arial; font-size:10px; padding:5px 0 5px; margin:2px; width:100%; text-align:left;" ><a style="color:#ddd; text-decoration:none;" target="_blank" href="http://www.eventbrite.com/r/eweb" >Online Ticketing</a><span style="color:#ddd;" > for </span><a style="color:#ddd; text-decoration:none;" target="_blank" href="http://www.eventbrite.com/event/' + str(evnt['id']) + '?ref=eweb">' + str(evnt['title']) + '</a><span style="color:#ddd;"> powered by </span><a style="color:#ddd; text-decoration:none;" target="_blank" href="http://www.eventbrite.com?ref=eweb" >Eventbrite</a></div></div>'

    @staticmethod
    def calendarWidget(evnt):
        return '<div style="width:195px; text-align:center;" ><iframe src="http://www.eventbrite.com/calendar-widget?eid=' + str(evnt['id']) + '" frameborder="0" height="382" width="195" marginheight="0" marginwidth="0" scrolling="no" allowtransparency="true"></iframe><div style="font-family:Helvetica, Arial; font-size:10px; padding:5px 0 5px; margin:2px; width:195px; text-align:center;" ><a style="color:#ddd; text-decoration:none;" target="_blank" href="http://www.eventbrite.com/r/ecal">Online event registration</a><span style="color:#ddd;"> powered by </span><a style="color:#ddd; text-decoration:none;" target="_blank" href="http://www.eventbrite.com?ref=ecal">Eventbrite</a></div></div>'

    @staticmethod
    def countdownWidget(evnt):
        return '<div style="width:195px; text-align:center;"><iframe src="http://www.eventbrite.com/countdown-widget?eid=' + str(evnt['id']) + '" frameborder="0" height="479" width="195" marginheight="0" marginwidth="0" scrolling="no" allowtransparency="true"></iframe><div style="font-family:Helvetica, Arial; font-size:10px; padding:5px 0 5px; margin:2px; width:195px; text-align:center;" ><a style="color:#ddd; text-decoration:none;" target="_blank" href="http://www.eventbrite.com/r/ecount" >Online event registration</a><span style="color:#ddd;" > for </span><a style="color:#ddd; text-decoration:none;" target="_blank" href="http://www.eventbrite.com/event/' + str(evnt['id']) + '?ref=ecount">' + str(evnt['title']) + '</a></div></div>'

    @staticmethod
    def buttonWidget(evnt):
        return '<a href="http://www.eventbrite.com/event/' + str(evnt['id']) + '?ref=ebtn" target="_blank"><img border="0" src="http://www.eventbrite.com/registerbutton?eid=' + str(evnt['id']) + '" alt="Register for ' + str(evnt['title']) + ' on Eventbrite" /></a>'

    @staticmethod
    def linkWidget(evnt, text=False, color='#000000'):
        text = text if text else evnt['title'] 
        return '<a href="http://www.eventbrite.com/event/' + str(evnt['id']) + '?ref=elink" target="_blank" style="color:' + color + ';">' + text + '</a>'
