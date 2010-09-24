
import urllib
import simplejson
from twisted.protocols.basic import LineOnlyReceiver
from allmydata.scripts.common import get_alias, DEFAULT_ALIAS, escape_path, \
                                     UnknownAliasError
from allmydata.scripts.common_http import do_http, format_http_error
from allmydata.util.encodingutil import quote_output, quote_path

class Checker:
    pass

def _quote_serverid_index_share(serverid, storage_index, sharenum):
    return "server %s, SI %s, shnum %r" % (quote_output(serverid, quotemarks=False),
                                           quote_output(storage_index, quotemarks=False),
                                           sharenum)

def check(options):
    stdout = options.stdout
    stderr = options.stderr
    nodeurl = options['node-url']
    if not nodeurl.endswith("/"):
        nodeurl += "/"
    where = options.where
    try:
        rootcap, path = get_alias(options.aliases, where, DEFAULT_ALIAS)
    except UnknownAliasError, e:
        e.display(stderr)
        return 1
    if path == '/':
        path = ''
    url = nodeurl + "uri/%s" % urllib.quote(rootcap)
    if path:
        url += "/" + escape_path(path)
    # todo: should it end with a slash?
    url += "?t=check&output=JSON"
    if options["verify"]:
        url += "&verify=true"
    if options["repair"]:
        url += "&repair=true"
    if options["add-lease"]:
        url += "&add-lease=true"

    resp = do_http("POST", url)
    if resp.status != 200:
        print >>stderr, format_http_error("ERROR", resp)
        return 1
    jdata = resp.read()
    if options.get("raw"):
        stdout.write(jdata)
        stdout.write("\n")
        return 0
    data = simplejson.loads(jdata)

    if options["repair"]:
        # show repair status
        if data["pre-repair-results"]["results"]["healthy"]:
            summary = "healthy"
        else:
            summary = "not healthy"
        stdout.write("Summary: %s\n" % summary)
        cr = data["pre-repair-results"]["results"]
        stdout.write(" storage index: %s\n" % quote_output(data["storage-index"], quotemarks=False))
        stdout.write(" good-shares: %r (encoding is %r-of-%r)\n"
                     % (cr["count-shares-good"],
                        cr["count-shares-needed"],
                        cr["count-shares-expected"]))
        stdout.write(" wrong-shares: %r\n" % cr["count-wrong-shares"])
        corrupt = cr["list-corrupt-shares"]
        if corrupt:
            stdout.write(" corrupt shares:\n")
            for (serverid, storage_index, sharenum) in corrupt:
                stdout.write("  %s\n" % _quote_serverid_index_share(serverid, storage_index, sharenum))
        if data["repair-attempted"]:
            if data["repair-successful"]:
                stdout.write(" repair successful\n")
            else:
                stdout.write(" repair failed\n")
    else:
        stdout.write("Summary: %s\n" % quote_output(data["summary"], quotemarks=False))
        cr = data["results"]
        stdout.write(" storage index: %s\n" % quote_output(data["storage-index"], quotemarks=False))
        stdout.write(" good-shares: %r (encoding is %r-of-%r)\n"
                     % (cr["count-shares-good"],
                        cr["count-shares-needed"],
                        cr["count-shares-expected"]))
        stdout.write(" wrong-shares: %r\n" % cr["count-wrong-shares"])
        corrupt = cr["list-corrupt-shares"]
        if corrupt:
            stdout.write(" corrupt shares:\n")
            for (serverid, storage_index, sharenum) in corrupt:
                stdout.write("  %s\n" % _quote_serverid_index_share(serverid, storage_index, sharenum))
    return 0


class FakeTransport:
    disconnecting = False

class DeepCheckOutput(LineOnlyReceiver):
    delimiter = "\n"
    def __init__(self, streamer, options):
        self.streamer = streamer
        self.transport = FakeTransport()

        self.verbose = bool(options["verbose"])
        self.stdout = options.stdout
        self.stderr = options.stderr
        self.num_objects = 0
        self.files_healthy = 0
        self.files_unhealthy = 0
        self.in_error = False

    def lineReceived(self, line):
        if self.in_error:
            print >>self.stderr, quote_output(line, quotemarks=False)
            return
        if line.startswith("ERROR:"):
            self.in_error = True
            self.streamer.rc = 1
            print >>self.stderr, quote_output(line, quotemarks=False)
            return

        d = simplejson.loads(line)
        stdout = self.stdout
        if d["type"] not in ("file", "directory"):
            return
        self.num_objects += 1
        # non-verbose means print a progress marker every 100 files
        if self.num_objects % 100 == 0:
            print >>stdout, "%d objects checked.." % self.num_objects
        cr = d["check-results"]
        if cr["results"]["healthy"]:
            self.files_healthy += 1
        else:
            self.files_unhealthy += 1
        if self.verbose:
            # verbose means also print one line per file
            path = d["path"]
            if not path:
                path = ["<root>"]
            summary = cr.get("summary", "Healthy (LIT)")
            print >>stdout, "%s: %s" % (quote_path(path), quote_output(summary, quotemarks=False))

        # always print out corrupt shares
        for shareloc in cr["results"].get("list-corrupt-shares", []):
            (serverid, storage_index, sharenum) = shareloc
            print >>stdout, " corrupt: %s" % _quote_serverid_index_share(serverid, storage_index, sharenum)

    def done(self):
        if self.in_error:
            return
        stdout = self.stdout
        print >>stdout, "done: %d objects checked, %d healthy, %d unhealthy" \
              % (self.num_objects, self.files_healthy, self.files_unhealthy)

class DeepCheckAndRepairOutput(LineOnlyReceiver):
    delimiter = "\n"
    def __init__(self, streamer, options):
        self.streamer = streamer
        self.transport = FakeTransport()

        self.verbose = bool(options["verbose"])
        self.stdout = options.stdout
        self.stderr = options.stderr
        self.num_objects = 0
        self.pre_repair_files_healthy = 0
        self.pre_repair_files_unhealthy = 0
        self.repairs_attempted = 0
        self.repairs_successful = 0
        self.post_repair_files_healthy = 0
        self.post_repair_files_unhealthy = 0
        self.in_error = False

    def lineReceived(self, line):
        if self.in_error:
            print >>self.stderr, quote_output(line, quotemarks=False)
            return
        if line.startswith("ERROR:"):
            self.in_error = True
            self.streamer.rc = 1
            print >>self.stderr, quote_output(line, quotemarks=False)
            return

        d = simplejson.loads(line)
        stdout = self.stdout
        if d["type"] not in ("file", "directory"):
            return
        self.num_objects += 1
        # non-verbose means print a progress marker every 100 files
        if self.num_objects % 100 == 0:
            print >>stdout, "%d objects checked.." % self.num_objects
        crr = d["check-and-repair-results"]
        if d["storage-index"]:
            if crr["pre-repair-results"]["results"]["healthy"]:
                was_healthy = True
                self.pre_repair_files_healthy += 1
            else:
                was_healthy = False
                self.pre_repair_files_unhealthy += 1
            if crr["post-repair-results"]["results"]["healthy"]:
                self.post_repair_files_healthy += 1
            else:
                self.post_repair_files_unhealthy += 1
        else:
            # LIT file
            was_healthy = True
            self.pre_repair_files_healthy += 1
            self.post_repair_files_healthy += 1
        if crr["repair-attempted"]:
            self.repairs_attempted += 1
            if crr["repair-successful"]:
                self.repairs_successful += 1
        if self.verbose:
            # verbose means also print one line per file
            path = d["path"]
            if not path:
                path = ["<root>"]
            # we don't seem to have a summary available, so build one
            if was_healthy:
                summary = "healthy"
            else:
                summary = "not healthy"
            print >>stdout, "%s: %s" % (quote_path(path), summary)

        # always print out corrupt shares
        prr = crr.get("pre-repair-results", {})
        for shareloc in prr.get("results", {}).get("list-corrupt-shares", []):
            (serverid, storage_index, sharenum) = shareloc
            print >>stdout, " corrupt: %s" % _quote_serverid_index_share(serverid, storage_index, sharenum)

        # always print out repairs
        if crr["repair-attempted"]:
            if crr["repair-successful"]:
                print >>stdout, " repair successful"
            else:
                print >>stdout, " repair failed"

    def done(self):
        if self.in_error:
            return
        stdout = self.stdout
        print >>stdout, "done: %d objects checked" % self.num_objects
        print >>stdout, " pre-repair: %d healthy, %d unhealthy" \
              % (self.pre_repair_files_healthy,
                 self.pre_repair_files_unhealthy)
        print >>stdout, " %d repairs attempted, %d successful, %d failed" \
              % (self.repairs_attempted,
                 self.repairs_successful,
                 (self.repairs_attempted - self.repairs_successful))
        print >>stdout, " post-repair: %d healthy, %d unhealthy" \
              % (self.post_repair_files_healthy,
                 self.post_repair_files_unhealthy)

class DeepCheckStreamer(LineOnlyReceiver):

    def run(self, options):
        stdout = options.stdout
        stderr = options.stderr
        self.rc = 0
        self.options = options
        nodeurl = options['node-url']
        if not nodeurl.endswith("/"):
            nodeurl += "/"
        self.nodeurl = nodeurl
        where = options.where
        try:
            rootcap, path = get_alias(options.aliases, where, DEFAULT_ALIAS)
        except UnknownAliasError, e:
            e.display(stderr)
            return 1
        if path == '/':
            path = ''
        url = nodeurl + "uri/%s" % urllib.quote(rootcap)
        if path:
            url += "/" + escape_path(path)
        # todo: should it end with a slash?
        url += "?t=stream-deep-check"
        if options["verify"]:
            url += "&verify=true"
        if options["repair"]:
            url += "&repair=true"
            output = DeepCheckAndRepairOutput(self, options)
        else:
            output = DeepCheckOutput(self, options)
        if options["add-lease"]:
            url += "&add-lease=true"
        resp = do_http("POST", url)
        if resp.status not in (200, 302):
            print >>stderr, format_http_error("ERROR", resp)
            return 1

        # use Twisted to split this into lines
        while True:
            chunk = resp.read(100)
            if not chunk:
                break
            if self.options["raw"]:
                stdout.write(chunk)
            else:
                output.dataReceived(chunk)
        if not self.options["raw"]:
            output.done()
        return self.rc

def deepcheck(options):
    return DeepCheckStreamer().run(options)
