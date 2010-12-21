# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import time, urllib2, base64, os, sys
from threading import Thread

class AuthorizationService(object):
    """An authorization service runs in a separate thread to keep the list
       of users and their optional resource mappings up to date.
    """
    def __init__(self, interval=3600.0):
        """Initializes a SecurityService.
        
        - `interval`: indicates how often the authorization data is updated.
        """

        self.auths = []
           
        self.interval = interval
        self.__running = False
        self.t = Thread(target=self._update)
        self.t.setDaemon(True)

    def _update(self):
        while self.__running:
            for a in self.auths:
                a.update()
            time.sleep(self.interval)

    def addAuth(self, auth):
        """Add an `Authorization`-class to the service.
        
        - `auth`: An `Authorization`-class instance
        """
        if isinstance(auth, Authorization):
            self.auths.append(auth)
        
    def stop(self):
        self.__running = False

    def start(self):
        self.__running = True
        self.t.start()
                                
    def isAuthorized(self, dn, resource=None):
        """Checks if a given user is authorized.
           
        @param dn string with X.509 subject DN
        """
        if len([True for auth in self.auths if auth.isAuthorized(dn, resource=resource)]) > 0:
            return True
        
        return False

# improvements:
# 1. it should be up to the class inheriting from Authorization how often the
# state should be updated.
# 2. a list is inefficient here, problem is how to catch the CN added by proxy 
#    certs when using a hash-map.


# make a dn object and override __eq__?

class Authorize(object):
    def __init__(self, validusers=[]):
        # list of X.509 DN subject strings representing users
        self.validusers = set(validusers)

    def isAuthorized(self, dn, resource=None):
        """Checks if a given user is authorized to access the service
           
        @param dn string with X.509 subject DN
        """
        for user in self.validusers:
            if dn.startswith(user):
                return True

        return False

    def replace(self, users):
        """Replace the current list of valid users
        
        @param users list of X.509 DN strings representing valid users
        """
        self.validusers = set(users)

    def merge(self, users):
        self.validusers = self.validusers.union(users)
                
# str.startsWith()

# this is a class that can be used if the authorization must be done
# at a lower layer in the application, for example if the user auth. must
# be done atomically together with a db write.

class AlwaysAuthorized(object):
    def isAuthorized(self, dn, resource=None):
        return True
        
class AuthorizeVOMRS(Authorize):

    def __init__(self, service, user=None, password=None):
        self.service = service
        self.authstr = None

        if user != None and password != None and user != '' and password != '':
            self.authstr = base64.encodestring('%s:%s' % (user, password))[:-1]

        # timestamp for when last update occurred
        self.ts = 0.0
        
        # how often the service should be asked for a new list of users
        Authorize.__init__(self)

    def _fetch(self):
        req = urllib2.Request(self.service)
        authheader =  "Basic %s" % self.authstr
        req.add_header("Authorization", authheader)
        
        try:
            users = urllib2.urlopen(req)
            self.parse(users)
            self.ts = time.time()
        except IOError, e:
            log.debug("Failed to fetch user list from VOMRS service %s: %s", self.service, str(e))
        except:
            raise

    def parse(self, users):
        self.merge([(user.strip()).strip('"') for user in users])

    def update(self):
        self._fetch()
                
class AuthorizeFlatFile(Authorize):
    """Handles files with one X.509 DN/row.
    
    Format: <DN>\n
            A line starting with a #-character is ignored.
    """
    def __init__(self, path):
        self.path = path
        self.__last_ts = sys.maxint
        Authorize.__init__(self)

    def parse(self, path):
        f = file(path, "r")
        
        self.merge([user.strip() for user in f])
        f.close()
    
    def update(self):
        mtime = os.path.getmtime(self.path)
        if self.__last_ts < mtime:
            self.parse(self.path)
            self.__last_ts = mtime
