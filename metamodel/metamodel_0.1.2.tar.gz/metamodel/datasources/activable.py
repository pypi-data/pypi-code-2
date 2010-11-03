from metamodel.datasources import DataSource

class ActivableDataSource(DataSource):
    def __init__(self, *args, **kwargs):
        self._connected = False
        active = None
        if "active" in kwargs:
            active = kwargs.pop("active")
        DataSource.__init__(self, *args, **kwargs)
        if not active == None:
           self.active = active

    # Activate
    def setProperty(self, name, value):
        DataSource.setProperty(self, name, value)
        if name == "active":
            if value == False and self._connected:
                self.disconnect()
            elif value == True and not self._connected:
                self.connect()

   
