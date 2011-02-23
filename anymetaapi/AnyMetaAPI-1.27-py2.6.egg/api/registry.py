# Copyright (c) 2008,2009  Mediamatic Lab
# See LICENSE for details.

import ConfigParser
import os, sys

from base import AnyMetaException



class AnyMetaRegistryException(Exception):
    pass



class AnyMetaRegistry:

    __instance = None

    cfgfile = None
    config  = None


    @staticmethod
    def getInstance():
        """
        Get the registry singleton, creating it if it's the first
        time.
        """
        if AnyMetaRegistry.__instance is None:
            AnyMetaRegistry.__instance = AnyMetaRegistry()
        return AnyMetaRegistry.__instance


    def __init__(self, cfgfile = None):
        """
        Initializes the registry singleton.
        """
        self.load(cfgfile)


    def load(self, cfgfile):
        if cfgfile is not None:
            self.cfgfile = cfgfile
        else:
            userfile = os.path.expanduser("~/.anymeta")
            if os.path.exists(userfile):
                self.cfgfile = userfile
            elif os.path.exists("/etc/anymeta.conf"):
                self.cfgfile = "/etc/anymeta.conf"
            else:
                # create userfile
                self.cfgfile = userfile
                open(userfile, "w").close()

        defaults = {'c_key': '', 'c_sec': '', 't_key': '', 't_sec': '', 'comment': ''}
        self.config = ConfigParser.ConfigParser(defaults)
        self.config.read([self.cfgfile])


    def get(self, key):
        """
        Get a registry entry from the config file.
        """

        s = self.config.sections()
        if key not in s:
            raise AnyMetaRegistryException("Unknown config section '%s'" % key)

        if self.config.get(key, 'c_key'):
            oauth = {'c_key': self.config.get(key, 'c_key'),
                     'c_sec': self.config.get(key, 'c_sec'),
                     't_key': self.config.get(key, 't_key'),
                     't_sec': self.config.get(key, 't_sec')
                     }
        else:
            oauth = None

        return {'entrypoint': self.config.get(key, 'entrypoint'),
                'oauth': oauth,
                'comment': self.config.get(key, 'comment')}

    def getAll(self):
        """
        Return all registry entries from the config file.
        """
        all = {}
        for k in self.config.sections():
            all[k] = self.get(k)
        return all


    def set(self, key, entrypoint, oauth, comment = ""):
        """
        Set a registry entry in the config file.
        """
        if key not in self.config.sections():
            self.config.add_section(key)

        self.config.set(key, 'entrypoint', entrypoint)
        self.config.set(key, 'comment', comment)

        try:
            self.config.set(key, 'c_key', oauth['c_key'])
            self.config.set(key, 'c_sec', oauth['c_sec'])
            self.config.set(key, 't_key', oauth['t_key'])
            self.config.set(key, 't_sec', oauth['t_sec'])
        except KeyError:
            raise AnyMetaRegistryException('Incomplete oauth data')


    def delete(self, key):
        """
        Delete a registry item from the config file.
        """
        self.config.remove_section(key)


    def save(self):
        """
        Saves the config file to ~/.anymeta.
        """
        fp = open(self.cfgfile, 'w')
        self.config.write(fp)
        fp.close()


    def exists(self, key):
        return key in self.config.sections()


    def register_interactive(self, key, entrypoint, comment = "", c_key = None, c_sec = None, callback = None):
        """
        Convenience function which creates a new OAuth key to use with
        AnyMeta, by doing discovery of the end points, authorizing the
        request interactively (the call prints instructions and
        pauses), and afterwards, saving the key in the registry.
        """
        if self.exists(key):
            print "*** Registration key '%s'  already exists, skipping... ***" % key
            print
            return

        if callback is None:

            def wait_for_url(url):
                print "*" * 60
                print "Please go to the following URL to authorize your request."
                print "When you're done, press ENTER here to finish."
                print
                print ">>> ", url
                print
                print "*" * 60
                sys.stdin.readline()

            callback = wait_for_url

        from discovery import OAuthDiscovery
        import oauth.oauth as oauth
        import httplib, urllib

        sigmethod  = oauth.OAuthSignatureMethod_HMAC_SHA1()
        connection = httplib.HTTPConnection(urllib.splithost(urllib.splittype(entrypoint)[1])[0])
        oauthinfo  = OAuthDiscovery.discover(entrypoint)

        # Create the consumer

        if c_key is None and not 'static_key' in oauthinfo:
            raise AnyMetaRegistryException("No consumer key given and no static consumer key discovered")

        if c_key is not None:
            consumer = oauth.OAuthConsumer(c_key, c_sec)
        else:
            consumer = oauth.OAuthConsumer(oauthinfo['static_key'], '')

        # Get request token
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, http_url=oauthinfo['request_uri'])
        oauth_request.sign_request(sigmethod, consumer, None)
        path = urllib.splithost(urllib.splittype(oauthinfo['request_uri'])[1])[1]
        connection.request(oauth_request.http_method, path, headers=oauth_request.to_header())
        token = oauth.OAuthToken.from_string(connection.getresponse().read())
        connection.close()

        # Authorize request token (interactively)
        oauth_request = oauth.OAuthRequest.from_token_and_callback(token=token, callback=None, http_url=oauthinfo['authorize_uri'])
        url = oauth_request.to_url()

        callback(url)

        oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, token=token, http_url=oauthinfo['access_uri'])
        oauth_request.sign_request(sigmethod, consumer, token)

        path = urllib.splithost(urllib.splittype(oauthinfo['access_uri'])[1])[1]
        connection.request(oauth_request.http_method, path, headers=oauth_request.to_header())
        s = connection.getresponse().read()
        connection.close()

        token = oauth.OAuthToken.from_string(s)

        oauth = {'c_key': consumer.key,
                 'c_sec': consumer.secret,
                 't_key': token.key,
                 't_sec': token.secret }

        print "Saving... ",

        self.set(key, entrypoint, oauth, comment)
        self.save()

        print "done!"



def get():
    """
    Shortcut to call the registry with anymeta.registry.get()
    """
    return AnyMetaRegistry.getInstance()
