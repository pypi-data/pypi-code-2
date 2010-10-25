from datetime import datetime
from datetime import date
from decimal import Decimal

class Foo(object):
    _xml_metadata = {
                     'sequence': ('sample',),
                     'types': {'sample': lambda: str}}

    def __init__(self, *args, **kwargs):
        self.sample = 'test'
        
class Widget(object):
    _xml_metadata = {'namespace': 'http://www.example.com/schemas/widget',
                     'sequence': ('Id', 'Name', 'Description', 'Created', 'IsActive','Customer','Sku','Price',),
                     'attributes': ('Default', 'Color', 'LastPurchase',),
                     'types': {'Id': lambda: int, 'Price': lambda: Decimal, 'Sku': lambda: [str], 'LastPurchase': lambda: date, 'Customer': lambda: Person, 'Name': lambda: str, 'Description': lambda: str, 'Created': lambda: datetime, 'IsActive': lambda: bool, 'Default': lambda: bool, 'Color': lambda: str}
                     }

    def __init__(self, *args, **kwargs):
        self.LastPurchase = None
        self.Name = None
        self.Description = None
        self.Created = None
        self.IsActive = None
        self.Default = None
        self.Color = None
        self.Customer = None
        self.Sku = None
        self.Id = None
        self.Price = None

class Person(object):
    _xml_metadata = {'namespace': 'http://www.example.com/schemas/widget',
                     'sequence': ('FullName',),
                     'attributes': ('IsDefault',),
                     'types': {'FullName': lambda: str, 'IsDefault': lambda: str}
                     }    
    def __init__(self):
        self.FullName = None
        self.IsDefault = None
        
class WidgetWithPrimitiveType(str):
    _xml_metadata = {'namespace': 'http://www.example.com/schemas/widget',
                     'attributes': ('AccessLevel',),
                     'types': {'AccessLevel': lambda: str}
                     }

    def __init__(self, *args, **kwargs):
        super(WidgetWithPrimitiveType, self).__init__(*args, **kwargs)
        self.AccessLevel = None
        