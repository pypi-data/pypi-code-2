
"""
    Hack the realex code out of my legacy application
"""

import string

from random import randint
import time
import httplib
from hashlib import sha1
import logging

from xml.etree.ElementTree import tostring, Element, fromstring

from zope.schema import ValidationError

logger = logging.getLogger('getpaid.realex')

class InvalidParameter(ValidationError):
    """Invalid parameter to Credit Card Processing Module"""

class CommunicationsError(ValidationError):
    """Unable to communicate with the Credit Card Authority"""

def TElement(name, **kwargs):
    """An element that can contain text"""
    text = None
    if 'text' in kwargs:
        text = kwargs['text']
        del kwargs['text']
    rv = Element(name, kwargs)
    if text:
        rv.text = text
    return rv

HOSTNAME='epage.payandshop.com'
URL='/epage-remote.cgi'

# Message used for test purposes
TEST_RESPONSE_SUCCESS = {
    'result': 0,
    'message': 'SUCCESS',
    'authcode': '999999',
    'orderid': '9876543-12345',
    'pasref': '8888888',
    }

TEST_RESPONSE_FAILED = {
    'result': 1,
    'message': 'FAILED',
    'authcode': '999999',
    'orderid': '9876543-12345',
    'pasref': '8888888',
    }
TEST_RESPONSE = TEST_RESPONSE_SUCCESS


class Realex(object):
    """Realex Credit Card Processing Utility. 
    """

    MerchantID =  None
    Secret = None
    TESTING = None
    chargeDescription = None
    SubAccount = None
    Currency = None

    def __init__(self, MerchantID, Secret, Testing=False, SubAccount=u'internet', chargeDescription=None, Currency='EUR'):
        self.MerchantID = MerchantID
        self.Secret = Secret
        self.TESTING = Testing
        self.chargeDescription = chargeDescription
        self.SubAccount = SubAccount
        self.Currency = Currency or 'EUR'

    def _stripToDigits(self, num):
        """Sometimes get a number such as 1234-1234-1234-1234 or 1234 1243.
        Strip out non digits"""
        return ''.join([d for d in num if d in string.digits])

    def _SHA1Digest(self, s):
        """Pass in a string of timestamp. merchant_id, order_id, amount, currency"""
        d = sha1(s)
        d = sha1(d.hexdigest()+'.'+self.Secret)
        return d.hexdigest()

    def _cleanOrderId(self,orderid):
        """Remove invalid characters from orderid"""
        rv = []
        for c in orderid:
            if c not in string.digits and c.lower() not in string.lowercase and c not in ['-', '_']:
                rv.append('_')
            else:
                rv.append(c)
        return ''.join(rv)
       
    def _makeSimpleAuthRequest(self, 
            orderid,   # Our own order reference
            amount,    # Amount of the txn in cent
            card_number,  # Card number
            card_expdate, # Expyr date MMYY
            card_chname,  # Card Holder Name
            card_type,    # Card type - must be VISA, MC, AMEX, LASER
            card_cvn,     # Card Validation Number - Required if VISA
            prodid=None,  # Product id is supplied
            chargeDescription=None,  # Description of Charge
            custipaddress=None,  # Customer IP Address
        ):
        t = tuple(time.localtime()[:6])
        timestamp="%s%02.2d%02.2d%02.2d%02.2d%02.2d"%t

        # Build a python dictionary, and then convert that to XML
        rv = Element('request', timestamp=timestamp, type='auth')
        rv.append(TElement('merchantid', text = self.MerchantID))
        rv.append(TElement('account', text=self.SubAccount))
        rv.append(TElement('orderid', text=orderid))

        amount = str(amount)
        if amount.find('.') != -1:
            raise InvalidParameter('Currency Amount %s should be an integer value of cent' % amount)
        rv.append(TElement('amount', currency=self.Currency, text=amount))
        card = Element('card')
        rv.append(card)

        # Strip non-digits
        if card_cvn:
            card_cvn = self._stripToDigits(card_cvn)

        if len(card_number) < 15 or len(card_number) > 19:
            raise InvalidParameter('Card number must be 15-19 digits')
        card.append(TElement('number', text=card_number))
        card.append(TElement('expdate', text=card_expdate))
        card.append(TElement('chname', text=card_chname))
        card_type = card_type.upper()
        if card_type == 'MASTERCARD':
            card_type='MC'
        if card_type not in ['LASER', 'VISA', 'MC']:
            raise InvalidParameter('Credit Card %s Invalid' % card_type)
        card.append(TElement('type', text=card_type))

        rv.append(Element('autosettle', flag='1'))
        if card_cvn and card_cvn.strip():
            cvn = Element('cvn' )
            card.append(cvn)
            cvn.append(TElement('number', text=card_cvn))
            cvn.append(TElement('presind', text='1'))

        if prodid or custipaddress:
            tssinfo = Element('tssinfo')
            rv.append(tssinfo)
            if prodid:
                tssinfo.append(TElement('prodid', text=str(prodid)))
            if custipaddress:
                tssinfo.append(TElement('custipaddress', text=str(custipaddress)))

        if chargeDescription is None and self.chargeDescription:
            chargeDescription = self.chargeDescription

        if chargeDescription:
            narrative = TElement('narrative')
            rv.append(narrative)
            narrative.append(TElement('chargedescription', text=str(chargeDescription)))

        digest = self._SHA1Digest(timestamp + '.'+self.MerchantID + '.'+orderid + '.'+amount + '.'+self.Currency+'.'+card_number)
        rv.append(TElement('sha1hash', text=digest))
        return tostring(rv)

    def Authorise(self, orderid, amount, card_number, card_expdate,
        card_chname, card_type, card_cvn=None, 
        prodid=None, chargeDescription=None, custipaddress=None):
        """Make a payment via REALEX """


        # I add a random number ot the orderid because realex records the
        # order reference even when it rejects the order - therefore I cannot
        # get it through later
        r = randint(1000, 9999)
        orderid='%s-%s' %(self._cleanOrderId(orderid), r)
        card_number = self._stripToDigits(card_number)

        xml = self._makeSimpleAuthRequest(orderid, amount, card_number,
            card_expdate, card_chname, card_type, card_cvn,
            prodid=prodid, chargeDescription=chargeDescription,
            custipaddress=custipaddress)

        if self.TESTING:
            logger.info("Credit Card Request (TEST MODE), order %s, amount %s, " \
                "card_number %s, card_expdate %s, card_chname %s, card_type %s, prodid %s, narrative %s",
                orderid, amount, card_number, card_expdate, card_chname, card_type, prodid, chargeDescription)
            logger.info(xml)
            return TEST_RESPONSE

        logger.info('About to make Credit Card Request, order %s, prodid %s, narrative %s',
            orderid, prodid, chargeDescription)

        rv = self._mkRequest(xml, 'Authorise')

        if rv['result'] != 0:
            request = self._starNumber(card_number, xml)
            logger.error('Credit Card Request Failed (%s), request: %s, result: %s',
                rv['result'], request, str(rv))
        else:
            logger.info('Credit Card Request Succeeded, order %s, authcode %s, pasref %s',
                rv.get('orderid'), rv.get('authcode'), rv.get('pasref'))

        return {
            'result': rv.get('result'),          # 0 for success
            'message': rv.get('message'),        # text response code
            'orderid': rv.get('orderid'),        # Our reference
            'authcode': rv.get('authcode'),      # Reference returned from Bank
            'pasref': rv.get('pasref'),          # Reference returned from Realex
        }

    def _starNumber(self, card_number, s):
        midcc = card_number[4:-2]
        repcc = '*'*len(midcc)
        return str(s).replace(midcc, repcc)

    def _makeSimpleRebateRequest(self, orderid, pasref, authcode, amount, password):
        t = tuple(time.localtime()[:6])
        timestamp="%s%02.2d%02.2d%02.2d%02.2d%02.2d"%t
        digest = self._SHA1Digest(timestamp + '.'+self.MerchantID + '.'+ str(orderid) + '.' + str(amount) + '.'+self.Currency+'.')

        rv = Element('request', timestamp=timestamp, type='rebate')
        rv.append(TElement('merchantid', text=self.MerchantID))
        rv.append(TElement('account', text=self.SubAccount))
        rv.append(TElement('orderid', text=str(orderid)))
        rv.append(TElement('pasref', text=str(pasref)))
        rv.append(TElement('authcode', text=str(authcode)))
        rv.append(TElement('amount', text=str(amount)))
        rv.append(TElement('autosettle', flag='1'))
        rv.append(TElement('refundhash', text=sha1(password).hexdigest()))
        rv.append(TElement('sha1hash', text=digest))
        return tostring(rv)


    def Rebate(self, orderid, pasref, authcode, amount, password):
        if not password:
            return {
                'result': -1, # 0 for success
                'message': 'Cannot do rebates - password is required',        # Text version of result
            }

        logger.info('Credit Card Rebate Requested, pasref = %s' % pasref) 

        xml = self._makeSimpleRebateRequest(orderid, pasref, authcode, amount, password)

        if self.TESTING:
            return {
                'result': 0,                     # 0 for success
                'message': 'Test Rebate',        # Text version of result
            }

        rv = self._mkRequest(xml, 'Rebate')
        if rv['result'] != 0:
            logger.error('Credit Card Rebate Failed (%s)' % rv['result'], xml, str(rv))
        else:
            logger.info('Credit Card Rebate Succeeded', xml, str(rv))

        return {
            'result': rv.get('result'), # 0 for success
            'message': rv.get('message'),        # Text version of result
        }

    def _makeSimpleVoidRequest(self, orderid, pasref, authcode):
        t = tuple(time.localtime()[:6])
        timestamp="%s%02.2d%02.2d%02.2d%02.2d%02.2d"%t
        digest = self._SHA1Digest(timestamp + '.'+self.MerchantID + '.'+ str(orderid) + '...')

        rv = Element('request', timestamp=timestamp, type='void')
        rv.append(TElement('merchantid', text=self.MerchantID))
        rv.append(TElement('account', text=self.SubAccount))
        rv.append(TElement('orderid', text=str(orderid)))
        rv.append(TElement('pasref', text=str(pasref)))
        rv.append(TElement('authcode', text=str(authcode)))
        rv.append(TElement('sha1hash', text=digest))
        return tostring(rv)

    def Void(self, orderid, pasref, authcode, void_message="no void message provided"):
        logger.info('Credit Card Void Requested, pasref = %s' % pasref) 

        xml = self._makeSimpleVoidRequest(orderid, pasref, authcode)

        if self.TESTING:
            return {
                'result': 0,                   # 0 for success
                'message': 'Test Void',        # Text version of result
            }

        rv = self._mkRequest(xml, 'Void')
        if rv['result'] != 0:
            logger.error('Credit Card Void Failed (%s) %s, %s', rv['result'], xml, str(rv))
        else:
            logger.info('Credit Card Void Succeeded: %s, %s', xml, str(rv))

        return {
            'result': rv.get('result'),          # 0 for success
            'message': rv.get('message'),        # Text version of result
        }


    def _mkRequest(self, xml, request_name):
        conn=httplib.HTTPSConnection(HOSTNAME, 443)
        conn.putrequest('GET', URL)
        conn.putheader("Content-Type", "text/xml")
        conn.putheader("Content-Length",  "%s" % len(xml))
        conn.endheaders()       
        conn.send(xml)       
        resp = conn.getresponse()

        if resp.status != 200:
            logger.error('Communications Error (%s), response = %s' % (request_name, resp.status), 
                exc_info=True)
            raise CommunicationsError('Error communicating with Bank, %s' % resp.status)

        xml = fromstring(resp.read())
        rv = dict([(el.tag.lower(), el.text) for el in xml])
        rv['result'] = int(rv['result'])
        return rv
