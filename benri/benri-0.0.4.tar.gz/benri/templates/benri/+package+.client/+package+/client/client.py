# -*- coding: iso-8859-15 -*-

from benri.client import Client as BenriClient

class Client(BenriClient):
    
    def __init__(self, service_url):
        BenriClient.__init__(self, service_url)
