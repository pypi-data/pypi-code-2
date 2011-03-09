#!/usr/bin/env python
# coding:utf-8

from ctypes import *

libsid = cdll.LoadLibrary("libsidutils.so.0")
SidDatabase = getattr(libsid, "_ZN11SidDatabaseD2Ev")

md5 = getattr(libsid, "_ZN3MD5C1Ev")
md5_gethash = getattr(libsid, "_ZN3MD59getDigestEv")
md5_append = getattr(libsid, "_ZN3MD56appendEPKvi")

