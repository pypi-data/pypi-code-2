import os, time, weakref, itertools
from zope.interface import implements
from twisted.python import failure
from twisted.internet import defer
from twisted.application import service
from foolscap.api import Referenceable, Copyable, RemoteCopy, fireEventually

from allmydata.util.hashutil import file_renewal_secret_hash, \
     file_cancel_secret_hash, bucket_renewal_secret_hash, \
     bucket_cancel_secret_hash, plaintext_hasher, \
     storage_index_hash, plaintext_segment_hasher, convergence_hasher
from allmydata import hashtree, uri
from allmydata.storage.server import si_b2a
from allmydata.immutable import encode
from allmydata.util import base32, dictutil, idlib, log, mathutil
from allmydata.util.happinessutil import servers_of_happiness, \
                                         shares_by_server, merge_peers, \
                                         failure_message
from allmydata.util.assertutil import precondition
from allmydata.util.rrefutil import add_version_to_remote_reference
from allmydata.interfaces import IUploadable, IUploader, IUploadResults, \
     IEncryptedUploadable, RIEncryptedUploadable, IUploadStatus, \
     NoServersError, InsufficientVersionError, UploadUnhappinessError, \
     DEFAULT_MAX_SEGMENT_SIZE
from allmydata.immutable import layout
from pycryptopp.cipher.aes import AES

from cStringIO import StringIO


KiB=1024
MiB=1024*KiB
GiB=1024*MiB
TiB=1024*GiB
PiB=1024*TiB

class HaveAllPeersError(Exception):
    # we use this to jump out of the loop
    pass

# this wants to live in storage, not here
class TooFullError(Exception):
    pass

class UploadResults(Copyable, RemoteCopy):
    implements(IUploadResults)
    # note: don't change this string, it needs to match the value used on the
    # helper, and it does *not* need to match the fully-qualified
    # package/module/class name
    typeToCopy = "allmydata.upload.UploadResults.tahoe.allmydata.com"
    copytype = typeToCopy

    # also, think twice about changing the shape of any existing attribute,
    # because instances of this class are sent from the helper to its client,
    # so changing this may break compatibility. Consider adding new fields
    # instead of modifying existing ones.

    def __init__(self):
        self.timings = {} # dict of name to number of seconds
        self.sharemap = dictutil.DictOfSets() # {shnum: set(serverid)}
        self.servermap = dictutil.DictOfSets() # {serverid: set(shnum)}
        self.file_size = None
        self.ciphertext_fetched = None # how much the helper fetched
        self.uri = None
        self.preexisting_shares = None # count of shares already present
        self.pushed_shares = None # count of shares we pushed


# our current uri_extension is 846 bytes for small files, a few bytes
# more for larger ones (since the filesize is encoded in decimal in a
# few places). Ask for a little bit more just in case we need it. If
# the extension changes size, we can change EXTENSION_SIZE to
# allocate a more accurate amount of space.
EXTENSION_SIZE = 1000
# TODO: actual extensions are closer to 419 bytes, so we can probably lower
# this.

def pretty_print_shnum_to_servers(s):
    return ', '.join([ "sh%s: %s" % (k, '+'.join([idlib.shortnodeid_b2a(x) for x in v])) for k, v in s.iteritems() ])

class PeerTracker:
    def __init__(self, peerid, storage_server,
                 sharesize, blocksize, num_segments, num_share_hashes,
                 storage_index,
                 bucket_renewal_secret, bucket_cancel_secret):
        precondition(isinstance(peerid, str), peerid)
        precondition(len(peerid) == 20, peerid)
        self.peerid = peerid
        self._storageserver = storage_server # to an RIStorageServer
        self.buckets = {} # k: shareid, v: IRemoteBucketWriter
        self.sharesize = sharesize

        wbp = layout.make_write_bucket_proxy(None, sharesize,
                                             blocksize, num_segments,
                                             num_share_hashes,
                                             EXTENSION_SIZE, peerid)
        self.wbp_class = wbp.__class__ # to create more of them
        self.allocated_size = wbp.get_allocated_size()
        self.blocksize = blocksize
        self.num_segments = num_segments
        self.num_share_hashes = num_share_hashes
        self.storage_index = storage_index

        self.renew_secret = bucket_renewal_secret
        self.cancel_secret = bucket_cancel_secret

    def __repr__(self):
        return ("<PeerTracker for peer %s and SI %s>"
                % (idlib.shortnodeid_b2a(self.peerid),
                   si_b2a(self.storage_index)[:5]))

    def query(self, sharenums):
        d = self._storageserver.callRemote("allocate_buckets",
                                           self.storage_index,
                                           self.renew_secret,
                                           self.cancel_secret,
                                           sharenums,
                                           self.allocated_size,
                                           canary=Referenceable())
        d.addCallback(self._got_reply)
        return d

    def ask_about_existing_shares(self):
        return self._storageserver.callRemote("get_buckets",
                                              self.storage_index)

    def _got_reply(self, (alreadygot, buckets)):
        #log.msg("%s._got_reply(%s)" % (self, (alreadygot, buckets)))
        b = {}
        for sharenum, rref in buckets.iteritems():
            bp = self.wbp_class(rref, self.sharesize,
                                self.blocksize,
                                self.num_segments,
                                self.num_share_hashes,
                                EXTENSION_SIZE,
                                self.peerid)
            b[sharenum] = bp
        self.buckets.update(b)
        return (alreadygot, set(b.keys()))


    def abort(self):
        """
        I abort the remote bucket writers for all shares. This is a good idea
        to conserve space on the storage server.
        """
        self.abort_some_buckets(self.buckets.keys())

    def abort_some_buckets(self, sharenums):
        """
        I abort the remote bucket writers for the share numbers in sharenums.
        """
        for sharenum in sharenums:
            if sharenum in self.buckets:
                self.buckets[sharenum].abort()
                del self.buckets[sharenum]


def str_shareloc(shnum, bucketwriter):
    return "%s: %s" % (shnum, idlib.shortnodeid_b2a(bucketwriter._nodeid),)

class Tahoe2PeerSelector(log.PrefixingLogMixin):

    def __init__(self, upload_id, logparent=None, upload_status=None):
        self.upload_id = upload_id
        self.query_count, self.good_query_count, self.bad_query_count = 0,0,0
        # Peers that are working normally, but full.
        self.full_count = 0
        self.error_count = 0
        self.num_peers_contacted = 0
        self.last_failure_msg = None
        self._status = IUploadStatus(upload_status)
        log.PrefixingLogMixin.__init__(self, 'tahoe.immutable.upload', logparent, prefix=upload_id)
        self.log("starting", level=log.OPERATIONAL)

    def __repr__(self):
        return "<Tahoe2PeerSelector for upload %s>" % self.upload_id

    def get_shareholders(self, storage_broker, secret_holder,
                         storage_index, share_size, block_size,
                         num_segments, total_shares, needed_shares,
                         servers_of_happiness):
        """
        @return: (upload_servers, already_peers), where upload_servers is a set of
                 PeerTracker instances that have agreed to hold some shares
                 for us (the shareids are stashed inside the PeerTracker),
                 and already_peers is a dict mapping shnum to a set of peers
                 which claim to already have the share.
        """

        if self._status:
            self._status.set_status("Contacting Peers..")

        self.total_shares = total_shares
        self.servers_of_happiness = servers_of_happiness
        self.needed_shares = needed_shares

        self.homeless_shares = set(range(total_shares))
        self.contacted_peers = [] # peers worth asking again
        self.contacted_peers2 = [] # peers that we have asked again
        self._started_second_pass = False
        self.use_peers = set() # PeerTrackers that have shares assigned to them
        self.preexisting_shares = {} # shareid => set(peerids) holding shareid
        # We don't try to allocate shares to these servers, since they've said
        # that they're incapable of storing shares of the size that we'd want
        # to store. We keep them around because they may have existing shares
        # for this storage index, which we want to know about for accurate
        # servers_of_happiness accounting
        # (this is eventually a list, but it is initialized later)
        self.readonly_peers = None
        # These peers have shares -- any shares -- for our SI. We keep
        # track of these to write an error message with them later.
        self.peers_with_shares = set()

        # this needed_hashes computation should mirror
        # Encoder.send_all_share_hash_trees. We use an IncompleteHashTree
        # (instead of a HashTree) because we don't require actual hashing
        # just to count the levels.
        ht = hashtree.IncompleteHashTree(total_shares)
        num_share_hashes = len(ht.needed_hashes(0, include_leaf=True))

        # figure out how much space to ask for
        wbp = layout.make_write_bucket_proxy(None, share_size, 0, num_segments,
                                             num_share_hashes, EXTENSION_SIZE,
                                             None)
        allocated_size = wbp.get_allocated_size()
        all_peers = storage_broker.get_servers_for_index(storage_index)
        if not all_peers:
            raise NoServersError("client gave us zero peers")

        # filter the list of peers according to which ones can accomodate
        # this request. This excludes older peers (which used a 4-byte size
        # field) from getting large shares (for files larger than about
        # 12GiB). See #439 for details.
        def _get_maxsize(peer):
            (peerid, conn) = peer
            v1 = conn.version["http://allmydata.org/tahoe/protocols/storage/v1"]
            return v1["maximum-immutable-share-size"]
        writable_peers = [peer for peer in all_peers
                          if _get_maxsize(peer) >= allocated_size]
        readonly_peers = set(all_peers[:2*total_shares]) - set(writable_peers)

        # decide upon the renewal/cancel secrets, to include them in the
        # allocate_buckets query.
        client_renewal_secret = secret_holder.get_renewal_secret()
        client_cancel_secret = secret_holder.get_cancel_secret()

        file_renewal_secret = file_renewal_secret_hash(client_renewal_secret,
                                                       storage_index)
        file_cancel_secret = file_cancel_secret_hash(client_cancel_secret,
                                                     storage_index)
        def _make_trackers(peers):
           return [PeerTracker(peerid, conn,
                               share_size, block_size,
                               num_segments, num_share_hashes,
                               storage_index,
                               bucket_renewal_secret_hash(file_renewal_secret,
                                                          peerid),
                               bucket_cancel_secret_hash(file_cancel_secret,
                                                         peerid))
                    for (peerid, conn) in peers]
        self.uncontacted_peers = _make_trackers(writable_peers)
        self.readonly_peers = _make_trackers(readonly_peers)
        # We now ask peers that can't hold any new shares about existing
        # shares that they might have for our SI. Once this is done, we
        # start placing the shares that we haven't already accounted
        # for.
        ds = []
        if self._status and self.readonly_peers:
            self._status.set_status("Contacting readonly peers to find "
                                    "any existing shares")
        for peer in self.readonly_peers:
            assert isinstance(peer, PeerTracker)
            d = peer.ask_about_existing_shares()
            d.addBoth(self._handle_existing_response, peer.peerid)
            ds.append(d)
            self.num_peers_contacted += 1
            self.query_count += 1
            self.log("asking peer %s for any existing shares" %
                     (idlib.shortnodeid_b2a(peer.peerid),),
                    level=log.NOISY)
        dl = defer.DeferredList(ds)
        dl.addCallback(lambda ign: self._loop())
        return dl


    def _handle_existing_response(self, res, peer):
        """
        I handle responses to the queries sent by
        Tahoe2PeerSelector._existing_shares.
        """
        if isinstance(res, failure.Failure):
            self.log("%s got error during existing shares check: %s"
                    % (idlib.shortnodeid_b2a(peer), res),
                    level=log.UNUSUAL)
            self.error_count += 1
            self.bad_query_count += 1
        else:
            buckets = res
            if buckets:
                self.peers_with_shares.add(peer)
            self.log("response to get_buckets() from peer %s: alreadygot=%s"
                    % (idlib.shortnodeid_b2a(peer), tuple(sorted(buckets))),
                    level=log.NOISY)
            for bucket in buckets:
                self.preexisting_shares.setdefault(bucket, set()).add(peer)
                self.homeless_shares.discard(bucket)
            self.full_count += 1
            self.bad_query_count += 1


    def _get_progress_message(self):
        if not self.homeless_shares:
            msg = "placed all %d shares, " % (self.total_shares)
        else:
            msg = ("placed %d shares out of %d total (%d homeless), " %
                   (self.total_shares - len(self.homeless_shares),
                    self.total_shares,
                    len(self.homeless_shares)))
        return (msg + "want to place shares on at least %d servers such that "
                      "any %d of them have enough shares to recover the file, "
                      "sent %d queries to %d peers, "
                      "%d queries placed some shares, %d placed none "
                      "(of which %d placed none due to the server being"
                      " full and %d placed none due to an error)" %
                        (self.servers_of_happiness, self.needed_shares,
                         self.query_count, self.num_peers_contacted,
                         self.good_query_count, self.bad_query_count,
                         self.full_count, self.error_count))


    def _loop(self):
        if not self.homeless_shares:
            merged = merge_peers(self.preexisting_shares, self.use_peers)
            effective_happiness = servers_of_happiness(merged)
            if self.servers_of_happiness <= effective_happiness:
                msg = ("server selection successful for %s: %s: pretty_print_merged: %s, "
                    "self.use_peers: %s, self.preexisting_shares: %s") \
                        % (self, self._get_progress_message(),
                        pretty_print_shnum_to_servers(merged),
                        [', '.join([str_shareloc(k,v) for k,v in p.buckets.iteritems()])
                            for p in self.use_peers],
                        pretty_print_shnum_to_servers(self.preexisting_shares))
                self.log(msg, level=log.OPERATIONAL)
                return (self.use_peers, self.preexisting_shares)
            else:
                # We're not okay right now, but maybe we can fix it by
                # redistributing some shares. In cases where one or two
                # servers has, before the upload, all or most of the
                # shares for a given SI, this can work by allowing _loop
                # a chance to spread those out over the other peers,
                delta = self.servers_of_happiness - effective_happiness
                shares = shares_by_server(self.preexisting_shares)
                # Each server in shares maps to a set of shares stored on it.
                # Since we want to keep at least one share on each server
                # that has one (otherwise we'd only be making
                # the situation worse by removing distinct servers),
                # each server has len(its shares) - 1 to spread around.
                shares_to_spread = sum([len(list(sharelist)) - 1
                                        for (server, sharelist)
                                        in shares.items()])
                if delta <= len(self.uncontacted_peers) and \
                   shares_to_spread >= delta:
                    items = shares.items()
                    while len(self.homeless_shares) < delta:
                        # Loop through the allocated shares, removing
                        # one from each server that has more than one
                        # and putting it back into self.homeless_shares
                        # until we've done this delta times.
                        server, sharelist = items.pop()
                        if len(sharelist) > 1:
                            share = sharelist.pop()
                            self.homeless_shares.add(share)
                            self.preexisting_shares[share].remove(server)
                            if not self.preexisting_shares[share]:
                                del self.preexisting_shares[share]
                            items.append((server, sharelist))
                        for writer in self.use_peers:
                            writer.abort_some_buckets(self.homeless_shares)
                    return self._loop()
                else:
                    # Redistribution won't help us; fail.
                    peer_count = len(self.peers_with_shares)
                    failmsg = failure_message(peer_count,
                                          self.needed_shares,
                                          self.servers_of_happiness,
                                          effective_happiness)
                    servmsgtempl = "server selection unsuccessful for %r: %s (%s), merged=%s"
                    servmsg = servmsgtempl % (
                        self,
                        failmsg,
                        self._get_progress_message(),
                        pretty_print_shnum_to_servers(merged)
                        )
                    self.log(servmsg, level=log.INFREQUENT)
                    return self._failed("%s (%s)" % (failmsg, self._get_progress_message()))

        if self.uncontacted_peers:
            peer = self.uncontacted_peers.pop(0)
            # TODO: don't pre-convert all peerids to PeerTrackers
            assert isinstance(peer, PeerTracker)

            shares_to_ask = set(sorted(self.homeless_shares)[:1])
            self.homeless_shares -= shares_to_ask
            self.query_count += 1
            self.num_peers_contacted += 1
            if self._status:
                self._status.set_status("Contacting Peers [%s] (first query),"
                                        " %d shares left.."
                                        % (idlib.shortnodeid_b2a(peer.peerid),
                                           len(self.homeless_shares)))
            d = peer.query(shares_to_ask)
            d.addBoth(self._got_response, peer, shares_to_ask,
                      self.contacted_peers)
            return d
        elif self.contacted_peers:
            # ask a peer that we've already asked.
            if not self._started_second_pass:
                self.log("starting second pass",
                        level=log.NOISY)
                self._started_second_pass = True
            num_shares = mathutil.div_ceil(len(self.homeless_shares),
                                           len(self.contacted_peers))
            peer = self.contacted_peers.pop(0)
            shares_to_ask = set(sorted(self.homeless_shares)[:num_shares])
            self.homeless_shares -= shares_to_ask
            self.query_count += 1
            if self._status:
                self._status.set_status("Contacting Peers [%s] (second query),"
                                        " %d shares left.."
                                        % (idlib.shortnodeid_b2a(peer.peerid),
                                           len(self.homeless_shares)))
            d = peer.query(shares_to_ask)
            d.addBoth(self._got_response, peer, shares_to_ask,
                      self.contacted_peers2)
            return d
        elif self.contacted_peers2:
            # we've finished the second-or-later pass. Move all the remaining
            # peers back into self.contacted_peers for the next pass.
            self.contacted_peers.extend(self.contacted_peers2)
            self.contacted_peers2[:] = []
            return self._loop()
        else:
            # no more peers. If we haven't placed enough shares, we fail.
            merged = merge_peers(self.preexisting_shares, self.use_peers)
            effective_happiness = servers_of_happiness(merged)
            if effective_happiness < self.servers_of_happiness:
                msg = failure_message(len(self.peers_with_shares),
                                      self.needed_shares,
                                      self.servers_of_happiness,
                                      effective_happiness)
                msg = ("peer selection failed for %s: %s (%s)" % (self,
                                msg,
                                self._get_progress_message()))
                if self.last_failure_msg:
                    msg += " (%s)" % (self.last_failure_msg,)
                self.log(msg, level=log.UNUSUAL)
                return self._failed(msg)
            else:
                # we placed enough to be happy, so we're done
                if self._status:
                    self._status.set_status("Placed all shares")
                msg = ("server selection successful (no more servers) for %s: %s: %s" % (self,
                            self._get_progress_message(), pretty_print_shnum_to_servers(merged)))
                self.log(msg, level=log.OPERATIONAL)
                return (self.use_peers, self.preexisting_shares)

    def _got_response(self, res, peer, shares_to_ask, put_peer_here):
        if isinstance(res, failure.Failure):
            # This is unusual, and probably indicates a bug or a network
            # problem.
            self.log("%s got error during peer selection: %s" % (peer, res),
                    level=log.UNUSUAL)
            self.error_count += 1
            self.bad_query_count += 1
            self.homeless_shares |= shares_to_ask
            if (self.uncontacted_peers
                or self.contacted_peers
                or self.contacted_peers2):
                # there is still hope, so just loop
                pass
            else:
                # No more peers, so this upload might fail (it depends upon
                # whether we've hit servers_of_happiness or not). Log the last
                # failure we got: if a coding error causes all peers to fail
                # in the same way, this allows the common failure to be seen
                # by the uploader and should help with debugging
                msg = ("last failure (from %s) was: %s" % (peer, res))
                self.last_failure_msg = msg
        else:
            (alreadygot, allocated) = res
            self.log("response to allocate_buckets() from peer %s: alreadygot=%s, allocated=%s"
                    % (idlib.shortnodeid_b2a(peer.peerid),
                       tuple(sorted(alreadygot)), tuple(sorted(allocated))),
                    level=log.NOISY)
            progress = False
            for s in alreadygot:
                self.preexisting_shares.setdefault(s, set()).add(peer.peerid)
                if s in self.homeless_shares:
                    self.homeless_shares.remove(s)
                    progress = True
                elif s in shares_to_ask:
                    progress = True

            # the PeerTracker will remember which shares were allocated on
            # that peer. We just have to remember to use them.
            if allocated:
                self.use_peers.add(peer)
                progress = True

            if allocated or alreadygot:
                self.peers_with_shares.add(peer.peerid)

            not_yet_present = set(shares_to_ask) - set(alreadygot)
            still_homeless = not_yet_present - set(allocated)

            if progress:
                # They accepted at least one of the shares that we asked
                # them to accept, or they had a share that we didn't ask
                # them to accept but that we hadn't placed yet, so this
                # was a productive query
                self.good_query_count += 1
            else:
                self.bad_query_count += 1
                self.full_count += 1

            if still_homeless:
                # In networks with lots of space, this is very unusual and
                # probably indicates an error. In networks with peers that
                # are full, it is merely unusual. In networks that are very
                # full, it is common, and many uploads will fail. In most
                # cases, this is obviously not fatal, and we'll just use some
                # other peers.

                # some shares are still homeless, keep trying to find them a
                # home. The ones that were rejected get first priority.
                self.homeless_shares |= still_homeless
                # Since they were unable to accept all of our requests, so it
                # is safe to assume that asking them again won't help.
            else:
                # if they *were* able to accept everything, they might be
                # willing to accept even more.
                put_peer_here.append(peer)

        # now loop
        return self._loop()


    def _failed(self, msg):
        """
        I am called when peer selection fails. I first abort all of the
        remote buckets that I allocated during my unsuccessful attempt to
        place shares for this file. I then raise an
        UploadUnhappinessError with my msg argument.
        """
        for peer in self.use_peers:
            assert isinstance(peer, PeerTracker)

            peer.abort()

        raise UploadUnhappinessError(msg)


class EncryptAnUploadable:
    """This is a wrapper that takes an IUploadable and provides
    IEncryptedUploadable."""
    implements(IEncryptedUploadable)
    CHUNKSIZE = 50*1024

    def __init__(self, original, log_parent=None):
        self.original = IUploadable(original)
        self._log_number = log_parent
        self._encryptor = None
        self._plaintext_hasher = plaintext_hasher()
        self._plaintext_segment_hasher = None
        self._plaintext_segment_hashes = []
        self._encoding_parameters = None
        self._file_size = None
        self._ciphertext_bytes_read = 0
        self._status = None

    def set_upload_status(self, upload_status):
        self._status = IUploadStatus(upload_status)
        self.original.set_upload_status(upload_status)

    def log(self, *args, **kwargs):
        if "facility" not in kwargs:
            kwargs["facility"] = "upload.encryption"
        if "parent" not in kwargs:
            kwargs["parent"] = self._log_number
        return log.msg(*args, **kwargs)

    def get_size(self):
        if self._file_size is not None:
            return defer.succeed(self._file_size)
        d = self.original.get_size()
        def _got_size(size):
            self._file_size = size
            if self._status:
                self._status.set_size(size)
            return size
        d.addCallback(_got_size)
        return d

    def get_all_encoding_parameters(self):
        if self._encoding_parameters is not None:
            return defer.succeed(self._encoding_parameters)
        d = self.original.get_all_encoding_parameters()
        def _got(encoding_parameters):
            (k, happy, n, segsize) = encoding_parameters
            self._segment_size = segsize # used by segment hashers
            self._encoding_parameters = encoding_parameters
            self.log("my encoding parameters: %s" % (encoding_parameters,),
                     level=log.NOISY)
            return encoding_parameters
        d.addCallback(_got)
        return d

    def _get_encryptor(self):
        if self._encryptor:
            return defer.succeed(self._encryptor)

        d = self.original.get_encryption_key()
        def _got(key):
            e = AES(key)
            self._encryptor = e

            storage_index = storage_index_hash(key)
            assert isinstance(storage_index, str)
            # There's no point to having the SI be longer than the key, so we
            # specify that it is truncated to the same 128 bits as the AES key.
            assert len(storage_index) == 16  # SHA-256 truncated to 128b
            self._storage_index = storage_index
            if self._status:
                self._status.set_storage_index(storage_index)
            return e
        d.addCallback(_got)
        return d

    def get_storage_index(self):
        d = self._get_encryptor()
        d.addCallback(lambda res: self._storage_index)
        return d

    def _get_segment_hasher(self):
        p = self._plaintext_segment_hasher
        if p:
            left = self._segment_size - self._plaintext_segment_hashed_bytes
            return p, left
        p = plaintext_segment_hasher()
        self._plaintext_segment_hasher = p
        self._plaintext_segment_hashed_bytes = 0
        return p, self._segment_size

    def _update_segment_hash(self, chunk):
        offset = 0
        while offset < len(chunk):
            p, segment_left = self._get_segment_hasher()
            chunk_left = len(chunk) - offset
            this_segment = min(chunk_left, segment_left)
            p.update(chunk[offset:offset+this_segment])
            self._plaintext_segment_hashed_bytes += this_segment

            if self._plaintext_segment_hashed_bytes == self._segment_size:
                # we've filled this segment
                self._plaintext_segment_hashes.append(p.digest())
                self._plaintext_segment_hasher = None
                self.log("closed hash [%d]: %dB" %
                         (len(self._plaintext_segment_hashes)-1,
                          self._plaintext_segment_hashed_bytes),
                         level=log.NOISY)
                self.log(format="plaintext leaf hash [%(segnum)d] is %(hash)s",
                         segnum=len(self._plaintext_segment_hashes)-1,
                         hash=base32.b2a(p.digest()),
                         level=log.NOISY)

            offset += this_segment


    def read_encrypted(self, length, hash_only):
        # make sure our parameters have been set up first
        d = self.get_all_encoding_parameters()
        # and size
        d.addCallback(lambda ignored: self.get_size())
        d.addCallback(lambda ignored: self._get_encryptor())
        # then fetch and encrypt the plaintext. The unusual structure here
        # (passing a Deferred *into* a function) is needed to avoid
        # overflowing the stack: Deferreds don't optimize out tail recursion.
        # We also pass in a list, to which _read_encrypted will append
        # ciphertext.
        ciphertext = []
        d2 = defer.Deferred()
        d.addCallback(lambda ignored:
                      self._read_encrypted(length, ciphertext, hash_only, d2))
        d.addCallback(lambda ignored: d2)
        return d

    def _read_encrypted(self, remaining, ciphertext, hash_only, fire_when_done):
        if not remaining:
            fire_when_done.callback(ciphertext)
            return None
        # tolerate large length= values without consuming a lot of RAM by
        # reading just a chunk (say 50kB) at a time. This only really matters
        # when hash_only==True (i.e. resuming an interrupted upload), since
        # that's the case where we will be skipping over a lot of data.
        size = min(remaining, self.CHUNKSIZE)
        remaining = remaining - size
        # read a chunk of plaintext..
        d = defer.maybeDeferred(self.original.read, size)
        # N.B.: if read() is synchronous, then since everything else is
        # actually synchronous too, we'd blow the stack unless we stall for a
        # tick. Once you accept a Deferred from IUploadable.read(), you must
        # be prepared to have it fire immediately too.
        d.addCallback(fireEventually)
        def _good(plaintext):
            # and encrypt it..
            # o/' over the fields we go, hashing all the way, sHA! sHA! sHA! o/'
            ct = self._hash_and_encrypt_plaintext(plaintext, hash_only)
            ciphertext.extend(ct)
            self._read_encrypted(remaining, ciphertext, hash_only,
                                 fire_when_done)
        def _err(why):
            fire_when_done.errback(why)
        d.addCallback(_good)
        d.addErrback(_err)
        return None

    def _hash_and_encrypt_plaintext(self, data, hash_only):
        assert isinstance(data, (tuple, list)), type(data)
        data = list(data)
        cryptdata = []
        # we use data.pop(0) instead of 'for chunk in data' to save
        # memory: each chunk is destroyed as soon as we're done with it.
        bytes_processed = 0
        while data:
            chunk = data.pop(0)
            self.log(" read_encrypted handling %dB-sized chunk" % len(chunk),
                     level=log.NOISY)
            bytes_processed += len(chunk)
            self._plaintext_hasher.update(chunk)
            self._update_segment_hash(chunk)
            # TODO: we have to encrypt the data (even if hash_only==True)
            # because pycryptopp's AES-CTR implementation doesn't offer a
            # way to change the counter value. Once pycryptopp acquires
            # this ability, change this to simply update the counter
            # before each call to (hash_only==False) _encryptor.process()
            ciphertext = self._encryptor.process(chunk)
            if hash_only:
                self.log("  skipping encryption", level=log.NOISY)
            else:
                cryptdata.append(ciphertext)
            del ciphertext
            del chunk
        self._ciphertext_bytes_read += bytes_processed
        if self._status:
            progress = float(self._ciphertext_bytes_read) / self._file_size
            self._status.set_progress(1, progress)
        return cryptdata


    def get_plaintext_hashtree_leaves(self, first, last, num_segments):
        # this is currently unused, but will live again when we fix #453
        if len(self._plaintext_segment_hashes) < num_segments:
            # close out the last one
            assert len(self._plaintext_segment_hashes) == num_segments-1
            p, segment_left = self._get_segment_hasher()
            self._plaintext_segment_hashes.append(p.digest())
            del self._plaintext_segment_hasher
            self.log("closing plaintext leaf hasher, hashed %d bytes" %
                     self._plaintext_segment_hashed_bytes,
                     level=log.NOISY)
            self.log(format="plaintext leaf hash [%(segnum)d] is %(hash)s",
                     segnum=len(self._plaintext_segment_hashes)-1,
                     hash=base32.b2a(p.digest()),
                     level=log.NOISY)
        assert len(self._plaintext_segment_hashes) == num_segments
        return defer.succeed(tuple(self._plaintext_segment_hashes[first:last]))

    def get_plaintext_hash(self):
        h = self._plaintext_hasher.digest()
        return defer.succeed(h)

    def close(self):
        return self.original.close()

class UploadStatus:
    implements(IUploadStatus)
    statusid_counter = itertools.count(0)

    def __init__(self):
        self.storage_index = None
        self.size = None
        self.helper = False
        self.status = "Not started"
        self.progress = [0.0, 0.0, 0.0]
        self.active = True
        self.results = None
        self.counter = self.statusid_counter.next()
        self.started = time.time()

    def get_started(self):
        return self.started
    def get_storage_index(self):
        return self.storage_index
    def get_size(self):
        return self.size
    def using_helper(self):
        return self.helper
    def get_status(self):
        return self.status
    def get_progress(self):
        return tuple(self.progress)
    def get_active(self):
        return self.active
    def get_results(self):
        return self.results
    def get_counter(self):
        return self.counter

    def set_storage_index(self, si):
        self.storage_index = si
    def set_size(self, size):
        self.size = size
    def set_helper(self, helper):
        self.helper = helper
    def set_status(self, status):
        self.status = status
    def set_progress(self, which, value):
        # [0]: chk, [1]: ciphertext, [2]: encode+push
        self.progress[which] = value
    def set_active(self, value):
        self.active = value
    def set_results(self, value):
        self.results = value

class CHKUploader:
    peer_selector_class = Tahoe2PeerSelector

    def __init__(self, storage_broker, secret_holder):
        # peer_selector needs storage_broker and secret_holder
        self._storage_broker = storage_broker
        self._secret_holder = secret_holder
        self._log_number = self.log("CHKUploader starting", parent=None)
        self._encoder = None
        self._results = UploadResults()
        self._storage_index = None
        self._upload_status = UploadStatus()
        self._upload_status.set_helper(False)
        self._upload_status.set_active(True)
        self._upload_status.set_results(self._results)

        # locate_all_shareholders() will create the following attribute:
        # self._peer_trackers = {} # k: shnum, v: instance of PeerTracker

    def log(self, *args, **kwargs):
        if "parent" not in kwargs:
            kwargs["parent"] = self._log_number
        if "facility" not in kwargs:
            kwargs["facility"] = "tahoe.upload"
        return log.msg(*args, **kwargs)

    def start(self, encrypted_uploadable):
        """Start uploading the file.

        Returns a Deferred that will fire with the UploadResults instance.
        """

        self._started = time.time()
        eu = IEncryptedUploadable(encrypted_uploadable)
        self.log("starting upload of %s" % eu)

        eu.set_upload_status(self._upload_status)
        d = self.start_encrypted(eu)
        def _done(uploadresults):
            self._upload_status.set_active(False)
            return uploadresults
        d.addBoth(_done)
        return d

    def abort(self):
        """Call this if the upload must be abandoned before it completes.
        This will tell the shareholders to delete their partial shares. I
        return a Deferred that fires when these messages have been acked."""
        if not self._encoder:
            # how did you call abort() before calling start() ?
            return defer.succeed(None)
        return self._encoder.abort()

    def start_encrypted(self, encrypted):
        """ Returns a Deferred that will fire with the UploadResults instance. """
        eu = IEncryptedUploadable(encrypted)

        started = time.time()
        self._encoder = e = encode.Encoder(self._log_number,
                                           self._upload_status)
        d = e.set_encrypted_uploadable(eu)
        d.addCallback(self.locate_all_shareholders, started)
        d.addCallback(self.set_shareholders, e)
        d.addCallback(lambda res: e.start())
        d.addCallback(self._encrypted_done)
        return d

    def locate_all_shareholders(self, encoder, started):
        peer_selection_started = now = time.time()
        self._storage_index_elapsed = now - started
        storage_broker = self._storage_broker
        secret_holder = self._secret_holder
        storage_index = encoder.get_param("storage_index")
        self._storage_index = storage_index
        upload_id = si_b2a(storage_index)[:5]
        self.log("using storage index %s" % upload_id)
        peer_selector = self.peer_selector_class(upload_id, self._log_number,
                                                 self._upload_status)

        share_size = encoder.get_param("share_size")
        block_size = encoder.get_param("block_size")
        num_segments = encoder.get_param("num_segments")
        k,desired,n = encoder.get_param("share_counts")

        self._peer_selection_started = time.time()
        d = peer_selector.get_shareholders(storage_broker, secret_holder,
                                           storage_index,
                                           share_size, block_size,
                                           num_segments, n, k, desired)
        def _done(res):
            self._peer_selection_elapsed = time.time() - peer_selection_started
            return res
        d.addCallback(_done)
        return d

    def set_shareholders(self, (upload_servers, already_peers), encoder):
        """
        @param upload_servers: a sequence of PeerTracker objects that have agreed to hold some
            shares for us (the shareids are stashed inside the PeerTracker)
        @paran already_peers: a dict mapping sharenum to a set of peerids
                              that claim to already have this share
        """
        msgtempl = "set_shareholders; upload_servers is %s, already_peers is %s"
        values = ([', '.join([str_shareloc(k,v) for k,v in p.buckets.iteritems()])
            for p in upload_servers], already_peers)
        self.log(msgtempl % values, level=log.OPERATIONAL)
        # record already-present shares in self._results
        self._results.preexisting_shares = len(already_peers)

        self._peer_trackers = {} # k: shnum, v: instance of PeerTracker
        for peer in upload_servers:
            assert isinstance(peer, PeerTracker)
        buckets = {}
        servermap = already_peers.copy()
        for peer in upload_servers:
            buckets.update(peer.buckets)
            for shnum in peer.buckets:
                self._peer_trackers[shnum] = peer
                servermap.setdefault(shnum, set()).add(peer.peerid)
        assert len(buckets) == sum([len(peer.buckets) for peer in upload_servers]), \
            "%s (%s) != %s (%s)" % (
                len(buckets),
                buckets,
                sum([len(peer.buckets) for peer in upload_servers]),
                [(p.buckets, p.peerid) for p in upload_servers]
                )
        encoder.set_shareholders(buckets, servermap)

    def _encrypted_done(self, verifycap):
        """ Returns a Deferred that will fire with the UploadResults instance. """
        r = self._results
        for shnum in self._encoder.get_shares_placed():
            peer_tracker = self._peer_trackers[shnum]
            peerid = peer_tracker.peerid
            r.sharemap.add(shnum, peerid)
            r.servermap.add(peerid, shnum)
        r.pushed_shares = len(self._encoder.get_shares_placed())
        now = time.time()
        r.file_size = self._encoder.file_size
        r.timings["total"] = now - self._started
        r.timings["storage_index"] = self._storage_index_elapsed
        r.timings["peer_selection"] = self._peer_selection_elapsed
        r.timings.update(self._encoder.get_times())
        r.uri_extension_data = self._encoder.get_uri_extension_data()
        r.verifycapstr = verifycap.to_string()
        return r

    def get_upload_status(self):
        return self._upload_status

def read_this_many_bytes(uploadable, size, prepend_data=[]):
    if size == 0:
        return defer.succeed([])
    d = uploadable.read(size)
    def _got(data):
        assert isinstance(data, list)
        bytes = sum([len(piece) for piece in data])
        assert bytes > 0
        assert bytes <= size
        remaining = size - bytes
        if remaining:
            return read_this_many_bytes(uploadable, remaining,
                                        prepend_data + data)
        return prepend_data + data
    d.addCallback(_got)
    return d

class LiteralUploader:

    def __init__(self):
        self._results = UploadResults()
        self._status = s = UploadStatus()
        s.set_storage_index(None)
        s.set_helper(False)
        s.set_progress(0, 1.0)
        s.set_active(False)
        s.set_results(self._results)

    def start(self, uploadable):
        uploadable = IUploadable(uploadable)
        d = uploadable.get_size()
        def _got_size(size):
            self._size = size
            self._status.set_size(size)
            self._results.file_size = size
            return read_this_many_bytes(uploadable, size)
        d.addCallback(_got_size)
        d.addCallback(lambda data: uri.LiteralFileURI("".join(data)))
        d.addCallback(lambda u: u.to_string())
        d.addCallback(self._build_results)
        return d

    def _build_results(self, uri):
        self._results.uri = uri
        self._status.set_status("Finished")
        self._status.set_progress(1, 1.0)
        self._status.set_progress(2, 1.0)
        return self._results

    def close(self):
        pass

    def get_upload_status(self):
        return self._status

class RemoteEncryptedUploadable(Referenceable):
    implements(RIEncryptedUploadable)

    def __init__(self, encrypted_uploadable, upload_status):
        self._eu = IEncryptedUploadable(encrypted_uploadable)
        self._offset = 0
        self._bytes_sent = 0
        self._status = IUploadStatus(upload_status)
        # we are responsible for updating the status string while we run, and
        # for setting the ciphertext-fetch progress.
        self._size = None

    def get_size(self):
        if self._size is not None:
            return defer.succeed(self._size)
        d = self._eu.get_size()
        def _got_size(size):
            self._size = size
            return size
        d.addCallback(_got_size)
        return d

    def remote_get_size(self):
        return self.get_size()
    def remote_get_all_encoding_parameters(self):
        return self._eu.get_all_encoding_parameters()

    def _read_encrypted(self, length, hash_only):
        d = self._eu.read_encrypted(length, hash_only)
        def _read(strings):
            if hash_only:
                self._offset += length
            else:
                size = sum([len(data) for data in strings])
                self._offset += size
            return strings
        d.addCallback(_read)
        return d

    def remote_read_encrypted(self, offset, length):
        # we don't support seek backwards, but we allow skipping forwards
        precondition(offset >= 0, offset)
        precondition(length >= 0, length)
        lp = log.msg("remote_read_encrypted(%d-%d)" % (offset, offset+length),
                     level=log.NOISY)
        precondition(offset >= self._offset, offset, self._offset)
        if offset > self._offset:
            # read the data from disk anyways, to build up the hash tree
            skip = offset - self._offset
            log.msg("remote_read_encrypted skipping ahead from %d to %d, skip=%d" %
                    (self._offset, offset, skip), level=log.UNUSUAL, parent=lp)
            d = self._read_encrypted(skip, hash_only=True)
        else:
            d = defer.succeed(None)

        def _at_correct_offset(res):
            assert offset == self._offset, "%d != %d" % (offset, self._offset)
            return self._read_encrypted(length, hash_only=False)
        d.addCallback(_at_correct_offset)

        def _read(strings):
            size = sum([len(data) for data in strings])
            self._bytes_sent += size
            return strings
        d.addCallback(_read)
        return d

    def remote_close(self):
        return self._eu.close()


class AssistedUploader:

    def __init__(self, helper):
        self._helper = helper
        self._log_number = log.msg("AssistedUploader starting")
        self._storage_index = None
        self._upload_status = s = UploadStatus()
        s.set_helper(True)
        s.set_active(True)

    def log(self, *args, **kwargs):
        if "parent" not in kwargs:
            kwargs["parent"] = self._log_number
        return log.msg(*args, **kwargs)

    def start(self, encrypted_uploadable, storage_index):
        """Start uploading the file.

        Returns a Deferred that will fire with the UploadResults instance.
        """
        precondition(isinstance(storage_index, str), storage_index)
        self._started = time.time()
        eu = IEncryptedUploadable(encrypted_uploadable)
        eu.set_upload_status(self._upload_status)
        self._encuploadable = eu
        self._storage_index = storage_index
        d = eu.get_size()
        d.addCallback(self._got_size)
        d.addCallback(lambda res: eu.get_all_encoding_parameters())
        d.addCallback(self._got_all_encoding_parameters)
        d.addCallback(self._contact_helper)
        d.addCallback(self._build_verifycap)
        def _done(res):
            self._upload_status.set_active(False)
            return res
        d.addBoth(_done)
        return d

    def _got_size(self, size):
        self._size = size
        self._upload_status.set_size(size)

    def _got_all_encoding_parameters(self, params):
        k, happy, n, segment_size = params
        # stash these for URI generation later
        self._needed_shares = k
        self._total_shares = n
        self._segment_size = segment_size

    def _contact_helper(self, res):
        now = self._time_contacting_helper_start = time.time()
        self._storage_index_elapsed = now - self._started
        self.log(format="contacting helper for SI %(si)s..",
                 si=si_b2a(self._storage_index), level=log.NOISY)
        self._upload_status.set_status("Contacting Helper")
        d = self._helper.callRemote("upload_chk", self._storage_index)
        d.addCallback(self._contacted_helper)
        return d

    def _contacted_helper(self, (upload_results, upload_helper)):
        now = time.time()
        elapsed = now - self._time_contacting_helper_start
        self._elapsed_time_contacting_helper = elapsed
        if upload_helper:
            self.log("helper says we need to upload", level=log.NOISY)
            self._upload_status.set_status("Uploading Ciphertext")
            # we need to upload the file
            reu = RemoteEncryptedUploadable(self._encuploadable,
                                            self._upload_status)
            # let it pre-compute the size for progress purposes
            d = reu.get_size()
            d.addCallback(lambda ignored:
                          upload_helper.callRemote("upload", reu))
            # this Deferred will fire with the upload results
            return d
        self.log("helper says file is already uploaded", level=log.OPERATIONAL)
        self._upload_status.set_progress(1, 1.0)
        self._upload_status.set_results(upload_results)
        return upload_results

    def _convert_old_upload_results(self, upload_results):
        # pre-1.3.0 helpers return upload results which contain a mapping
        # from shnum to a single human-readable string, containing things
        # like "Found on [x],[y],[z]" (for healthy files that were already in
        # the grid), "Found on [x]" (for files that needed upload but which
        # discovered pre-existing shares), and "Placed on [x]" (for newly
        # uploaded shares). The 1.3.0 helper returns a mapping from shnum to
        # set of binary serverid strings.

        # the old results are too hard to deal with (they don't even contain
        # as much information as the new results, since the nodeids are
        # abbreviated), so if we detect old results, just clobber them.

        sharemap = upload_results.sharemap
        if str in [type(v) for v in sharemap.values()]:
            upload_results.sharemap = None

    def _build_verifycap(self, upload_results):
        self.log("upload finished, building readcap", level=log.OPERATIONAL)
        self._convert_old_upload_results(upload_results)
        self._upload_status.set_status("Building Readcap")
        r = upload_results
        assert r.uri_extension_data["needed_shares"] == self._needed_shares
        assert r.uri_extension_data["total_shares"] == self._total_shares
        assert r.uri_extension_data["segment_size"] == self._segment_size
        assert r.uri_extension_data["size"] == self._size
        r.verifycapstr = uri.CHKFileVerifierURI(self._storage_index,
                                             uri_extension_hash=r.uri_extension_hash,
                                             needed_shares=self._needed_shares,
                                             total_shares=self._total_shares, size=self._size
                                             ).to_string()
        now = time.time()
        r.file_size = self._size
        r.timings["storage_index"] = self._storage_index_elapsed
        r.timings["contacting_helper"] = self._elapsed_time_contacting_helper
        if "total" in r.timings:
            r.timings["helper_total"] = r.timings["total"]
        r.timings["total"] = now - self._started
        self._upload_status.set_status("Finished")
        self._upload_status.set_results(r)
        return r

    def get_upload_status(self):
        return self._upload_status

class BaseUploadable:
    # this is overridden by max_segment_size
    default_max_segment_size = DEFAULT_MAX_SEGMENT_SIZE
    default_encoding_param_k = 3 # overridden by encoding_parameters
    default_encoding_param_happy = 7
    default_encoding_param_n = 10

    max_segment_size = None
    encoding_param_k = None
    encoding_param_happy = None
    encoding_param_n = None

    _all_encoding_parameters = None
    _status = None

    def set_upload_status(self, upload_status):
        self._status = IUploadStatus(upload_status)

    def set_default_encoding_parameters(self, default_params):
        assert isinstance(default_params, dict)
        for k,v in default_params.items():
            precondition(isinstance(k, str), k, v)
            precondition(isinstance(v, int), k, v)
        if "k" in default_params:
            self.default_encoding_param_k = default_params["k"]
        if "happy" in default_params:
            self.default_encoding_param_happy = default_params["happy"]
        if "n" in default_params:
            self.default_encoding_param_n = default_params["n"]
        if "max_segment_size" in default_params:
            self.default_max_segment_size = default_params["max_segment_size"]

    def get_all_encoding_parameters(self):
        if self._all_encoding_parameters:
            return defer.succeed(self._all_encoding_parameters)

        max_segsize = self.max_segment_size or self.default_max_segment_size
        k = self.encoding_param_k or self.default_encoding_param_k
        happy = self.encoding_param_happy or self.default_encoding_param_happy
        n = self.encoding_param_n or self.default_encoding_param_n

        d = self.get_size()
        def _got_size(file_size):
            # for small files, shrink the segment size to avoid wasting space
            segsize = min(max_segsize, file_size)
            # this must be a multiple of 'required_shares'==k
            segsize = mathutil.next_multiple(segsize, k)
            encoding_parameters = (k, happy, n, segsize)
            self._all_encoding_parameters = encoding_parameters
            return encoding_parameters
        d.addCallback(_got_size)
        return d

class FileHandle(BaseUploadable):
    implements(IUploadable)

    def __init__(self, filehandle, convergence):
        """
        Upload the data from the filehandle.  If convergence is None then a
        random encryption key will be used, else the plaintext will be hashed,
        then the hash will be hashed together with the string in the
        "convergence" argument to form the encryption key.
        """
        assert convergence is None or isinstance(convergence, str), (convergence, type(convergence))
        self._filehandle = filehandle
        self._key = None
        self.convergence = convergence
        self._size = None

    def _get_encryption_key_convergent(self):
        if self._key is not None:
            return defer.succeed(self._key)

        d = self.get_size()
        # that sets self._size as a side-effect
        d.addCallback(lambda size: self.get_all_encoding_parameters())
        def _got(params):
            k, happy, n, segsize = params
            f = self._filehandle
            enckey_hasher = convergence_hasher(k, n, segsize, self.convergence)
            f.seek(0)
            BLOCKSIZE = 64*1024
            bytes_read = 0
            while True:
                data = f.read(BLOCKSIZE)
                if not data:
                    break
                enckey_hasher.update(data)
                # TODO: setting progress in a non-yielding loop is kind of
                # pointless, but I'm anticipating (perhaps prematurely) the
                # day when we use a slowjob or twisted's CooperatorService to
                # make this yield time to other jobs.
                bytes_read += len(data)
                if self._status:
                    self._status.set_progress(0, float(bytes_read)/self._size)
            f.seek(0)
            self._key = enckey_hasher.digest()
            if self._status:
                self._status.set_progress(0, 1.0)
            assert len(self._key) == 16
            return self._key
        d.addCallback(_got)
        return d

    def _get_encryption_key_random(self):
        if self._key is None:
            self._key = os.urandom(16)
        return defer.succeed(self._key)

    def get_encryption_key(self):
        if self.convergence is not None:
            return self._get_encryption_key_convergent()
        else:
            return self._get_encryption_key_random()

    def get_size(self):
        if self._size is not None:
            return defer.succeed(self._size)
        self._filehandle.seek(0,2)
        size = self._filehandle.tell()
        self._size = size
        self._filehandle.seek(0)
        return defer.succeed(size)

    def read(self, length):
        return defer.succeed([self._filehandle.read(length)])

    def close(self):
        # the originator of the filehandle reserves the right to close it
        pass

class FileName(FileHandle):
    def __init__(self, filename, convergence):
        """
        Upload the data from the filename.  If convergence is None then a
        random encryption key will be used, else the plaintext will be hashed,
        then the hash will be hashed together with the string in the
        "convergence" argument to form the encryption key.
        """
        assert convergence is None or isinstance(convergence, str), (convergence, type(convergence))
        FileHandle.__init__(self, open(filename, "rb"), convergence=convergence)
    def close(self):
        FileHandle.close(self)
        self._filehandle.close()

class Data(FileHandle):
    def __init__(self, data, convergence):
        """
        Upload the data from the data argument.  If convergence is None then a
        random encryption key will be used, else the plaintext will be hashed,
        then the hash will be hashed together with the string in the
        "convergence" argument to form the encryption key.
        """
        assert convergence is None or isinstance(convergence, str), (convergence, type(convergence))
        FileHandle.__init__(self, StringIO(data), convergence=convergence)

class Uploader(service.MultiService, log.PrefixingLogMixin):
    """I am a service that allows file uploading. I am a service-child of the
    Client.
    """
    implements(IUploader)
    name = "uploader"
    URI_LIT_SIZE_THRESHOLD = 55

    def __init__(self, helper_furl=None, stats_provider=None):
        self._helper_furl = helper_furl
        self.stats_provider = stats_provider
        self._helper = None
        self._all_uploads = weakref.WeakKeyDictionary() # for debugging
        log.PrefixingLogMixin.__init__(self, facility="tahoe.immutable.upload")
        service.MultiService.__init__(self)

    def startService(self):
        service.MultiService.startService(self)
        if self._helper_furl:
            self.parent.tub.connectTo(self._helper_furl,
                                      self._got_helper)

    def _got_helper(self, helper):
        self.log("got helper connection, getting versions")
        default = { "http://allmydata.org/tahoe/protocols/helper/v1" :
                    { },
                    "application-version": "unknown: no get_version()",
                    }
        d = add_version_to_remote_reference(helper, default)
        d.addCallback(self._got_versioned_helper)

    def _got_versioned_helper(self, helper):
        needed = "http://allmydata.org/tahoe/protocols/helper/v1"
        if needed not in helper.version:
            raise InsufficientVersionError(needed, helper.version)
        self._helper = helper
        helper.notifyOnDisconnect(self._lost_helper)

    def _lost_helper(self):
        self._helper = None

    def get_helper_info(self):
        # return a tuple of (helper_furl_or_None, connected_bool)
        return (self._helper_furl, bool(self._helper))


    def upload(self, uploadable, history=None):
        """
        Returns a Deferred that will fire with the UploadResults instance.
        """
        assert self.parent
        assert self.running

        uploadable = IUploadable(uploadable)
        d = uploadable.get_size()
        def _got_size(size):
            default_params = self.parent.get_encoding_parameters()
            precondition(isinstance(default_params, dict), default_params)
            precondition("max_segment_size" in default_params, default_params)
            uploadable.set_default_encoding_parameters(default_params)

            if self.stats_provider:
                self.stats_provider.count('uploader.files_uploaded', 1)
                self.stats_provider.count('uploader.bytes_uploaded', size)

            if size <= self.URI_LIT_SIZE_THRESHOLD:
                uploader = LiteralUploader()
                return uploader.start(uploadable)
            else:
                eu = EncryptAnUploadable(uploadable, self._parentmsgid)
                d2 = defer.succeed(None)
                if self._helper:
                    uploader = AssistedUploader(self._helper)
                    d2.addCallback(lambda x: eu.get_storage_index())
                    d2.addCallback(lambda si: uploader.start(eu, si))
                else:
                    storage_broker = self.parent.get_storage_broker()
                    secret_holder = self.parent._secret_holder
                    uploader = CHKUploader(storage_broker, secret_holder)
                    d2.addCallback(lambda x: uploader.start(eu))

                self._all_uploads[uploader] = None
                if history:
                    history.add_upload(uploader.get_upload_status())
                def turn_verifycap_into_read_cap(uploadresults):
                    # Generate the uri from the verifycap plus the key.
                    d3 = uploadable.get_encryption_key()
                    def put_readcap_into_results(key):
                        v = uri.from_string(uploadresults.verifycapstr)
                        r = uri.CHKFileURI(key, v.uri_extension_hash, v.needed_shares, v.total_shares, v.size)
                        uploadresults.uri = r.to_string()
                        return uploadresults
                    d3.addCallback(put_readcap_into_results)
                    return d3
                d2.addCallback(turn_verifycap_into_read_cap)
                return d2
        d.addCallback(_got_size)
        def _done(res):
            uploadable.close()
            return res
        d.addBoth(_done)
        return d
