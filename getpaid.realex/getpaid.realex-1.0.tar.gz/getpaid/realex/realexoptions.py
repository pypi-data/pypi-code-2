"""
    Configuration of the Realex Payment Processor
"""
from zope import schema
from getpaid.core.interfaces import IPaymentProcessorOptions
from getpaid.core.options import PersistentOptions

class IRealexOptions(IPaymentProcessorOptions):

    MerchantID = schema.TextLine(title=u'Merchant Id', description=u'Provided by realex')
    Secret = schema.Password(title=u'Secret Code', description=u'Provided by realex')
    SubAccount = schema.TextLine(title=u'SubAccount', required=False, default=u'internettest',
            description=u"Set to 'internet' for live account, 'internettest' to test against a valid account")
    chargeDescription = schema.TextLine(title=u'Charge Description',
        description=u'Default charge description on the payment', required=False)
    Testing = schema.Bool(title=u'Test Mode', required=False, default=False,
            description=u'You do not need a realex account to use test mode. It does not attempt to contact a server')

RealexOptions = PersistentOptions.wire( "RealexOptions", "getpaid.realex", IRealexOptions )

