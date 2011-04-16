# -*- coding: utf-8 -*-

import urllib

from ibidem.util import workpool

class RetrievingURLOpener(urllib.FancyURLopener):
    X_HTTP_STATUS_CODE = "X-Http-Status-Code"
    X_HTTP_STATUS_MESSAGE = "X-Http-Status-Message"
    version = "UrlRetriever/0.1"

    def http_error_default(self, url, fp, errcode, errmsg, headers):
        print "ERROR downloading %s" % url
        print "errcode: %r, errmsg: %r, headers: %r" % (errcode, errmsg, headers)
        if headers:
            headers[RetrievingURLOpener.X_HTTP_STATUS_CODE] = str(errcode)
            headers[RetrievingURLOpener.X_HTTP_STATUS_MESSAGE] = errmsg
        return urllib.addinfourl(fp, headers, url)
    
    def prompt_user_passwd(self, host, realm):
        raise NotImplementedError()

class DownloadOrder(workpool.WorkOrder):
    def __init__(self, url, target_file=None, result_cb=None, report_cb=None):
        self.url = url
        self.target_file = target_file
        self.result_cb = result_cb
        self.report_cb = report_cb

    def execute(self):
        retriever = RetrievingURLOpener()
        try:
            if callable(self.report_cb):
                filename, headers = retriever.retrieve(self.url, self.target_file, self.report_cb)
            else:
                filename, headers = retriever.retrieve(self.url, self.target_file)
        except IOError, ioe:
            print "IOError while downloading %s: %s" % (self.url, str(ioe))
            filename = None
            headers = None
        if callable(self.result_cb):
            if headers:
                code = int(headers.getheader(RetrievingURLOpener.X_HTTP_STATUS_CODE, "200"))
            else:
                code = 500
            self.result_cb(filename, headers, code)

if __name__ == "__main__":
    import workpool
    def result(filename, headers, code):
        print "***SUCCESS***"
        print "FILENAME"
        print filename
        print "HEADERS"
        print headers
        print "CODE"
        print code
    def error(*args, **kwargs):
        print "***ERROR***"
        print "ARGS"
        print args
        print "KWARGS"
        print kwargs
    wp = workpool.WorkPool(2)
    ap_front = DownloadOrder("http://www.aftenposten.no", "ap_front.html", result_cb=result)
    wp.add(ap_front)
    ibi404 = DownloadOrder("http://ibidem.homeip.net/404-page", result_cb=result)
    wp.add(ibi404)
    wp.join()
