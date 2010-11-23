# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4
# GPL 2009
from __future__ import division
import cookielib
import hashlib
import os
import subprocess
import sys
import time
import urllib2

try:
    import json
except:
    import simplejson as json

from form import MultiPartForm


__all__ = ['Firefogg']
__version__ = 1.0

CHUNK_SIZE = 1024*1024

def firefogg2cmdline(input, output, options = {}):
    _rename = {
        'softTarget': 'soft-target',
        'noUpscaling': 'no-upscaling',
        'twopass': 'two-pass',
        'maxSize': 'max_size',
        'bufferDelay': 'buf-delay',
        'keyframeInterval': 'keyint',
    }
    _flags = [
        'noUpscaling',
        'twopass',
        'softTarget',
        'noaudio',
        'novideo',
    ]
    cmd = ['ffmpeg2theora', '-o', output, input]
    for key in options:
        k = '-%s' % _rename.get(key, key.lower())
        if len(k) > 2:
            k = '-'+k
        if key in _flags:
            if options[key]:
                cmd.append(k)
        else:
            cmd.append(k)
            cmd.append(str(options[key]))
    return cmd


class Firefogg:
    def __init__(self, cj=None, debug=False):
        '''
            param debug boolean, set to true to see debug information
        '''
        self.debug = debug
        if cj:
            self.cj = cj
        else:
            self.cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        urllib2.install_opener(self.opener)

    def json_request(self, url, form):
        try:
            request = urllib2.Request(url)
            request.add_header('User-agent', 'python-firefogg/%s' % __version__)
            body = str(form)
            request.add_header('Content-type', form.get_content_type())
            request.add_header('Content-length', len(body))
            request.add_data(body)
            result = urllib2.urlopen(request).read().strip()
            return json.loads(result)
        except urllib2.HTTPError, e:
            if self.debug:
                if e.code >= 500:
                    with open('/tmp/error.html', 'w') as f:
                        f.write(e.read())
                    os.system('firefox /tmp/error.html')
            result = e.read()
            try:
                result = json.loads(result)
            except:
                result = {'status':{}}
            result['status']['code'] = e.code
            result['status']['text'] = str(e)
            return result

    def upload(self, url, filename, data={}, options=False):
        '''
            param url upload url
            param filename file to upload
            param data dict with data to post for initiate upload
            param options dict if set, filename will be transcoded before upload
            
            return boolean, true upload success, false failed
        '''
        #FIXME: what about encode and upload at the same time?
        if options:
            tmpname = '%s.ogv' % os.path.splitext(filename)[0]
            n = 2
            while os.path.exists(tmpname):
                tmpname = '%s (%d).ogv' % (os.path.splitext(filename)[0], n)
                n +=1
            if not self.encode(filename, tmpname, options):
                return False
            filename = tmpname

        form = MultiPartForm()
        for key in data:
            form.add_field(key, data[key])
        data = self.json_request(url, form)
        if 'uploadUrl' in data:
            uploadUrl = data['uploadUrl']
            f = open(filename)
            fsize = os.stat(filename).st_size
            chunk = f.read(CHUNK_SIZE)
            data = None
            while chunk:
                if f.tell() == fsize:
                    done = 1
                form = MultiPartForm()
                fname = os.path.basename(filename)
                if isinstance(fname, unicode): fname = fname.encode('utf-8')
                form.add_file('chunk', fname, chunk)
                if len(chunk) < CHUNK_SIZE or f.tell() == fsize:
                    form.add_field('done', '1')
                try:
                    data = self.json_request(uploadUrl, form)
                except:
                    if self.debug:
                        print uploadUrl
                        print "failed to send request, will try again in 5 seconds"
                        import traceback
                        traceback.print_exc()
                    data = {'result': -1}
                    time.sleep(5)
                if data and 'status' in data and data['status']['code'] != 200:
                    if self.debug:
                        print "request returned error, will try again in 5 seconds"
                    time.sleep(5)
                elif data and data['result'] == 1:
                    chunk = f.read(CHUNK_SIZE)
            self.result = data
            return data and 'result' in data and data['result'] == 1
        else:
            if self.debug:
                if 'status' in data and data['status']['code'] == 401:
                    print "login required"
                else:
                    print "failed to upload file..."
                    print data
        return False

    def encode(input, output, options, debug=True):
        cmd = firefogg2cmdline(input, output, options)
        if self.debug:
            print cmd
        p = subprocess.Popen(cmd)
        p.wait()
        if self.debug:
            print p.returncode
        return p.returncode == 0
