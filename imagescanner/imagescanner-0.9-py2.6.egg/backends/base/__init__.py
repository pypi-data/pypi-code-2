"""Abstract base classes

$Id: __init__.py,v b0e8e4bd3d27 2011/05/14 17:42:19 seocam $"""

class ScannerManager(object):
    """Abstract ScannerManager class"""

    def __init__(self, **kwargs):
        self._devices = []
    
    def _refresh(self):
        """Look for new scanner devices"""
        raise NotImplementedError

    def get_scanner(self, scanner_id):
        """Return a scanner with the given ID or None if not found"""
        devices = self.list_scanners()

        for dev in devices:
            if dev.id == scanner_id:
                return dev
        return None

    def list_scanners(self):
        """Return a list with all the available devices"""
        self._refresh()
        return self._devices      

class Scanner(object):
    """Abstract Scanner class"""

    def scan(self, dpi=200):
        """Scan a new image using the given DPI and returns a PIL object"""
        raise NotImplementedError

    def status(self):
        """Get device status"""
        # TODO: Define standard status
        raise NotImplementedError
