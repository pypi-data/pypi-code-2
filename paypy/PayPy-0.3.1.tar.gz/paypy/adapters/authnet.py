"""Authorize.net Payment Adapter

Interacts with the Authorize.net API using mapped fields from the
Payment module.

"""

import urllib, urllib2
import hashlib
import datetime
import uuid
import re
import elementtree.ElementTree as ET

from paypy.adapters           import *
from paypy.exceptions.authnet import AIMException, ARBException

# AIM Constants
ENDPOINT_AIM_PRODUCTION = 'secure.authorize.net/gateway/transact.dll'
ENDPOINT_AIM_TEST       = 'test.authorize.net/gateway/transact.dll'

# ARB Constants
ENDPOINT_ARB_PRODUCTION = 'api.authorize.net/xml/v1/'
ENDPOINT_ARB_TEST       = 'apitest.authorize.net/xml/v1/'
REQUEST_PATH            = 'request.api'
XML_SCHEMA              = 'schema/AnetApiSchema.xsd'
ANET_XMLNS              = ' xmlns="AnetApi/xml/v1/schema/AnetApiSchema.xsd"'

# ARB Root Request Elements
REQUEST_ELEMENTS        = {'create' : 'ARBCreateSubscriptionRequest',
                           'update' : 'ARBUpdateSubscriptionRequest',
                           'status' : 'ARBGetSubscriptionStatusRequest',
                           'cancel' : 'ARBCancelSubscriptionRequest'}

###################
## AIM Field Dicts
###################
RESPONSE_CODES  = {
    1: 'approved',
    2: 'declined',
    3: 'error',
    4: 'held for review'
}

REQUIRED_FIELDS = (
    'x_login',
    'x_tran_key',
    'x_type',
    'x_card_num',
    'x_exp_date',
    'x_amount',
    'x_version',
    'x_method',
    'x_delim_char',
    'x_url',
    'x_relay_response',
)

DEFAULT_FIELDS  = {
    'version'         : '3.1',
    'delim_char'      : '|',
    'delim_data'      : 'TRUE',
    'url'             : 'FALSE',
    'type'            : 'AUTH_CAPTURE',
    'method'          : 'CC',
    'relay_response'  : 'FALSE',
    'testing'         : False
}

ALLOWED_FIELDS  = (
    'x_address',
    'x_allow_partial_auth',
    'x_amount',
    'x_auth_code',
    'x_authentication_indicator',
    'x_card_code',
    'x_card_num',
    'x_cardholder_authentication_value',
    'x_city',
    'x_company',
    'x_country',
    'x_cust_id',
    'x_customer_ip',
    'x_delim_char',
    'x_delim_data',
    'x_description',
    'x_duplicate_window',
    'x_duty',
    'x_email',
    'x_email_customer',
    'x_encap_char',
    'x_exp_date',
    'x_fax',
    'x_first_name',
    'x_footer_email_receipt',
    'x_freight',
    'x_header_email_receipt',
    'x_invoice_num',
    'x_last_name',
    'x_line_item',
    'x_login',
    'x_merchant_email',
    'x_method',
    'x_phone',
    'x_po_num',
    'x_recurring_billing',
    'x_relay_response',
    'x_ship_to_address',
    'x_ship_to_company',
    'x_ship_to_country',
    'x_ship_to_city',
    'x_ship_to_first_name',
    'x_ship_to_last_name',
    'x_ship_to_state',
    'x_ship_to_zip',
    'x_split_tender_id',
    'x_state',
    'x_tax',
    'x_tax_exempt',
    'x_test_request',
    'x_tran_key',
    'x_trans_id',
    'x_type',
    'x_version',
    'x_zip',
    'x_url'
)

###################
## ARB Field Dicts
###################
ARB_DEFAULT_FIELDS  = {
    'testing'         : False
}

ARB_REQUIRED_FIELDS = ('tran_key',
                       'login')

ARB_ALLOWED_FIELDS  = ('tran_key',
                       'login',
                       'id',
                       'ref_id',
                       'schedule',
                       'amount',
                       'card',
                       'billing',
                       'epithet',
                       'trial',
                       'account',
                       'order',
                       'customer',
                       'shipping')

class TransactionResult(Result):
    """Represent a transaction result as an object."""
    
    def __init__(self, data, delimiter='|'):
        
        fields = data.read().split(delimiter)
        
        self.code             = int(fields[0])
        self.status           = RESPONSE_CODES[self.code]
        self.subcode          = int(fields[1])
        self.reason_code      = int(fields[2])
        self.reason           = fields[3]
        self.approval         = fields[4]  if fields[4]  != '' else None
        self.avs              = fields[5]  if fields[5]  != '' else None
        self.transaction_id   = fields[6]  if fields[6]  != '' else None
        self.invoice_id       = fields[7]  if fields[7]  != '' else None
        self.description      = fields[8]  if fields[8]  != '' else None
        self.amount           = fields[9]  if fields[9]  != '' else None
        self.method           = fields[10] if fields[10] != '' else None
        self.type             = fields[11] if fields[11] != '' else None
        self.customer_id      = fields[12] if fields[12] != '' else None
        self.firstname        = fields[13] if fields[13] != '' else None
        self.lastname         = fields[14] if fields[14] != '' else None
        self.company          = fields[15] if fields[15] != '' else None
        self.address          = fields[16] if fields[16] != '' else None
        self.city             = fields[17] if fields[17] != '' else None
        self.state            = fields[18] if fields[18] != '' else None
        self.zip              = fields[19] if fields[19] != '' else None
        self.country          = fields[20] if fields[20] != '' else None
        self.phone            = fields[21] if fields[21] != '' else None
        self.fax              = fields[22] if fields[22] != '' else None
        self.email            = fields[23] if fields[23] != '' else None
        self.ship_firstname   = fields[24] if fields[24] != '' else None
        self.ship_lastname    = fields[25] if fields[25] != '' else None
        self.ship_company     = fields[26] if fields[26] != '' else None
        self.ship_address     = fields[27] if fields[27] != '' else None
        self.ship_city        = fields[28] if fields[28] != '' else None
        self.ship_state       = fields[29] if fields[29] != '' else None
        self.ship_zip         = fields[30] if fields[30] != '' else None
        self.ship_country     = fields[31] if fields[31] != '' else None
        self.tax              = fields[32] if fields[32] != '' else None
        self.duty             = fields[33] if fields[33] != '' else None
        self.freight          = fields[34] if fields[34] != '' else None
        self.tax_exempt       = fields[35] if fields[35] != '' else None
        self.po_number        = fields[36] if fields[36] != '' else None
        self.hash             = fields[37] if fields[37] != '' else None
        self.ccr              = fields[38] if fields[38] != '' else None
        self.avr              = fields[39] if fields[39] != '' else None
        self.account_number   = fields[40] if fields[40] != '' else None
        self.card_type        = fields[41] if fields[41] != '' else None
        self.tender_id        = fields[42] if fields[42] != '' else None
        self.requested_amount = fields[43] if fields[43] != '' else None
        self.balance          = fields[44] if fields[44] != '' else None
        
        self.response         = fields
    
    def validate(self, login, salt):
        """Validate a returned response with the given hash."""
        
        value = ''.join([salt, login, self.transaction_id, self.amount])
        return self.hash.upper() == hashlib.md5(value).hexdigest().upper()
    
    def __str__(self):
        """Return the response message."""
        
        return self.reason
    
    def __int__(self):
        """Return the response code."""
        
        return self.code
    
    def __repr__(self):
        """Return the object representation."""
        
        return '<%s at 0x%x %s>' % (self.__class__.__name__, abs(id(self)), self.type)

class RecurringTransactionResult(Result):
    """Represent a recurring (subscription) transaction result as an object."""
    
    def __init__(self, data):
        """Set the result items."""
        
        data     = data.replace(ANET_XMLNS, '')
        
        root     = ET.XML(data)
        messages = root.find('messages')
        
        self.result_code = messages.find('resultCode').text
        self.code        = messages.find('message/code').text
        self.reason      = messages.find('message/text').text
        self.status      = None
        
        self.subscription_id = None
        subscription_id      = root.find('subscriptionId')
        
        if root.tag == 'ARBCreateSubscriptionResponse' and subscription_id is not None:
            self.subscription_id = subscription_id.text
        
        # GetSubscriptionStatusResponse specific
        if root.tag == 'ARBGetSubscriptionStatusResponse':
            self.status = root.find('Status').text.capitalize().strip()
    
    def __str__(self):
        """Calling str on the object will return the subscription_id if successful (and it exists) or the the message."""
        
        if self.subscription_id:
            return self.subscription_id
        
        if self.status:
            return self.status
        
        return self.reason
    
    def __repr__(self):
        """Object representation of the subscription result object."""
        
        return '<%s at 0x%x %s>' % (self.__class__.__name__, abs(id(self)), self.result_code)

class Transaction(Adapter):
    """Authorize.net AIM (Advanced Integration Method) transaction object adapter.
    
    Represent an Authorize.net transaction and provide a method for
    submission.
    
    """
    
    def __init__(self, configuration):
        
        if not isinstance(configuration, dict):
            raise AIMException('Configuration must be a dictionary')

        default = DEFAULT_FIELDS
        
        default.update(configuration)
        
        configuration = default
        
        testing = configuration.pop('testing')
        host    = ENDPOINT_AIM_TEST if testing else ENDPOINT_AIM_PRODUCTION
        
        # Create a set and fields dict with proper Authnet key names
        fields_dict = dict([['x_'+k, v] for k,v in configuration.items()])
        fields      = set(fields_dict)
        
        # Diff configuration with the required fields
        diff        = set(REQUIRED_FIELDS).difference(fields)
        
        if diff:
            raise AIMException('The following fields are required: %s' % repr(diff))
        
        # Make sure all of the fields passed in are allowed
        diff        = fields.difference(set(ALLOWED_FIELDS))
        
        if diff:
            raise AIMException('The following fields are not allowed: %s' % repr(diff))
        
        self.fields = fields_dict
        
        # Create the connection object
        self.connection = urllib2.Request(url='https://' + host)
    
    def set_fields(self, fields):
        """Amend the instantiated configuration with more fields."""
        
        # Convert to authnet friendly key names
        fields     = dict([['x_'+k, v] for k,v in fields.items()])
        
        # Check to be sure we are adding fields that are okay
        diff   = set(fields).difference(set(ALLOWED_FIELDS))
        
        if diff:
            raise AIMException('The following fields are not allowed: %s' % repr(diff))
        
        self.fields.update(fields)
    
    def process(self):
        """Process the transaction and return a result."""
        
        data = urllib.urlencode(self.fields)
        
        self.connection.headers['Content-Length'] = str(len(data))
        self.connection.data                      = data
        
        request = urllib2.urlopen(self.connection)
        result  = TransactionResult(request)
        
        return result

class RecurringTransaction(Adapter):
    """Authorize.net ARB (Automated Recurring Billing) transaction object adapter.
    
    Represent an Authorize.net recurring transaction and provide
    methods for submitting new subscriptions, updating subscriptions,
    cancelling subscriptions, and retrieving the status of a
    subscription.
    
    """
    
    def __init__(self, configuration):
        
        if not isinstance(configuration, dict):
            raise ARBException('Configuration must be a dictionary')
        
        default = ARB_DEFAULT_FIELDS
        default.update(configuration)
        
        configuration = default
        
        testing = configuration.pop('testing')
        host    = ENDPOINT_ARB_TEST if testing else ENDPOINT_ARB_PRODUCTION
        
        self.connection                         = urllib2.Request(url='https://' + host + REQUEST_PATH)
        self.connection.headers['Content-Type'] = 'text/xml'
        
        # Before doing anything, let's make sure the absolute necessary are (somewhat) present
        diff = set(ARB_REQUIRED_FIELDS).difference(set(configuration))

        if diff:
            raise ARBException('The following top-level fields are required: %s' % repr(diff))
        
        # Make sure all of the fields passed in are allowed
        diff = set(configuration).difference(set(ARB_ALLOWED_FIELDS))
        
        if diff:
            raise ARBException('The following top-level fields are not allowed: %s' % repr(diff))
        
        # Tranny keys (haha) and login id
        self.key   = configuration['tran_key']
        self.login = configuration['login']
        
        # Name
        self.epithet = configuration.pop('epithet') if 'epithet' in configuration else None
        
        # Coerce to string
        self.subscription_id = str(configuration.pop('id')) if 'id' in configuration else None
        
        # Assign basic configuration points
        self.ref_id = configuration['ref_id'] if 'ref_id' in configuration else ''
        
        # Standard object attributes
        self.schedule   = None
        self.amount     = None
        self.trial      = None
        self.payment    = None
        self.customer   = None
        self.billing    = None
        self.order      = None
        self.payload    = None
        
        # Schedule element
        if 'schedule' in configuration:
            schedule      = configuration['schedule']
            self.schedule = {}
            
            self.schedule['start']  = (schedule['start']  if 'start'  in schedule else datetime.datetime.utcnow())
            self.schedule['length'] = (schedule['length'] if 'length' in schedule else 1)

            if 'unit' in schedule:
                self.schedule['unit'] = schedule['unit']
                
                if self.schedule['unit'] not in ('months', 'days'):
                    raise ARBException('The interval unit "%s" is not supported' % unit)
            else:
                self.schedule['unit'] = 'months'
            
            if 'cycles' in schedule:
                self.schedule['cycles'] = schedule['cycles']
                
                if int(self.schedule['cycles']) > 9999:
                    raise ARBException('The subscription cycle cannot exceed 9999 (ongoing)')
            else:
                self.schedule['cycles'] = 9999
        
        # Amount element
        if 'amount' in configuration:
            self.amount = str(configuration['amount'])
        
        # Trial
        if 'trial' in configuration:
            trial = configuration['trial']
            
            self.trial = trial
        
        # Credit
        if 'card' in configuration:
            self.payment          = configuration['card']
            self.payment.update({'type' : 'card'})
        
            # Check the card expiration date
            exp  = re.search('(\d\d\d\d)-(\d\d)', self.payment['expiration'])
                
            if not exp:
                raise ARBException('The expiration date provided is not valid, it should be in this form: YYYY-MM')
        
        # Account
        if 'account' in configuration:
            if 'card' in configuration:
                raise ARBException('You cannot specify the bank account and credit card payment options simultaneously')
            
            self.payment             = {'account' : configuration['account']}
            self.payment.update({'type' : 'account'})
        
        # Customer information
        if 'customer' in configuration:
            self.customer = configuration['customer']
        
        if 'billing' in configuration:
            self.billing = configuration['billing']
        
        # Order information
        if 'order' in configuration:
            self.order    = configuration['order']
    
    def create(self):
        """Create a new subscription."""
        
        return RecurringTransactionResult(self._request('create'))
    
    def update(self):
        """Update a given subscription."""

        return RecurringTransactionResult(self._request('update'))
    
    def status(self):
        """Retrieve the subscription's status."""
        
        if self.subscription_id is None:
            raise ARBException('A valid subscription ID must be provided')
        
        return RecurringTransactionResult(self._request('status'))
    
    def cancel(self):
        """Cancel the subscription object."""
        
        if self.subscription_id is None:
            raise ARBException('A valid subscription ID must be provided as an argument')
        
        return RecurringTransactionResult(self._request('cancel'))
    
    def _request(self, operation):
        """Send the request to authorize.net."""
        
        data = self._to_xml(REQUEST_ELEMENTS[operation])
        
        self.connection.headers['Content-Length'] = str(len(data))
        self.connection.data                      = data
        
        request   = urllib2.urlopen(self.connection)
        result    = request.read()
        
        return result
    
    def _to_xml(self, operation):
        """Convert object attributes to an XML document."""
        
        name = self.epithet
        
        # Build the document root element
        root = ET.Element(operation, xmlns='AnetApi/xml/v1/schema/AnetApiSchema.xsd')
        
        # Merchant authentication element
        auth = ET.SubElement(root, 'merchantAuthentication')
        ET.SubElement(auth, 'name').text           = self.login
        ET.SubElement(auth, 'transactionKey').text = self.key
        
        # Set the reference ID
        ET.SubElement(root, 'refId').text          = self.ref_id
        
        # Do we have a subscription ID provided?
        if self.subscription_id:
            ET.SubElement(root, 'subscriptionId').text = self.subscription_id
        
        # If we are running anything but a CancelSubscriptionRequest operation, we need to fill out the request
        if operation not in ('ARBCancelSubscriptionRequest', 'ARBGetSubscriptionStatusRequest'):
            subscription = ET.SubElement(root, 'subscription')
            
            # Do we have a name for this subscription?
            if name:
                ET.SubElement(subscription, 'name').text = name
            
            # Build the schedule element
            if self.schedule:
                schedule = ET.SubElement(subscription, 'paymentSchedule')
                interval = ET.SubElement(schedule, 'interval')
                
                ET.SubElement(interval, 'length').text    = str(self.schedule['length'])
                ET.SubElement(interval, 'unit').text      = str(self.schedule['unit'])
                ET.SubElement(schedule, 'startDate').text = self.schedule['start'].strftime('%Y-%m-%d')
                
                # If a trial, build the lement
                if self.trial:
                    self.schedule['cycles'] += self.trial['cycles']
                    ET.SubElement(schedule, 'trialOccurrences').text = str(self.trial['cycles'])
                
                ET.SubElement(schedule, 'totalOccurrences').text     = str(self.schedule['cycles'])
                
            # Build the charge amount element
            if self.amount:
                ET.SubElement(subscription, 'amount').text       = str(self.amount)
                
            # Build the trial amount
            if self.trial:
                ET.SubElement(subscription, 'trialAmount').text  = str(self.trial['amount'])
                
            # Build the payment element
            if self.payment:
                payment_type = self.payment['type']
                
                if payment_type == 'card':
                    payment = ET.SubElement(subscription, 'payment')
                    credit  = ET.SubElement(payment, 'creditCard')
                    
                    ET.SubElement(credit, 'cardNumber').text     = str(self.payment['number'])
                    ET.SubElement(credit, 'expirationDate').text = self.payment['expiration']
                    
                    if 'code' in self.payment:
                        ET.SubElement(credit, 'cardCode').text     = str(self.payment['code'])
                    
                elif payment_type == 'account':
                    payment = ET.SubElement(subscription, 'payment')
                    account = ET.SubElement(subscription, 'bankAccount')
                    
                    ET.SubElement(account, 'accountType').text   = self.payment['account_type']
                    ET.SubElement(account, 'routingNumber').text = str(self.payment['routing_number'])
                    ET.SubElement(account, 'accountNumber').text = str(self.payment['account_number'])
                    ET.SubElement(account, 'nameOnAccount').text = self.payment['name']
                    ET.SubElement(account, 'echeckType').text    = self.payment['echeck']
                    ET.SubElement(account, 'bankName').text      = self.payment['bank']
            
            # If we have an additional order element, add it here
            if self.order:
                order = ET.SubElement(subscription, 'order')
                
                if 'invoice' in self.order:
                    ET.SubElement(order, 'invoiceNumber').text = str(self.order['invoice'])
                
                if 'description' in self.order:
                    ET.SubElement(order, 'description').text   = self.order['description']
            
            # Build the customer and bill to elements
            if self.customer:
                customer = ET.SubElement(subscription, 'customer')
                
                if 'id' in self.customer:
                    ET.SubElement(customer, 'id').text  = str(self.customer['id'])
                
                if 'email' in self.customer:
                    ET.SubElement(customer, 'email').text = self.customer['email']
                
                if 'phone' in self.customer:
                    ET.SubElement(customer, 'phoneNumber').text = str(self.customer['phone'])
                
            if self.billing:
                bill     = ET.SubElement(subscription, 'billTo')
                
                ET.SubElement(bill, 'firstName').text = self.billing['firstname']
                ET.SubElement(bill, 'lastName').text  = self.billing['lastname']
                
                if 'company' in self.billing:
                    ET.SubElement(bill, 'company').text = self.billing['company']
                
                if 'address' in self.billing:
                    ET.SubElement(bill, 'address').text = self.billing['address']
                
                if 'city' in self.billing:
                    ET.SubElement(bill, 'city').text    = self.billing['city']
                
                if 'state' in self.billing:
                    ET.SubElement(bill, 'state').text   = self.billing['state']
                
                if 'zip' in self.billing:
                    ET.SubElement(bill, 'zip').text     = str(self.billing['zip'])
                
                if 'country' in self.billing:
                    ET.SubElement(bill, 'country').text = self.billing['country']
    
        self.payload = ET.tostring(root, encoding='UTF-8')
        
        return self.payload
