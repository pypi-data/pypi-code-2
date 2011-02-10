
import re
import time

log_re = re.compile(
    r'^(?P<remote_addr>("[^"]+"|[^\s]+))'
    r" -"
    r" (?P<remote_user>[^\s]+)"
    r" \[(?P<time>[^\]]+)\]"
    r'\s+"(?P<request>[^"]*)"'
    r" (?P<status>[^\s]+)"
    r" (?P<bytes>[^\s]+)"
    r'\s+"(?P<referrer>[^"]*)"'
    r'\s+"(?P<user_agent>[^"]*)"'
    r".*$")

class AccessLogParser(object):
    def __call__(self, line):
        m = log_re.match(line.strip())
        d = m.groupdict()
        d['remote_addr'] = d['remote_addr'].replace('"', '')
        try:
            request = d.pop('request')
            d['method'], d['path'], d['httpver'] = request.split(' ')
        except ValueError:
            d['method'], d['path'], d['httpver'] = None, None, None
        try:
            d['bytes'] = int(d['bytes'])
        except ValueError:
            d['bytes'] = 0
        d['status'] = int(d['status'])
        ts = int(time.mktime(time.strptime(d.pop('time'), '%d/%b/%Y:%H:%M:%S +0000')))
        return ts, d
