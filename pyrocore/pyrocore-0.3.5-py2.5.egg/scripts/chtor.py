""" PyroCore - Metafile Editor.

    Copyright (c) 2010 The PyroScope Project <pyroscope.project@gmail.com>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
import os
import time
import hashlib
import urlparse

from pyrocore.scripts.base import ScriptBase, ScriptBaseWithConfig
from pyrocore import config, error
from pyrocore.util import bencode, metafile


class MetafileChanger(ScriptBaseWithConfig):
    """ Change attributes of a bittorrent metafile.
    """

    # argument description for the usage information
    ARGS_HELP = "<metafile>..."

    # Keys of rTorrent session data
    RT_RESUMT_KEYS = ('libtorrent_resume', 'log_callback', 'err_callback', 'rtorrent')
              

    def add_options(self):
        """ Add program options.
        """
        super(MetafileChanger, self).add_options()

        self.add_bool_option("-n", "--dry-run",
            help="don't write changes to disk, just tell what would happen")
        self.add_bool_option("--no-skip",
            help="do not skip broken metafiles that fail the integrity check")
        self.add_bool_option("-p", "--make-private",
            help="make torrent private (DHT/PEX disabled)")
        self.add_bool_option("-P", "--make-public",
            help="make torrent public (DHT/PEX enabled)")
        self.add_bool_option("-C", "--clean",
            help="remove all non-standard data from metafile outside the info dict")
        self.add_bool_option("-A", "--clean-all",
            help="remove all non-standard data from metafile including the info dict")
        self.add_bool_option("-R", "--clean-rtorrent",
            help="remove all rTorrent session data from metafile")
        # TODO: chtor --tracker
        ##self.add_value_option("-T", "--tracker", "DOMAIN",
        ##    help="filter given torrents for a tracker domain")
        self.add_value_option("-a", "--reannounce", "URL",
            help="set a new announce URL, but only if the old announce URL matches the new one")
        self.add_value_option("--reannounce-all", "URL",
            help="set a new announce URL on ALL given metafiles")
        self.add_bool_option("--no-cross-seed",
            help="when using --reannounce-all, do not add a non-standard field to the info dict ensuring unique info hashes")
        self.add_value_option("--comment", "TEXT",
            help="set a new comment (an empty value deletes it)")
        self.add_bool_option("--bump-date",
            help="set the creation date to right now")
        self.add_bool_option("--no-date",
            help="remove the 'creation date' field")


    def mainloop(self):
        """ The main loop.
        """
        if not self.args:
            self.parser.error("No metafiles given, nothing to do!")

        if self.options.reannounce and self.options.reannounce_all:
            self.parser.error("Confliction options --reannounce and --reannounce-all!")

        # Set filter criteria for metafiles
        filter_url_prefix = None
        if self.options.reannounce:
            # <scheme>://<netloc>/<path>?<query>
            filter_url_prefix = urlparse.urlsplit(self.options.reannounce, allow_fragments=False)
            filter_url_prefix = urlparse.urlunsplit((
                filter_url_prefix.scheme, filter_url_prefix.netloc, '/', '', ''
            ))
            self.LOG.info("Filtering for metafiles with announce URL prefix %r..." % filter_url_prefix)

        if self.options.reannounce_all:
            self.options.reannounce = self.options.reannounce_all
        else:
            # When changing the announce URL w/o changing the domain, don't change the info hash!
            self.options.no_cross_seed = True

        # Resolve tracker alias, if URL doesn't look like an URL
        if self.options.reannounce and not urlparse.urlparse(self.options.reannounce).scheme:
            try:
                _, tracker_url = config.lookup_announce_alias(self.options.reannounce)
            except (KeyError, IndexError):
                raise error.UserError("Unknown tracker alias or bogus URL %r!" % (self.options.reannounce,))
            else:
                self.options.reannounce = tracker_url[0]

        # go through given files
        bad = 0
        changed = 0
        for filename in self.args:
            try:
                # Read and remember current content
                metainfo = bencode.bread(filename)
                old_metainfo = bencode.bencode(metainfo)
            except (KeyError, bencode.BencodeError), exc:
                self.LOG.warning("Skipping bad metafile %r (%s: %s)" % (filename, type(exc).__name__, exc))
                bad += 1
            else:
                # Check metafile integrity
                try:
                    metafile.check_meta(metainfo)
                except ValueError, exc:
                    self.LOG.warn("Metafile %r failed integrity check: %s" % (filename, exc,))
                    if not self.options.no_skip:
                        continue
                
                # Skip any metafiles that don't meet the pre-conditions
                if filter_url_prefix and not metainfo['announce'].startswith(filter_url_prefix):
                    self.LOG.warn("Skipping metafile %r no tracked by %r!" % (filename, filter_url_prefix,))
                    continue

                # Change private flag?
                if self.options.make_private and not metainfo["info"].get("private", 0):
                    self.LOG.info("Setting private flag...")
                    metainfo["info"]["private"] = 1
                if self.options.make_public and metainfo["info"].get("private", 0):
                    self.LOG.info("Clearing private flag...")
                    del metainfo["info"]["private"]

                # Remove non-standard keys?
                if self.options.clean or self.options.clean_all:
                    metafile.clean_meta(metainfo, including_info=self.options.clean_all, log=self.LOG)

                # Clean rTorrent data?
                if self.options.clean_rtorrent:
                    for key in self.RT_RESUMT_KEYS:
                        if key in metainfo:
                            self.LOG.info("Removing key %r..." % (key,))
                            del metainfo[key]

                # Change announce URL?
                if self.options.reannounce:
                    metainfo['announce'] = self.options.reannounce 

                    if not self.options.no_cross_seed:
                        # Enforce unique hash per tracker
                        metainfo["info"]["x_cross_seed"] = hashlib.md5(self.options.reannounce).hexdigest()

                # Change comment or creation date?
                if self.options.comment is not None:
                    if self.options.comment:
                        metainfo["comment"] = self.options.comment
                    elif "comment" in metainfo:
                        del metainfo["comment"]
                if self.options.bump_date:
                    metainfo["creation date"] = long(time.time())
                if self.options.no_date and "creation date" in metainfo:
                    del metainfo["creation date"]

                # Write new metafile, if changed
                new_metainfo = bencode.bencode(metainfo)
                if new_metainfo != old_metainfo:
                    self.LOG.info("Changing %r..." % filename)
                    changed += 1

                    if not self.options.dry_run:
                        # Write to temporary file
                        tempname = os.path.join(
                            os.path.dirname(filename),
                            '.' + os.path.basename(filename),
                        )
                        self.LOG.debug("Writing %r..." % tempname)
                        bencode.bwrite(tempname, metainfo)

                        # Replace existing file
                        if os.name != "posix":
                            # cannot rename to existing target on WIN32
                            os.remove(filename)
                        os.rename(tempname, filename)

        # Print summary
        if changed:
            self.LOG.info("%s %d metafile(s)." % (
                "Would've changed" if self.options.dry_run else "Changed", changed
            ))
        if bad:
            self.LOG.warn("Skipped %d bad metafile(s)!" % (bad))


def run(): #pragma: no cover
    """ The entry point.
    """
    ScriptBase.setup()
    MetafileChanger().run()

