"""
asynchat SRP authenticated sockets.
(c) alain.spineux@gmail.com

From the original SRPSocket version 1.1 found at 
http://members.tripod.com/professor_tom/archives/srpsocket.html

Secure Remote Passwords.  This is slightly different from the standard
implementation (with regard to the definition of 'u', the authentication
hash, and the fact that the database is a pickle).  Also the default random
number generator is not cryptographically strong.  It may be good enough to
password protect your MUD, if not your bank account.  Note that the passwd
database should not be world readable, or it will be vulnerable to a
dictionary attack (like the standard Unix password file).  See the SRP
distribution at http://srp.stanford.edu/srp/ for more information.
"""


srp_license="""This product uses the 'Secure Remote Password' cryptographic
authentication system developed by Tom Wu (tjw@CS.Stanford.EDU)."""

try:
    from hashlib import sha1 as sha
    sha_new=sha
except ImportError:
    # for python 2.4
    import sha
    sha_new=sha.new

import hmac
import random
import getpass
import pickle
import os
import base64

# New exceptions we raise.

class NoSuchUser(Exception): pass
class ImproperKeyValue(Exception): pass
class AuthFailure(Exception): pass

# Some utility functions:

def random_long(bits):
    """Generate a random long integer with the given number of bits."""

    r = 0L
    chunk = 24
    bchunk = (1 << chunk) - 1
    while bits > 0:
        if bits < chunk:
            bchunk = (1 << bits) - 1
        i = random.randint(0, bchunk)
        r = (r << chunk) + i
        bits = bits - chunk
    return r

def random_string(bytes):
    """Generate a random string with the given number of bytes."""

    r = ''
    for i in range(0, bytes):
        r = r + chr(random.randint(0, 255))
    return r

def string_to_long(s):
    """Convert a string of bytes into a long integer."""

    r = 0L
    for c in s:
        r = (r << 8) + ord(c)
    return r

def long_to_string(i):
    """Convert a long integer into a string of bytes."""

    s = ''
    while i > 0:
        s = chr(i & 255) + s
        i = i >> 8
    return s

def hash(s):
    """Hash a value with some hashing algorithm."""

    if type(s) != type(''):
        s = long_to_string(s)

    return sha_new(s).digest()

def private_key(u, s, p):
    """Given the username, salt, and cleartext password, return the private
    key, which is the long integer form of the hashed arguments."""

    h = hash(s + hash(u + p))
    x = string_to_long(h)
    return x

def encode_long(val):
    s = base64.encodestring(long_to_string(val))
    return s + '\n'

def encode_string(val):
    s = base64.encodestring(val)
    return s + '\n'


class SRP(object):
    # Some constants defining the sizes of various entities.
    
    saltlen = 16    # bytes
    tlen = 128      # bits
    ablen = 128     # bits

    # The prime field to work in, and the base to use.  Note that this must be
    # common to both client and host. (Alternatively, the host can send these
    # values to the client, who should then verify that they are safe.)
    # The first number is a prime p of the form 2q + 1, where q is also prime.
    # The second number is a generator in the field GF(p).

    pflist = [(137656596376486790043182744734961384933899167257744121335064027192370741112305920493080254690601316526576747330553110881621319493425219214435734356437905637147670206858858966652975541347966997276817657605917471296442404150473520316654025988200256062845025470327802138620845134916799507318209468806715548156999L,
              8623462398472349872L)]
    
    _singletons = dict()
    def __new__(cls, pfid=0):
        try:
            return cls._singletons[pfid]
        except KeyError:
            return cls._singletons.setdefault(pfid, super(SRP, cls).__new__(cls))

    
    def __init__(self, pfid=0):
        self.pfid=pfid
        self.n, self.g=self.pflist[self.pfid]

    def client_authenticator(self, K, user, s, A, B, u):
        """ calculate the "proofs": keyed hashes of values used in the computation of the key."""
        return hmac.new(K, hash(self.n) + hash(self.g) + hash(user) + s + `A` + `B` + `u`, sha).digest()
       
    def host_authenticator(self, K, A, m):
        """ calculate the "proofs": keyed hashes of values used in the computation of the key."""
        return hmac.new(K, `A` + m, sha).digest()
    

class UserDB:
    
    def __init__(self, srp=SRP()):
        self.srp=srp

    def create_new_verifier(self, username, password):
        """Given a username, cleartext password, and a prime field, pick a
        random salt and calculate the verifier.  The salt, verifier tuple is
        returned."""
        s = random_string(self.srp.saltlen)
        v = pow(self.srp.g, private_key(username, s, password), self.srp.n)
        return (s, v)

    def set(self, username, password, data=None, delayed=False): 
        raise NotImplementedError

    def get(self, username):
        """if not found raise NoSuchUser"""
        raise NotImplementedError

    def flush(self, force=False):
        raise NotImplementedError

class PickleDB(UserDB):
    
    def __init__(self, filename, srp=SRP()):
        UserDB.__init__(self, srp)
        self.filename=filename
        self.must_be_saved=False
        self.passwd={}
        self.mtime=None
        self.load()
        
    def load(self):
        try:
            f=open(self.filename)
            self.passwd=pickle.load(f)
            f.close()
        except IOError:
            self.passwd={}
            # try to save it
            self.save()
            
        self.mtime=os.path.getmtime(self.filename)

    def refresh(self):
        mtime=os.path.getmtime(self.filename)
        if mtime>self.mtime:
            self.load()
                
    def save(self, filename=None):
        if filename==None:
            filename=self.filename
        f=open(filename, 'w')
        pickle.dump(self.passwd, f)
        f.close()
        self.must_be_saved=False

    # This creates a new entry for the host password database.  In other words,
    # this is called when the user changes his password.
    # Note that when this is done over the network, the channel should be
    # encrypted.  The password should obviously never be sent in the clear, and
    # neither should the salt, verifier pair, as they are vulnerable to a
    # dictionary attack.  For the same reason, the passwd database should not be
    # world readable.
    def set(self, username, password, new_data=None, delayed=False):
        if password:
            salt, verifier=self.create_new_verifier(username, password)
            data=None
        else:
            # this can raise a NoSuchUser exception
            data, salt, verifier, pfid=self.get(username)
            
        if new_data!=None:
            data=new_data

        self.passwd[username] = (data, salt, verifier, self.srp.pfid)
        if not delayed:
            self.save()
        else:
            self.must_be_saved=True

    def get(self, username):
        self.refresh()
        try:
            return self.passwd[username]
        except KeyError:
            raise NoSuchUser, username

    def remove(self, username, silently=True, delayed=False):
        try:
            del self.passwd[username]
        except KeyError:
            if not silently:
                raise NoSuchUser, username
        if not delayed:
            self.save()
        else:
            self.must_be_saved=True

    def flush(self, force=False):
        if self.must_be_saved or force:
            self.save()
    
    
    
class SRPSession:
    """a server session"""
    def __init__(self, server):
        self.server=server

        self.user=self.data=self.A=None
        self.s=self.B=self.u=self.K=self.m=None
        
    def lookup(self, username, A):
        self.username=username
        self.A=A
        self.s, self.B, self.u, self.K, self.m, self.data=self.server.lookup(self.username, self.A)

    def host_authenticator(self):
        return self.server.srp.host_authenticator(self.K, self.A, self.m)

class SRPServer:
    
    def __init__(self, user_db, srp=SRP()):
        self.user_db=user_db
        self.srp=srp

    def lookup(self, user, A):
        """Look the user up in the passwd database, calculate our version of
        the session key, and return it along with a keyed hash of the values
        used in the calculation as proof.  The client must match this proof."""
    
        data, s, v, pfid=self.user_db.get(user)

        assert pfid==self.srp.pfid, 'wrong prime field and base' 
    
        # We don't trust the client, who might be trying to send bogus data in
        # order to break the protocol.
    
        if not 0 < A < self.srp.n:
            raise ImproperKeyValue

        # Pick our random public keys.
        
        while 1:
            b=random_long(self.srp.ablen)
            B=(v + pow(self.srp.g, b, self.srp.n)) % self.srp.n
            if B!=0: 
                break
        u=pow(self.srp.g, random_long(self.srp.tlen), self.srp.n)
    
        # Calculate the (private, shared secret) session key.
    
        t = (A * pow(v, u, self.srp.n)) % self.srp.n
        if t <= 1 or t + 1 == self.srp.n:
            raise ImproperKeyValue  # WeakKeyValue -- could be our fault so retry
        S = pow(t, b, self.srp.n)
        K = hash(S)
    
        # Create the proof using a keyed hash.
    
        m = self.srp.client_authenticator(K, user, s, A, B, u)
    
        return (s, B, u, K, m, data)
        
    def create_session(self):
        return SRPSession(self)

class SRPClient:
    
    def __init__(self, username, passphrase, srp=SRP()):
        
        self.username=username
        self.passphrase=passphrase
        
        # Here we could optionally query the host for the pfid and salt, or
        # indeed the pf itself plus salt.  We'd have to verify that n and g
        # are valid in the latter case, and we need a local copy anyway in the
        # former.
        
        self.srp=srp # self.srp.n, self.srp.g
    
        # Pick a random number and send it to the host, who responds with
        # the user's salt and more random numbers.  Note that in the standard
        # SRP implementation, u is derived from B.

        self.a = random_long(self.srp.ablen)
        self.A = pow(self.srp.g, self.a, self.srp.n)

        self.K=self.m=None

    def client_key(self, s, B, u):
        # We don't trust the host.  Perhaps the host is being spoofed.
        if not 0 < B < self.srp.n:
            raise ImproperKeyValue
    
        # Calculate the shared, secret session key.
    
        x = private_key(self.username, s, self.passphrase)
        v = pow(self.srp.g, x, self.srp.n)
        t = B
        if t < v:
            t = t + self.srp.n
        S = pow(t - v, self.a + u * x, self.srp.n)
        self.K = hash(S)
    
        # Compute the authentication proof.
        # This verifies that we do indeed know the same session key,
        # implying that we knew the correct password (even though the host
        # doesn't know the password!)
    
        self.m = self.srp.client_authenticator(self.K, self.username, s, self.A, B, u)
        
    def host_authenticator(self):
        return self.srp.host_authenticator(self.K, self.A, self.m)

if __name__ == '__main__':
    import sys, os
    if len(sys.argv)<=1:
        print 'usage: %s password_filename' % (os.path.basename(sys.argv[0]), )
        sys.exit(1)
    from cmd import Cmd
    class srpdb(Cmd):
        def __init__(self, filename):
            Cmd.__init__(self)
            self.saved = 1
            self.user_db=PickleDB(filename)
            
        def emptyline(self):
            pass
        def do_EOF(self, arg):
            print
            if not self.saved:
                print 'passwd file not saved; "quit" to abort or "save" first.'
                return
            return 1
        def do_exit(self, arg):
            return 1
        def do_quit(self, arg):
            return 1
        def do_list(self, arg):
            print self.user_db.passwd.keys()
        def do_passwd(self, user):
            password = getpass.getpass('Enter new password for %s: ' % user)
            self.user_db.set(user, password, None, delayed=True)
            self.saved = 0
        def do_del(self, user):
            self.user_db.remove(user, True)
            self.saved = 0
        def do_save(self, arg):
            self.user_db.save()
            self.saved = 1
    
    interp = srpdb(sys.argv[1])
    interp.prompt = "srpdb> "
    interp.cmdloop()

