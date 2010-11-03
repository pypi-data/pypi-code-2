from twisted.internet import threads, reactor

from xmlrpclib import ServerProxy
from urllib import urlencode

from metamodel import DataSource, SubscribableModel
from metamodel import Link, Property, Password

from time import strptime, mktime

class DokuwikiPage(SubscribableModel):
    name = Property(str, "", ro=True)
    id = Property(str, "", ro=True)
    timestamp = Property(float, 0, ro=True)
    perms = Property(int, 8, ro=True)
    size = Property(int, 0, ro=True)

class DokuwikiSection(SubscribableModel):
    name = Property(str, "")
    id = Property(str, "")

class Dokuwiki(DataSource):
    name = Property(str, "Dokuwiki Source")
    url = Link("")
    user = Property(str, "")
    password = Password("")
    active = Property(bool, False)

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
        SubscribableModel.setProperty(self, name, value)
        if name in ["active"]:
            if value == False and self._connected:
                self.disable()
            elif value == True and not self._connected:
                self.enable()

    def enable(self):
        self.connect()

    def disable(self):
        pass

    # put a page into the page tree
    def add_page(self, page):
        name = page["id"]
        path = name.split(":")
        print " *", page
        parent = self
        for i, pathm in enumerate(path):
            if i == len(path)-1: # a page
                t = mktime(strptime(page['lastModified'].value,"%Y-%m-%dT%H:%M:%S"))

                new = self.new(DokuwikiPage,
                               id = name,
                               name = pathm,
                               timestamp = t,
                               perms = int(page['perms']),
                               size = page['size'])
                parent.addChild(new)
                self._sections[name] = new
            else: # a namespace
                part_path = ":".join(path[:i+1])
                if not part_path in self._sections:
                    new = self.new(DokuwikiSection,
                                   id = name,
                                   name = pathm)
                    self._sections[part_path] = new
                    parent.addChild(new)
                else:
                    new = self._sections[part_path]

            parent = new

    def getChildrenToPersist(self):
        return []

    def callDeferred(self, get_func, got_func):
        d = threads.deferToThread(get_func)
        d.addCallback(got_func)

    def _getPageList(self):
        return self._rpc.wiki.getAllPages()

    def _gotPageList(self, pages):
        self._sections = {}
        self.purgeChildren()
        for page in pages:
            self.add_page(page)
        self._connected = True

    def get_pagelist(self):
        self.callDeferred(self._getPageList, self._gotPageList)

    def connect(self):
        # following commented line is for gtkhtml (not used)
        #simplebrowser.currentUrl = self.view.url.get_text()
        # handle response
        params = urlencode({'u':self.user,'p':self.password})
        fullurl = self.url + "/lib/exe/xmlrpc.php?"+ params
        self._rpc = ServerProxy(fullurl)
        print "connect!"
        #self.get_version()
        self.get_pagelist()

