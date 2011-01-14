# coding: utf-8
from decimal import Decimal
from main import GetAuthorizedException, PaymentAttempt

params = {
            'affiliation_id': '123456789',
                'total': Decimal('0.0451'),
                    'order_id': '763AH1', # strings are allowed here
                        'card_number': '1234567890123456',
                            'cvc2': 423,
                                'exp_month': 1,
                                    'exp_year': 2010,
                                        'card_holders_name': 'JOAO DA SILVA',
                                            'installments': 1,
                                            }

attempt = PaymentAttempt(**params)
try:
        transaction = attempt.get_authorized()
except GetAuthorizedException, e:
        print u'Erro %s: %s' % (e.codret, e.msg)
else:
   transaction.capture()
