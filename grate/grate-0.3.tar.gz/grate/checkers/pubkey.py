from twisted.python import log
from twisted.conch.ssh import keys
from twisted.conch.checkers import SSHPublicKeyDatabase
from twisted.python.failure import Failure
from twisted.cred.error import UnauthorizedLogin
from pymongo.binary import Binary
from grate.mongo import PublicKey


class GratePublicKeyChecker(SSHPublicKeyDatabase):

    def checkKey(self, creds):
        """
        Defined in SSHPublicKeyDatabase.

        :param creds: The credential object. This should be
            :class:`twisted.cred.credentials.ISSHPrivateKey`.
        :rtype: `string`
        :return: The authenticated user.
        """
        pubkey = keys.Key.fromString(data=creds.blob)
        log.msg('Checking key: %s' % pubkey.fingerprint())
        return self.matchKey(pubkey)

    def _cbRequestAvatarId(self, user, creds):
        """
        Defined in SSHPublicKeyDatabase. This method is called after checkKey.

        :param validKey: This is the result from the call to checkKey.
        :param creds: The credentials. Same one from checkKey.
        :rtype: `string` or :class:`twisted.python.failure.Failure`
        :return: The user or a `Failure` object.
        """
        # the second argument signifies a valid key
        ret = SSHPublicKeyDatabase._cbRequestAvatarId(self, user, creds)
        if isinstance(ret, Failure):
            return ret
        return user

    def matchKey(self, key):
        """
        :param key: The public key.
        :rtype: `string`
        :return: The user that is bound to the public key.
        """
        # must wrap it as a Binary
        blob = Binary(key.blob())
        # query for it.
        p = PublicKey.objects(data=blob).first()
        if not p:
            # we do not have the user on record.
            return Failure(UnauthorizedLogin('unrecognized key'))
        return p.user
