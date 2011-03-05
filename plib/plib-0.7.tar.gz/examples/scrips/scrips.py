#!/usr/bin/env python
"""
SCRIPS.PY
Copyright (C) 2008-2011 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Script to keep track of prescription refill dates
and send e-mail notifications. Intended to be run
stand-alone as a daily cron job, or to be imported
by scrips-edit.py for editing of the scrips.dat file.
"""

import os
import datetime

from plib import ini
from plib.stdlib import strtodate, strtobool
from plib.classes import TokenConverter

scripsdirname = ".scrips"
scripsdatname = "scrips.dat"


# This is dynamic so changing the above globals will change the
# file name retrieved at run time

def scripsdatfile():
    # First make sure the directory exists (this will allow the
    # file to be created if it doesn't exist)
    dirname = os.path.realpath(os.path.expanduser(os.path.join("~",
        scripsdirname)))
    if not os.path.isdir(dirname):
        os.mkdir(dirname)
    return os.path.join(dirname, scripsdatname)


TMPL = "Rx #%s for %s: last filled on %s for %s days, %s refills remaining%s."


class Scrip(TokenConverter):
    
    turnaround = 5 # lead time for normal refills
    leadtime = 5 # additional time if scrip must be renewed
    
    # This makes data conversion to/from string tokens easier
    converters = [
        ('name', str),
        ('rxnum', str),
        ('filldate', strtodate),
        ('days', int),
        ('refills', int),
        ('submitted', strtobool)]
    
    def duedate(self):
        d = self.days - self.turnaround
        if self.refills < 1:
            d = d - self.leadtime
        return (self.filldate + datetime.timedelta(d))
    
    def due(self):
        return (self.filldate.today() >= self.duedate())
    
    def _duestr(self):
        if self.due():
            if self.submitted:
                return "; Submitted for refill"
            else:
                return "; DUE FOR REFILL"
        else:
            return ""
    
    def __str__(self):
        return TMPL % \
            (self.rxnum, self.name, self.filldate, self.days, self.refills,
                self._duestr())


def scriplist(scripclass=Scrip):
    l = []
    fname = scripsdatfile()
    if os.path.isfile(fname):
        f = open(fname, 'rU')
        try:
            for line in f:
                if line[0] != '#':
                    l.append(scripclass(line.split()))
        finally:
            f.close()
    return l


username = os.getenv('USER')
if not username:
    username = os.getenv('USERNAME')
useraddr = "%s@localhost" % username
optnames = [
    ('fromaddr', useraddr),
    ('toaddr', useraddr),
    ('typestr', "text/plain"),
    ('charsetstr', "us-ascii"),
    ('serverstr', "localhost"),
    ('portnum', "25"),
    ('username', ""),
    ('password', "") ]


class ScripsIniFile(ini.PIniFile):
    _optionlist = [
        ("email", [(optname, ini.INI_STRING, optdefault)
            for optname, optdefault in optnames]),
        ("headers", [("dict", ini.INI_STRING, "{}")]),
        ("pharmacy", [("name", ini.INI_STRING, "Pharmacy")]) ]


inifile = ScripsIniFile("scrips")


if __name__ == "__main__":
    from plib.stdlib.options import parse_options
    
    optlist = (
        ("-d", "--display-only", { 'action': "store_true",
            'dest': "silent",
            'help': "just display scrip status" } ),
        ("-n", "--notify", { 'action': "store_false",
            'dest': "silent", 'default': False,
            'help': "send notification e-mail if scrip is due (default)" } )
        )
    opts, args = parse_options(optlist)
    
    if opts.silent:
        
        print "Display-only mode; will not send notification e-mail."
        
        def do_scrip(s):
            print s
    
    else:
        
        from email.Message import Message
        from email.Utils import formatdate
        import smtplib
        
        def mailstr(s):
            return ("Rx #%s for %s is due for refill as of %s from %s." %
                (s.rxnum, s.name, s.duedate(), inifile.pharmacy_name))
        
        def mailsubjstr(s):
            return "Rx reminder for %s" % s.name
        
        def sendmail(s):
            msg = Message()
            msg['From'] = inifile.email_fromaddr
            msg['To'] = inifile.email_toaddr
            msg['Date'] = formatdate()
            msg['Subject'] = mailsubjstr(s)
            headers = eval(inifile.headers_dict)
            for hname, hvalue in headers.iteritems():
                msg['X-%s' % hname] = hvalue
            msg.set_type(inifile.email_typestr)
            msg.set_payload(mailstr(s), inifile.email_charsetstr)
            server = smtplib.SMTP(
                inifile.email_serverstr, int(inifile.email_portnum))
            server.set_debuglevel(1)
            if inifile.email_username and inifile.email_password:
                server.starttls()
                server.login(inifile.email_username, inifile.email_password)
            server.sendmail(
                inifile.email_fromaddr, [inifile.email_toaddr],
                msg.as_string())
            server.quit()
        
        def do_scrip(s):
            print s
            if s.due() and not s.submitted:
                sendmail(s)
    
    for s in scriplist():
        do_scrip(s)
