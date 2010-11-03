import time
from ..datasources import DataSource
from metamodel.basemodel import SubscribableModel
from metamodel.properties import Link,Property
from twisted.internet import threads,reactor

class HgChangeSet(SubscribableModel):
    name = Property(str, "SVN Changeset")
    author = Property(str, "")
    timestamp = Property(float, 0.0)
    revision = Property(int, 0.0)
    

class HgLogs(DataSource):
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

    def getHgLogs(self):
        from mercurial import hg,ui,commands
        class MyUi(ui.ui):
            def __init__(self):
                ui.ui.__init__(self)
                self._newitem = None
            def parseHgLine(self, data):
                name,val = data.strip().split(":",1)
                return val.strip()
            def write(s, data):
                if data.startswith("changeset"):
                    val = s.parseHgLine(data)
                    s._newitem = self.new(HgChangeSet,changeset=val)
                    self.addChild(s._newitem)
                elif data.startswith("branch"):
                    val = s.parseHgLine(data)
                elif data.startswith("user"):
                    val = s.parseHgLine(data)
                    s._newitem.author = val
                elif data.startswith("date"):
                    val = s.parseHgLine(data)
                    val = val.split("+")[0].strip()
                    s._newitem.timestamp = time.mktime(time.strptime(val))
                elif data.startswith("summary"):
                    val = s.parseHgLine(data)
                    s._newitem.name = val
                elif data == '\n' and s._newitem:
                    s._newitem = None
        uio = MyUi()
        r = hg.repository(uio, path=self.url)
        commands.log(uio, r, rev=0, copies=False, date=0, only_branch=0,
                     no_merges=0, only_merges=0, keyword=0, user=0)

    def gotHgLogs(self, logs):
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
        self.getHgLogs()
        #d = threads.deferToThread(self.getSvnLogs)
        #d.addCallback(self.gotSvnLogs)
        #d.addErrback(self.someError)
            
    def stopDownload(self):
        pass
