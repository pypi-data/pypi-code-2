from unittest import TestCase
import os

DEMO_USER = os.env.get("WEB2SMS_DEMO_USERNAME")
DEMO_PASSWORD = os.env.get("WEB2SMS_DEMO_PASSWORD")
DEMO_ACCOUNT = os.env.get("WEB2SMS_DEMO_ACCOUNT")
DEMO_MOBILE = os.env.get("WEB2SMS_DEMO_MOBILE")

class Web2smsTests(TestCase):

    def setUp(self):
        pass

    def _get_client(self, *params, **kwargs):
        from web2sms.api import Client
        return Client(*params, **kwargs)

    def ntest_client(self):
        c = self._get_client("user","pass","account","en")
        complex_request = c.get_request_xml("SendWEB2SMS",
                {'SID':'SessionId', 'SendToAll': "False",
                    'UserList':{}, 'MobileList':
                            {'Mobile_id':"694111111",'Mobile_id':"695111111"}
                })

        complex_request_out = """
        <?xml version="1.0" encoding="utf-8" ?>
        <REQUEST><ACTION Name="SendWEB2SMS" /><PARAMETERS>
        <PARAM Name="MobileList" Type="XML">
        <MOBILE_LIST><MOBILE_ID>695111111</MOBILE_ID></MOBILE_LIST></PARAM>
        <PARAM Name="UserList" Type="XML"><USER_LIST/></PARAM>
        <PARAM Name="SendToAll" Type="String" Value="False"/>
        <PARAM Name="SID" Type="String" Value="SessionId"/>
        </PARAMETERS>
        </REQUEST>
        """
        # clear spaces making easier to compare
        self.assertEqual(complex_request.replace(" ",""),complex_request_out.replace("\n","").replace(" ",""))

    def test_send_sms(self):
        c = self._get_client(DEMO_USER,DEMO_PASSWORD,DEMO_ACCOUNT,"EN")
        c.send_sms("test sms", [DEMO_MOBILE])

