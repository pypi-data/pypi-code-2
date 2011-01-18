from email.message import Message
import subprocess
import urllib2

from ckanext.amqp import Listener

log = __import__("logging").getLogger("link_checker")

class Checker(Listener):
    defaults = Listener.defaults.copy()
    defaults.update({
        "queue": "link_checker",
        "routing_key": "Package",
        })
    def check_url(self, url):
        log.debug("checking %s" % url)
        try:
            fp = urllib2.urlopen(url)
            fp.read()
            fp.close()
            status, message = fp.code, fp.msg
        except Exception, e:
            status = -1
            message = "%s(%s)" % (
                e.__class__.__name__,
                ", ".join(e.args)
                )
        return status, message
    
    def process(self, data, message):
        package = data["payload"]
        broken = []
        for resource in package["resources"]:
            url = resource["url"]
            status, message = self.check_url(url)
            if status < 200 or status > 299:
                broken.append((url, status, message))
        if broken:
            return self.complain(package, broken)

    def complain(self, package, broken):
        # TODO: get strings like CKAN and email from/to
        # from the config file
        message = u"""
Dear package maintainers and administrators,

I am the URL checking program for CKAN and I have noticed that
one or more of the online resources for the package below
appear to be broken. Please take some time to check this out
and fix them.

    Package:       %(name)s
    Package Title: %(title)s
    Package URL:   %(ckan_url)s

The resources that appear to be broken are:
""" % package
        for report in broken:
            message += u"""
    Resource:      %s
    Status:        %s
    Message:       %s
""" % report

        message += u"""
Thank you very much for taking care to ensure that the information
in CKAN is as accurate as possible.
"""
        assert self.args, "Must give email addresses on the command line for now!"
        email = Message()
        email["From"] = "noreply@ckan.net"
        email["To"] = ", ".join(self.args)
        email["Subject"] = "Broken resources for package %(name)s" % package
        if package["maintainer_email"]:
            email.add_header("Cc", package["maintainer_email"])
        email.set_payload(message, "utf-8")

        log.info("Sending mail about broken links in %(name)s" % package)
        proc = subprocess.Popen(("/usr/sbin/sendmail", "-t"), stdin=subprocess.PIPE)
        proc.stdin.write(email.as_string())
        proc.stdin.close()
        proc.stdin = None
        proc.wait()
        
def checker():
    Checker().command()
