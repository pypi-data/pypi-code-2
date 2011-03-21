#!/usr/bin/env python
#coding=utf-8

from fetcher import Fetcher, FetcherUtil

engine = Fetcher()

from config import patterns

for kwp, ulist in patterns:
    for u in ulist:
        r = engine.fetch(u)
        if r.code == 200:
            print "fetched", u
            c = FetcherUtil.decode(r.content).lower()
            for kw in kwp:
                if kw.lower() in c:
                    print u, "matched", kw