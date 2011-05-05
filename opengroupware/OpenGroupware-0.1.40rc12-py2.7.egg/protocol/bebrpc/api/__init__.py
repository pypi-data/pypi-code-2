
from customer import CustomerAPI

def get_api(domain, context=None):
    if domain == 'customer': return CustomerAPI(context)
    