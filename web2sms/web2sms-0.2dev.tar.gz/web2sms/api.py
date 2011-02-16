import httplib2
import re

from xml.dom import minidom as dom
from BeautifulSoup import BeautifulStoneSoup as BS

first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')
def uncamel(name):
    """
    Converts CamelCase string to non camel case (using underscore to seperate words)

    http://stackoverflow.com/questions/1175208/does-the-python-standard-library-have-function-to-convert-camelcase-to-camel-case/1176023#1176023
    """

    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()


def login_required(method):
    """
    Login class method decorator
    """
    def wrapper(self, *args, **kwargs):
        if not self.logged_id():
            self.login()

        return method(self, *args, **kwargs)

    return wrapper


class Web2SMSException(Exception):
    pass

class Web2SMSClient(object):
    """
    Client represents the api wrapper class.
    """

    api_url = "http://web2sms.cosmote.gr/web2sms/DCM"

    def __init__(self, username, password, account, language='EN'):
        self.username = username
        self.password = password
        self.account = account
        self.language = language

        # Session params
        self.session_id = None
        self.user_id = None
        self.cookie = None

        # http client
        self.client = None

        # Client status params
        self.last_status = None
        self.last_error_message = None
        self.last_error_code = None

        self.init_client()

    def logged_id(self):
        return self.session_id and self.user_id

    def login(self):
        self.make_request("POSTLogin", {'U':self.username, 'P':self.password, 'A': 'WEB2SMS', 'ACCOUNT': self.account, 'L': self.language})

    def make_request(self, action, data, method="POST"):
        """
        Prepare xml, session
        """
        headers = {'content-type':'application/xml'}

        if self.cookie:
            # set the cookie to the last response set-cookie value
            headers.update({'Cookie':self.cookie})

        if self.session_id:
            data.update({'SID': self.session_id})

        xml = self.get_request_xml(action, data)

        #TODO: handle GET parameters
        url = self.api_url

        # the actual http request
        resp, content = self.make_http_request(url, method, xml, headers)

        doc = self.parse_response(resp, content)

        # dynamic method execution to handle special actions (like POSTLogin)
        custom_parse = getattr(self, "parse_%s" % action, None)
        if custom_parse:
            return custom_parse(resp, doc)

        return doc

    def make_http_request(self, url, method, body, headers):
        resp, content = self.client.request(url, method, body=body, headers=headers)
        return resp, content

    def parse_response_for_errors(self, doc):
        self.last_error_message = None
        self.last_error_code = None

        status = doc.find("status")
        self.last_status = status.text

        if self.last_status == "0":
            self.last_error_message = doc.find("error").find("message").text.encode("utf-8")
            self.last_error_code = doc.find("error").find("code").text.encode("utf-8")
            raise Exception("[%s] %s" % (self.last_error_code, self.last_error_message))

    def parse_POSTLogin(self, resp_headers, doc):
        self.user_id = doc.find("session").find("user_id").text
        self.session_id = doc.find("session").find("sid").text
        self.cookie = resp_headers['set-cookie']

    def parse_response(self, resp_headers, content):
        doc = BS(content, fromEncoding="utf-8")
        self.parse_response_for_errors(doc)
        return doc

    def init_client(self):
        self.client = httplib2.Http()

    @login_required
    def send_sms(self, text, mobile_list, get_status=True, validity=2, date=None):
        data = {}
        data['RequestStatusReport'] = "False"
        if get_status:
            data['RequestStatusReport'] = "True"

        data['Validity'] = str(validity)
        data['SendToAll'] = "False"
        data['SMS'] = str(text)

        if date:
            raise NotImplemented("Scheduled date is not supported yet.")

        data['UserList'] = {}
        data['GroupList'] = {}
        data['MobileList'] = dict([('MOBILE_ID', m) for m in mobile_list])

        self.make_request("SendWEB2SMS", data)

    @login_required
    def get_status(self):
        raise NotImplemented("Delivery status is not implemented yet")

    @login_required
    def delete_sms(self):
        raise NotImplemented("SMS deletion is not supported")

    def get_request_xml(self, method, params_dict):
        """
        Create a valid xml response

        :method parameter: refers to the api action to be executed (e.g. POSTLogin)
        :params_dict: refers to the action parameters
        """
        doc = dom.Document()
        request = doc.createElement("REQUEST")
        action = doc.createElement("ACTION")
        params = doc.createElement("PARAMETERS")

        action.setAttribute("Name", method)
        for param_name, param_value in list(params_dict.items()):

            param = doc.createElement("PARAM")
            param.setAttribute("Name", param_name)

            param_type = None
            if issubclass(type(param_value), basestring):
                param_type = "String"
                param.setAttribute("Value", param_value)

            if type(param_value) in [dict]:
                param_type = "XML"
                params_list = doc.createElement(uncamel(param_name).upper())
                for param_item_name, param_item_value in list(param_value.items()):
                    item = doc.createElement(param_item_name.upper().replace(" ","_"))
                    data = doc.createTextNode(param_item_value)
                    item.appendChild(data)

                    params_list.appendChild(item)
                param.appendChild(params_list)
            param.setAttribute("Type", param_type)
            params.appendChild(param)

        request.appendChild(action)
        request.appendChild(params)
        doc.appendChild(request)
        return doc.toxml(encoding="utf-8")
