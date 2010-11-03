from ..datasources import DataSource
from metamodel.basemodel import SubscribableModel
from metamodel.properties import Link,Property
from twisted.internet import threads,reactor

class SvnChangeSet(SubscribableModel):
    name = Property(str, "SVN Changeset")
    author = Property(str, "")
    timestamp = Property(float, 0.0)
    revision = Property(int, 0.0)
    

class SvnLogs(DataSource):
    name = Property(str, "SVN Source")
    url = Link("")
    active = Property(bool, False)
    delay = Property(int, 10)
    def __init__(self, *args, **kwargs):
        self._connected = False
        active = None
        if "active" in kwargs:
             active = kwargs.pop("active")
        DataSource.__init__(self, *args, **kwargs)
        if not active == None:
            self.active = active

    def getChildrenToPersist(self):
        return []

    # Activate
    def setProperty(self, name, value):
        SubscribableModel.setProperty(self, name, value)
        if name in ["active"]:
            if value == False and self._connected:
                self.stopDownload()
            elif value == True and not self._connected:
                reactor.callLater(5,self.startDownload)
        elif name == "delay" and self.active:
            self.stopDownload()
            self.startDownload()

    def getSvnLogs(self):
        from pysvn import Client
        c = Client()
        logs = c.log(self.url)
        return logs

    def gotSvnLogs(self, logs):
         for alog in logs:
            author = "unknown"
            if "author" in alog:
               author = alog.author
            self.addChild(self.new(SvnChangeSet,
                                   name=alog.message,
                                   timestamp=alog.date,
                                   author=author,
                                   revision=alog.revision.number
                                   ))
    def someError(self, *args):
        self.active = False

    def startDownload(self):
        d = threads.deferToThread(self.getSvnLogs)
        d.addCallback(self.gotSvnLogs)
        d.addErrback(self.someError)
            
    def stopDownload(self):
        pass
