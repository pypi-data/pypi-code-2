"""
A datasource which periodically checks an rss feed.
"""
import time

from metamodel.basemodel import SubscribableModel
from metamodel.properties import Property, Link

from metamodel.datasources import DataSource

from twisted_feeder import FeederFactory, FeederProtocol
from twisted.internet import task

class RSSItem(SubscribableModel):
    """
    An rss item.
    """
    name = Property(str, "an rss item")
    updated = Property(str, "last updated")
    timestamp = Property(float, 0.0)

class RSSDataSource(DataSource, FeederProtocol):
    """
    An rss data feed.
    """
    name = Property(str, "RSS Source")
    url = Link("")
    active = Property(bool, False)
    delay = Property(int, 10)
    title = Property(str, "", ro=True)
    def  __init__(self, *args, **kwargs):
        self._looping_call = None
        FeederProtocol.__init__(self)
        self._connected = False
        self.factory = FeederFactory('.')
        self._entry_times = []
        self._entry_dict = {}
        self._lastidx = 0
        active = None
        if "active" in kwargs:
            active = kwargs.pop("active")
        DataSource.__init__(self, *args, **kwargs)
        if not active == None:
            self.active = active

    def workOnPage(self, parsed_feed, _):
        """
        callback with the parsed feed.
        """
        chan = parsed_feed.get('channel', None)
        if chan:
            prevtitle = self.title
            self.title = chan.get('title', '')
            if not prevtitle == self.title:
                if not self.isDefault('name'):
                    self.name = self.title
        for entry in parsed_feed["entries"]:
            if "updated_parsed" in entry:
                f_time = time.mktime(entry["updated_parsed"])
            else:
                f_time = time.time()
            if not f_time in self._entry_dict:
                self._entry_dict[f_time] = entry
                #entry_dict[f_time] = titles[i]+" "+e["title"]
                self._entry_times.append(f_time)

        self._entry_times.sort()
        while self._lastidx < len(self._entry_dict):
            entry = self._entry_dict[self._entry_times[self._lastidx]]
            self.textReceived(entry)
            self._lastidx += 1
        return parsed_feed

    def textReceived(self, data):
        """
        create a metamodel item from a parsed rss item.
        """
        title = data["title"].encode('latin-1','ignore').strip()
        item = self.new(RSSItem, name=title)
        item._datasource = self
        for prop in data.keys():
            if isinstance(data[prop], unicode):
                if not hasattr(RSSItem, prop):
                    if prop == "link":
                        prop_obj = Link("", ro=True)
                    else:
                        prop_obj = Property(str, "", ro=True)
                    prop_obj.name = prop
                    RSSItem.properties.append(prop_obj)
                    setattr(RSSItem, prop, prop_obj)
                setattr(item,
                          prop,
                          data[prop].encode('latin-1', 'ignore').strip())
        if "updated" in data:
            try:
                #t = time.mktime(time.strptime(data["updated"],
                #      "%a, %d %b %Y %H:%M:%S %Z"))
                atime = time.mktime(data["updated_parsed"])
            except KeyError:
                print "CANT DECODE TIME!!!:", data["updated"]
                atime = 666.0
            setattr(item, "timestamp", float(atime))
        self.addChild(item)

    # Activate
    def setProperty(self, name, value):
        """
        property changes
        """
        SubscribableModel.setProperty(self, name, value)
        if name in ["active"]:
            if value == False and self._connected:
                self.stopDownload()
            elif value == True and not self._connected:
                self.startDownload()
        elif name == "delay" and self.active:
            self.stopDownload()
            self.startDownload()

    def startDownload(self):
        """
        Start downloading the feed.
        """
        self._looping_call = task.LoopingCall(self.start,
            [[self.url]], self.factory.cacheDir, False)
        self._looping_call.start(self.delay)
        #self.start([[self.url]], self.factory.cacheDir, False)

    def stopDownload(self):
        """
        Stop downloading.
        """
        if self._looping_call:
            self._looping_call.stop()
            self._looping_call = None

    builtby = ["DataSource"]
