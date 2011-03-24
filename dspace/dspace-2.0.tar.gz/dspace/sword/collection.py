from dspace.sword.service import SwordService
from dspace.sword.item import SwordItem




class SwordCollection(object):
    """ """
    
    def __init__(self, service, handle):
        assert isinstance(service, SwordService)
        self._handle = handle
        self._service = service
    
    def deposit_item(self, item):
        assert isinstance(item,SwordItem)
        return self._service.deposit(self._handle, item.get_package())
    
