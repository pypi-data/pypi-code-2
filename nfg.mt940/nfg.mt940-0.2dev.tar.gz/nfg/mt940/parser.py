#!/usr/bin/python

# copyright 2011, NET Net Facilities Group BV, support@nfg.nl
# license: GPL-v3

__doc__ = """ Parse MT940 format bank-statements into XML format """

import string
import re
import datetime
from decimal import Decimal

RE61 = re.compile('(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(\D+)([0-9,]+)\D.*')

class Message(object):
    def __init__(self, lines):
        self.TRN = None
        self.REF = None
        self.ACC = None
        self.SEQ = None
        self.BALOPEN = None
        self.BALCLOSE = None
        self.STATEMENT = []
        self.BALCLOSEAVAIL = self.BALFORWAVAIL = None
        lines = [ x.strip() for x in lines ]
        lines = [ re.sub('\s+',' ',x) for x in lines ]
        self.parse(lines)

    def parse(self,lines):
        for line in lines:
            if line.startswith(':20:'):
                self.TRN = line[4:]
                continue
            if line.startswith(':21:'):
                self.REF = line[4:]
                continue
            if line.startswith(':25:'):
                self.ACC = line[4:]
                continue
            if line.startswith(':28:'):
                self.SEQ = line[4:]
                continue
            elif line.startswith(':28C:'):
                self.SEQ = line[5:]
                continue
            if line.startswith(':60F:') or line.startswith(':60M:'):
                i = line[5:]
                cd = i[0]
                dt = datetime.date(2000 + int(i[1:3]), int(i[3:5]), int(i[5:7]))
                cu = i[7:10]
                ba = Decimal(i[10:].replace(',','.'))
                if cd == 'D': ba = -ba
                self.BALOPEN = (dt,cu,ba)
                continue
            if line.startswith(':61:'):
                i = line[4:]
                (y,vm,vd,em,ed,cd,ba) = RE61.match(i).groups()
                
                vdt = datetime.date(2000 + int(y), int(vm), int(vd))
                edt = datetime.date(2000 + int(y), int(em), int(ed))
                ba = Decimal(ba.replace(',','.'))

                self.STATEMENT.append(dict(
                    line = (vdt,edt,cd,ba),
                    description = []
                ))
                continue
            if line.startswith(':86:'):
                self.STATEMENT[-1]['description'].append(line[4:])
                continue
            if line.startswith(':62F:') or line.startswith(':62M'):
                i = line[5:]
                cd = i[0]
                dt = datetime.date(2000 + int(i[1:3]), int(i[3:5]), int(i[5:7]))
                cu = i[7:10]
                ba = Decimal(i[10:].replace(',','.'))
                if cd == 'D': ba = -ba
                self.BALCLOSE = (dt,cu,ba)
                continue
            if line.startswith(':64:'):
                self.BALCLOSEAVAIL = line[4:]
                continue
            if line.startswith(':65:'):
                self.BALFORWAVAIL = line[4:]
                continue
            if not self.STATEMENT:
                raise Exception, line
            self.STATEMENT[-1]['description'].append(line)

    def __repr__(self):
        r = "  <statement>\n"
        r = r + "    <account>%s</account>\n" % self.ACC
        r = r + "    <number>%s</number>\n" % self.SEQ
        r = r + "    <date>%s</date>\n" % self.BALOPEN[0]
        r = r + "    <currency>%s</currency>\n" % self.BALOPEN[1]
        r = r + "    <open>%s</open>\n" % self.BALOPEN[2]
        r = r + "    <close>%s</close>\n" % self.BALCLOSE[2]
        for s in self.STATEMENT:
            cd,ba = s.get('line')[2],s.get('line')[3]
            if cd == 'D': ba = -ba
            r = r + "      <line>\n" 
            r = r + "        <date>%s</date>\n" % s.get('line')[0]
            r = r + "        <amount>%d</amount>\n" % ba
            r = r + "        <description>%s</description>\n" % string.join(s.get('description',' '))
            r = r + "      </line>\n"
        return r + "  </statement>\n"

class MT940(object):
    """ parser for mt940 data """
    
    message_header = None
    message_trailer = '-'

    def __init__(self, data):
        self.rawdata = data
        lines = data.split('\r\n')
        if lines[1] == '940':
            self.message_header = lines[0:3]
        self.createMessages(lines)

    def createMessages(self, lines):
        message = []
        messages = []
        for line in lines:
            if line in self.message_header and not message:
                continue
            if line == self.message_trailer:
                messages.append(Message(message))
                message = []
                continue
            message.append(line)
        self.messages = messages

    def __repr__(self):
        r = "<mt940>\n"
        for m in self.messages:
            r = r + repr(m)
        return r + "</mt940>\n"




