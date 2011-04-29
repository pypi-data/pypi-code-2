#!/usr/bin/env python
from basebrowser import BaseBrowser
#from request import Request
#from response import Response
from curlwrapper.request import Request as BrowserRequest
from curlwrapper.response import Response as BrowserResponse
import pycurl
import StringIO
import sys
import os
import time
import traceback

class Browser(BaseBrowser): #CURL
    def debug_msg(self, debug_type, debug_msg):
        print "debug(%d): %s" % (debug_type, debug_msg)

    def init_pycurl(self):
        #if using socks4 this is useless anyway
        #self.c.setopt(pycurl.DNS_CACHE_TIMEOUT, 360)
        #self.c.setopt(pycurl.DNS_USE_GLOBAL_CACHE, 1)
        self.c.setopt(pycurl.SSL_VERIFYPEER, 0)
        self.c.setopt(pycurl.SSL_VERIFYHOST, 1)
        self.c.setopt(pycurl.IPRESOLVE, pycurl.IPRESOLVE_V4)
        self.c.setopt(pycurl.TIMEOUT, self.timeout)
        self.c.setopt(pycurl.USERAGENT, self.user_agent)
        self.c.setopt(pycurl.ENCODING, 'gzip, deflate')
        if self.range:
            self.c.setopt(pycurl.RANGE, '0-%s'%(self.range*1024))
        if self.redirect == True:
            self.c.setopt(pycurl.FOLLOWLOCATION, True)
            self.c.setopt(pycurl.MAXREDIRS, 15)
        elif self.redirect == False:
            self.c.setopt(pycurl.FOLLOWLOCATION, False)
            self.c.setopt(pycurl.MAXREDIRS, 0)
        self.c.setopt(pycurl.NOSIGNAL, 1) 
        if hasattr(self, 'veryverbose') and self.veryverbose:
            self.c.setopt(pycurl.DEBUGFUNCTION, self.debug_msg)
            self.c.setopt(pycurl.VERBOSE, 1)
        #self.c.setopt(pycurl.HEADER, 1) # show headers?
        #self.c.setopt(pycurl.HEADER_OUT, True) # show headers? 

    def request(self, r):
        """
        Performs a http request
        """
        try:
            url = r.url.encode('utf-8')
        except UnicodeDecodeError:
            print r.url
        referer = r.referer.encode('utf-8')
        proxy = r.proxy
        tries = r.tries
        #TODO: convert headers to a DICT
        headers = list(set(self.headers))    #deduped copy
        if r.additional_headers:
            headers.extend(r.additional_headers)
            headers = list(set(headers))
        b_response = BrowserResponse()  
        try:
            self.c = pycurl.Curl()
            if tries >= self.retry_limit:
                return BrowserResponse(success=False, 
                            errorMsg="tries greater than " +
                            str(self.retry_limit) + " " + url)
            elif tries > 0:
                #print "retry "  + str(tries) + " " + str(id) + " " + time.strftime("%I:%M:%S %p",time.localtime())
                pass
            tries += 1
            self.c.setopt(pycurl.URL, url)
            if referer != '':
                self.c.setopt(pycurl.REFERER, referer)
            self.init_pycurl()
            if self.has_cookies == True:
                self.c.setopt(pycurl.COOKIEFILE, self.cookie_file_path)
                self.c.setopt(pycurl.COOKIEJAR, self.cookie_file_path)
            if r.cookies != '':
                self.c.setopt(pycurl.COOKIE, r.cookies)
            if r.post != None:
                #print self.post
                
                self.c.setopt(pycurl.POST, 1);
                if type(r.post) != type([]):
                    headers.append('Content-Type: application/x-www-form-urlencoded; charset=UTF-8')
                    self.c.setopt(pycurl.POSTFIELDS, r.post)
                elif r.multipart:
                    #use multipart form
                    #headers.append('Content-Type: application/x-www-form-urlencoded; charset=UTF-8')
                    #had to remove the content type header here for some aspx uploads
                    self.c.setopt(pycurl.HTTPPOST, r.post)
                else:
                    self.c.setopt(pycurl.POSTFIELDS, r.post)  
            """
            #may not need this
            if r.filename != None:
                self.c.setopt(pycurl.UPLOAD, r.post);
                self.c.setopt(pycurl.READFUNCTION, open(r.filename, 'rb').read)
                filesize = os.path.getsize(filename)
                self.c.setopt(pycurl.INFILESIZE, filesize)
            """
            if self.current_proxy != '':
                r.proxy = self.current_proxy
            if r.proxy != None:
                self.c.setopt(pycurl.PROXY, r.proxy)
                #self.c.setopt(pycurl.PROXYTYPE,pycurl.PROXYTYPE_SOCKS4)
                #6 should be socks4a
                if self.proxy_type == "AUTO":
                    self.detect_proxy_type()
                if self.use_proxy_dns and self.proxy_type == "SOCKS4":
                    self.c.setopt(pycurl.PROXYTYPE, 6)
                elif self.proxy_type == "SOCKS4":
                    self.c.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS4)
                elif self.proxy_type == "SOCKS5":
                    self.c.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)
            elif r.proxy == None and self.proxies_only == True:
                return BrowserResponse(success=False, error_msg="alert no proxy")
            self.c.setopt(pycurl.HTTPHEADER, headers)
            self.c.setopt(pycurl.WRITEFUNCTION, b_response.response_buffer.write)
            self.c.setopt(pycurl.HEADERFUNCTION, b_response.raw_headers.write)
            self.c.perform()
            code = self.c.getinfo(pycurl.HTTP_CODE)
            b_response.raw_cookies = self.c.getinfo(pycurl.INFO_COOKIELIST) 
            b_response.response_URI = self.c.getinfo(pycurl.EFFECTIVE_URL)
            b_response.redirect_count = self.c.getinfo(pycurl.REDIRECT_COUNT)
            b_response.redirect_url = self.c.getinfo(pycurl.REDIRECT_URL)
            """print 'T:%.1f L:%.1f C:%.1f R:%.1f' % (c.getinfo(pycurl.TOTAL_TIME),
                    c.getinfo(pycurl.NAMELOOKUP_TIME), 
                    c.getinfo(pycurl.CONNECT_TIME),
                    c.getinfo(pycurl.REDIRECT_TIME),
            )
            """
            self.c.close()
            b_response.set_data(code=code)
            return b_response
        except pycurl.error, e:
            if self.verbose:
                print "pycurl error tries", tries, str(e.args) ,  url, r.proxy
                if e[1] == 'Failed to receive SOCKS4 connect request ack.':
                    print 'could not connect to proxy sleeping 5 seconds'
                    time.sleep(3)
                pass
            #TODO add retry code here
            b_response.error_msg ="raised a \
                            pycurl.error " + str(e.args)
            b_response.error_code = e[0]
        except Exception, e:
            if self.verbose:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print "*** print_tb:"
                traceback.print_tb(exc_traceback, file=sys.stdout)
                print "*** print_exception:"
                traceback.print_exception(exc_type, exc_value, exc_traceback,
                                        file=sys.stdout)
        return b_response


