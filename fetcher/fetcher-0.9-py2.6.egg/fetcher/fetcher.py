#!/usr/bin/env python
#coding=utf-8

__created__ = "2009/09/27"
__author__ = "xlty.0512@gmail.com"
__author__ = "牧唐 杭州"

import urllib, urllib2, urlparse, cookielib
import re, time, sys
import gzip
from cStringIO import StringIO
import logging

class FetcherUtil():
    @staticmethod
    def _fix_url(u):
        """
                        格式化相对地址为绝对地址
        """
        domain = path = None
        s, h, path, _, _ = urlparse.urlsplit(u)
        domain = s + "://" + h
        def _(locate):
            if not locate.lower().startswith("http"):
                if locate.startswith("/"):
                    return domain + locate
                else: 
                    if u.endswith("/"):
                        return u + locate
                    else:
    #                        do diff things
                        r = -1
                        if path: r = path.rfind("/")
                        return domain + (path and r > 0 and path[:r + 1] or "") + locate
            return locate
        return _

    @staticmethod
    def get_content(res):
        """
        gzip 解码
        """
        ce = res.headers.get("Content-Encoding")
        if ce and 'zip' in ce:
            return gzip.GzipFile(fileobj=StringIO(res.read())).read() 
        return res.read()
    
    @staticmethod
    def decode(content, to="utf-8", default=sys.getdefaultencoding()):
        """
                                要安装: http://chardet.feedparser.org/
                                安装命令: easy_install chardet
        """
        enc, confidence = FetcherUtil.charset(content)
        
        if enc == to.lower():
            return content

        if confidence > 0.5:
            return content.decode(enc).encode(to)
        else:
            #没法检测时, 指定系统默认
            return content.decode(default).encode(to)

    @staticmethod
    def charset(content):
        """
                                要安装: http://chardet.feedparser.org/
                                安装命令: easy_install chardet
        """
        import chardet
        cs = chardet.detect(content)
        return cs["encoding"].lower(), cs["confidence"]

class FetchedData():
    def __init__(self, url, code, msg, headers, content):
        self.url = url
        self.code = code
        self.msg = msg
        self.content = content
        self.headers = headers

    def __str__(self):
        return "url: %s, code: %s, content-len: %s" % (self.url, self.code, len(self.content)) 

    def ok(self):
        return self.code == 200

    @classmethod
    def create(clz, response):
        c = None

        #TODO 添加编码检测功能

        if response.code == 200:
            c = FetcherUtil.get_content(response)
        return FetchedData(response.url, response.code, response.msg, response.headers, c)

class Fetcher():
    headers = {}
    headers['User-Agent'] = """Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 GTB6"""
    headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    headers['Accept-Encoding'] = 'gzip,deflate'
    headers['Accept-Language'] = "zh,en-us;q=0.7,en;q=0.3"
    headers['Accept-Charset'] = "ISO-8859-1,utf-8;q=0.7,*;q=0.7"
    headers['Connection'] = "keep-alive"
    headers['Keep-Alive'] = "115"
    headers['Cache-Control'] = "no-cache"

    def _opener(self):
        """
                        构建自动处理httpcookie的opener
        """
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), urllib2.HTTPHandler())
        return opener

    def _wrap(self, url, param=None):
        return urllib2.Request(url, param, self.headers)

    def __init__(self):
        self.opener = self._opener()

    def head(self, url, param=None):
        try:
            ret = self.opener.open(self._wrap(url, param))
            ret.close()
            return ret.headers
        except:
            from traceback import print_exc
            out = StringIO()
            print_exc(file=out)
            logging.error("fetcher err: [%s] [%s]" % (out.getvalue(), url))
            return {"code":1000}

    def fetch(self, url, param=None):
        """
                        抓取给定页面
        """
        try:
            ret = self.opener.open(self._wrap(url, param))
            data = FetchedData.create(ret)
            ret.close()
            return data
        except BaseException, msg:
            from traceback import print_exc
            out = StringIO()
            print_exc(file=out)
            logging.error("fetcher err: [%s] [%s]" % (out.getvalue(), url))
            return FetchedData(url, 1000, msg, None, None)

class ImageFetcher():
    def __init__(self, patterns=".*(png|jpg)$"):
        self.fetcher = Fetcher()
        self.p = re.compile(patterns, re.I)

    def head(self, url):
        s, h, path, _, _ = urlparse.urlsplit(url)
        domain = s + "://" + h
        self.fetcher.headers["Referer"] = domain
        return self.fetcher.head(url)

    def fetchImage(self, url):
        s, h, path, _, _ = urlparse.urlsplit(url)
        domain = s + "://" + h
        self.fetcher.headers["Referer"] = domain
        d = self.fetcher.fetch(url)
        if d.code == 200:
            return StringIO(d.content)
        return None

    def fetch(self, url):
        d = self.fetcher.fetch(url)
        if d.code == 200:
            imgs = re.findall(r"""img\s+src=\s*['"]([^'"<> ]*?)['"]""", d.content, re.I | re.S | re.M)
            return map(FetcherUtil._fix_url(url), filter(lambda u:self.p.match(u), imgs))
        else: return []

if __name__ == "__main__":
    fetcher = Fetcher()
    d = fetcher.fetch("http://www.taobao.com")
    print FetcherUtil.charset(d.content)
#    print FetcherUtil.decode(d.content, "gb2312")
