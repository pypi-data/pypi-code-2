"""Session management"""


import logging
import types
import weakref
import stackless

from .const import ROLE_SERVICE, ROLE_ANY, ROLE_NOACCESS
from .errors import AccessError
from . import loop
from process import Process
from . import util
from .util import FormatRole, Bunch


MAXCALLINFOLEN = 1024

class SessionManager(Process):

    serviceName = "sessionManager"
    serviceAllowRPC = True
    processStartAsync = False

    sidCount = 0
    uidCount = 0


    def __init__(self):

        super(SessionManager, self).__init__()
        self.sessions = []


    def StartProcess(self):
        pass


    def StopProcess(self):
        for s in self.sessions:
            s.Close()
            s.sessionManager = None
        del self.sessions[:]


    def CreateSession(self, userid = None, username = None, role = ROLE_ANY):
        """Returns a new session.
        If 'userid' is "auto", then one will be generated from a pool of
        reserved system id's.

        Caller is responsible for calling Close() on the session when it's not
        in use anymore.
        """
        self.log.debug("CreateSession, userid=%s, username=%s, role=%s", userid, username, role)
        username = unicode(username)
        role = long(role)

        if userid == "auto":
            self.uidCount -= 1
            userid = self.uidCount
        elif userid is not None:
            userid = int(userid)

        vars = Bunch(sid = self.sidCount+1, userid = userid, userName = username, role = role, charid = None)

        self.sidCount += 1
        session = Session(self, set([ "userid", "charid", "userName" ]))
        session.vars.update(vars)
        self.sessions.append(session)

        # We never release a direct reference to session objects outside this module
        return weakref.proxy(session)


    def _DestroySession(self, session):
        self.sessions.remove(session)


    def FindSession(self, **kw):
        """Find session using one or more of the following search parameters:
        sid         session ID
        userid      user ID
        username    user name
        """

        # TODO: Index sessions on sid, userid and username

        sid = kw.get("sid", -1)
        userid = kw.get("userid", -1)
        username = kw.get("username", -1)

        for s in self.sessions:
            if s.sid == sid or s.userid == userid or s.userName == username:
                return s


    def UpdateSessionVariables(self, _session, pairs):
        updates = dict((k, v[1]) for (k, v) in pairs.iteritems())
        _session.LocalUpdateVariables(**updates)

    UpdateSessionVariables.access = ROLE_SERVICE


class Session(object):

    def __init__(self, sessionManager, propagatedVars=set()):
        self.vars = {}
        self.propagatedVars = propagatedVars
        self.ep = None
        self.sessionManager = sessionManager
        self.remotables = {}        # Key is (serviceName, objectName, objectID), value is remotable object
        self.valid = True
        self.callbackObjects = []


    def __repr__(self):
        return "Session <sid:%s, uid:%s, role:%s, name:%s>" % (self.sid, self.userid, self.role, self.userName)


    def __getattr__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        elif key in self.vars:
            return self.vars[key]
        else:
            raise AttributeError(key)


    def GetService(self, serviceName):
        service = self.sessionManager.app.GetService(serviceName)
        if not getattr(service, "serviceAllowRPC", False):
            raise AccessError("Service %s does not allow RPC access" % self.svc.serviceName)

        return service


    def Close(self):
        if not self.valid:
            return

        self.valid = False

        self.SendSessionEvent("OnSessionClosing")

        del self.callbackObjects[:]

        if self.ep:
            self.ep.SessionClosing(self)

        self.ep = None

        for object in self.remotables.values():
            object.SessionDetach(self)

        self.sessionManager._DestroySession(self)

        self.role = ROLE_ANY

    def AttachToRemotable(self, remotable):
        if remotable.objectKey not in self.remotables:
            # Add remotable to self
            self.remotables[remotable.objectKey] = remotable

            # Add self to remotable session list
            remotable.sessions.append(self)

            # Notify
            remotable.SessionAttach(self)


    def DetachFromRemotable(self, remotable):
        if remotable.objectKey in self.remotables:
            # Remove remotable object from self
            del self.remotables[remotable.objectKey]

            # Remove self from remotable session list
            remotable.sessions.remove(self)

            # Notify
            remotable.SessionDetach(self)

            # Clean out all context session state
            pass

    def LocalUpdateVariables(self, **kw):
        changes = {}

        for key, val in kw.items():
            oldValue = getattr(self, key, None)
            if oldValue != val:
                if key == "userid" and oldValue is not None:
                    raise RuntimeError("Session.UpdateVariable: Can't modify userid on session %s", self)

                self.sessionManager.log.debug("Session '%s' updating '%s' from '%s' to '%s'", self, key, oldValue, val)
                self.vars[key] = val
                changes[key] = (oldValue, val)

        # Notify any interested local objects about the session change.
        if len(changes):
            self.SendSessionEvent("OnSessionChange", changes)

        return changes

    LocalUpdateVariable = LocalUpdateVariables

    def UpdateVariables(self, **kw):
        changes = self.LocalUpdateVariables(**kw)

        changedKeys = set(changes)
        propagatedKeys = self.propagatedVars & changedKeys

        if len(propagatedKeys):
            propagatedChanges = dict((k, changes[k]) for k in propagatedKeys)
            self.ep.CallAsync("sessionManager.UpdateSessionVariables", propagatedChanges)

            for object in self.remotables.values():
                object.SessionChanges(self, propagatedChanges)

    UpdateVariable = UpdateVariables

    def CallServiceMethod(self, serviceName, methodName, args, kw):
        service = self.GetService(serviceName)

        method = getattr(service, methodName)
        return self.CallBoundMethod(serviceName, method, args, kw)


    def CallBoundMethod(self, objectName, method, args, kw):
        """
        Calls 'method'.

        'method' is a bound method or a function.
        'objectName' is used in error messages to identify the context of 'method'.
        'args' and 'kw' are what they are.

        The method must contain a property named 'access' which identifies the level of
        access. If the property is missing, the method is not considered published and
        cannot be called using CallBoundMethod.

        The 'access' property is a set of one or more ROLE flags. If the calling session
        doesn't have access according to the value of 'access' property, an exception
        is raised.

        If 'method' contains one or more arguments starting with an underscore, it's considered a
        session argument. The session value or values (bearing the same name but without
        the underscore) are spliced in front of 'args' prior to the call to 'method'. The
        following assumption can thus be made: Underscore arguments are always set by the system
        using values from the calling session, and therefore can be trusted completely. The following
        arguments contain values possible from a buggy or hacked client, and should always be
        scrutinized.

        The special argument "_session" can be used to get the session object itself. Calling
        util.GetSession() inside 'method' will also return the same session object.

        Session arguments must precede all other arguments.

        In the context of 'method' the current session is the calling session.
        """

        # Verify method access
        access = getattr(method, "access", ROLE_NOACCESS)
        if access == ROLE_NOACCESS or not util.HasAccess(access, self):
            err = "Access denied. %s has no access to method '%s' in service or class '%s'. Session role is %s, method access role is %s."
            err = err % (self, method.func_name, objectName, FormatRole(self.role), FormatRole(access))
            raise AccessError(err)


        sessionArgs = getattr(method, "sessionArgs", None)

        if sessionArgs is None:
            # Extract pre-args
            sessionArgs = []

            # This section could be replaced with: varnames = inspect.getargspec(method)[0][1:]
            # but getargspec does a lot more, so this is kind of an optimization.
            code = method.func_code if type(method) is types.FunctionType else method.im_func.func_code
            varnames = code.co_varnames[1:code.co_argcount]

            for varname in varnames:
                if varname[0] == "_":
                    attribute = varname[1:]
                    if not hasattr(self, attribute) and attribute != "session":
                        msg = "Function '%s.%s' declares session argument '%s' which is not found in session '%s'"
                        args = (objectName, method.func_name, attribute, self)
                        raise RuntimeError(msg % args)
                    sessionArgs.append(attribute)
            method.__dict__["sessionArgs"] =  sessionArgs # using setattr() here fails for some reasons.


        if sessionArgs:
            # Cook arguments
            cooked = []
            for attribute in sessionArgs:
                if attribute == "session":
                    cooked.append(self)
                else:
                    cooked.append(getattr(self, attribute))
            args = tuple(cooked + list(args))

        if self.sessionManager.log.level <= logging.DEBUG:
            # Prevent flooding the log with long argument detail by clipping it to MAXCALLINFOLEN chars.
            msg = "Calling %s::%s(*args=%s" % (objectName, method.func_name, args)
            # Only add the keyword arguments if there is enough space left.
            if len(msg) < MAXCALLINFOLEN-50:
                msg += ", **kwargs=%s)" % (kw,)
            if len(msg) > MAXCALLINFOLEN:
                msg = msg[:MAXCALLINFOLEN] +"... CLIPPED"
            self.sessionManager.log.debug(msg)

        # Masquerade session
        tmp = util.GetSession()
        t = stackless.getcurrent()
        t.session = self

        try:
            return method(*args, **kw)
        finally:
            t.session = tmp

    def RegisterCallbackObject(self, cb):
        """Calls 'cb' when session closes with 'self' as an argument.
        Holds a weakref on cb to avoid circular dependencies."""
        self.callbackObjects.append(weakref.ref(cb))


    def UnregisterCallbackObject(self, cb):
        """Removes 'cb' from callback list."""
        self.callbackObjects.remove(cb)

    def SendSessionEvent(self, eventName, *args, **kwargs):
        for wr in self.callbackObjects:
            ob = wr()
            if ob:
                eventFunc = getattr(ob, eventName, None)
                if eventFunc is not None:
                    try:
                        eventFunc(self, *args, **kwargs)
                    except Exception:
                        self.sessionManager.log.exception("Session %s in callback %s", self, ob)
