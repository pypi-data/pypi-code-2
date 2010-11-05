# -*- coding: utf-8 -*-
from ctypes import util

import ctypes
import const
import os


if os.name == 'nt':
    native = ctypes.cdll.libcurl
else:
    native = ctypes.CDLL(util.find_library('curl'))


def curl_easy_errcheck(result, func, args):
    from pylibcurl.exceptions import CurlError

    if (isinstance(result, int) and result != const.CURLE_OK) or result is None:
        raise CurlError(result)

    return result
    
curl_easy_cleanup = native.curl_easy_cleanup

# curl_easy_duphandle
curl_easy_duphandle = native.curl_easy_duphandle
curl_easy_duphandle.errcheck = curl_easy_errcheck

# curl_easy_escape
curl_easy_escape = native.curl_easy_escape
curl_easy_escape.errcheck = curl_easy_errcheck

# curl_easy_getinfo
curl_easy_getinfo = native.curl_easy_getinfo
curl_easy_getinfo.errcheck = curl_easy_errcheck

# curl_easy_init
curl_easy_init = native.curl_easy_init
curl_easy_init.restype = ctypes.POINTER(ctypes.c_void_p)
curl_easy_init.errcheck = curl_easy_errcheck


# curl_easy_pause
curl_easy_pause = native.curl_easy_pause
curl_easy_pause.errcheck = curl_easy_errcheck

# curl_easy_perform
curl_easy_perform = native.curl_easy_perform
curl_easy_perform.errcheck = curl_easy_errcheck

# curl_easy_recv
curl_easy_recv = native.curl_easy_recv
curl_easy_recv.errcheck = curl_easy_errcheck


curl_easy_reset = native.curl_easy_reset

# curl_easy_send
curl_easy_send = native.curl_easy_send
curl_easy_send.errcheck = curl_easy_errcheck

# curl_easy_setopt
curl_easy_setopt = native.curl_easy_setopt
curl_easy_setopt.errcheck = curl_easy_errcheck

# curl_easy_strerror
curl_easy_strerror = native.curl_easy_strerror
curl_easy_strerror.restype = ctypes.c_char_p


# curl_easy_unescape
curl_easy_unescape = native.curl_easy_unescape
curl_easy_unescape.errcheck = curl_easy_errcheck

#curl_escape (deprecated, do not use)
curl_formadd = native.curl_formadd
curl_formfree = native.curl_formfree
curl_formget = native.curl_formget
curl_free = native.curl_free
curl_getdate = native.curl_getdate
#curl_getenv (deprecated, do not use)

curl_global_cleanup = native.curl_global_cleanup
curl_global_init = native.curl_global_init
curl_global_init_mem = native.curl_global_init_mem

#curl_mprintf (deprecated, do not use)

def curl_multi_errcheck(result, func, args):
    from pylibcurl.exceptions import MultiError

    if (isinstance(result, int) and result not in (const.CURLM_OK, const.CURLM_CALL_MULTI_PERFORM)) or result is None:
        raise MultiError(result)

    return result
    

# curl_multi_add_handle
curl_multi_add_handle = native.curl_multi_add_handle
curl_multi_add_handle.errcheck = curl_multi_errcheck

# curl_multi_assign
curl_multi_assign = native.curl_multi_assign
curl_multi_assign.errcheck = curl_multi_errcheck

# curl_multi_cleanup
curl_multi_cleanup = native.curl_multi_cleanup
curl_multi_cleanup.errcheck = curl_multi_errcheck

# curl_multi_fdset
curl_multi_fdset = native.curl_multi_fdset
curl_multi_fdset.errcheck = curl_multi_errcheck

# info_read
curl_multi_info_read = native.curl_multi_info_read
curl_multi_info_read.restype = ctypes.POINTER(const.CURLMsg)
curl_multi_info_read.errcheck = curl_multi_errcheck


# curl_multi_init
curl_multi_init = native.curl_multi_init
curl_multi_init.restype = ctypes.POINTER(ctypes.c_void_p)
curl_multi_init.errcheck = curl_multi_errcheck

# curl_multi_perform
curl_multi_perform = native.curl_multi_perform
curl_multi_perform.errcheck = curl_multi_errcheck

# curl_multi_remove_handle
curl_multi_remove_handle = native.curl_multi_remove_handle
curl_multi_remove_handle.errcheck = curl_multi_errcheck

# curl_multi_setopt
curl_multi_setopt = native.curl_multi_setopt
curl_multi_setopt.errcheck = curl_multi_errcheck

# curl_multi_socket_action
curl_multi_socket_action = native.curl_multi_socket_action
curl_multi_socket_action.errcheck = curl_multi_errcheck

curl_multi_strerror = native.curl_multi_strerror
curl_multi_strerror.restype = ctypes.c_char_p

# curl_multi_timeout 
curl_multi_timeout = native.curl_multi_timeout
curl_multi_timeout.errcheck = curl_multi_errcheck


# Share

def curl_share_errcheck(result, func, args):
    from pylibcurl.exceptions import ShareError

    if (isinstance(result, int) and result != const.CURLSHE_OK) or result is None:
        raise ShareError(result)
        
    return result

# curl_share_cleanup 
curl_share_cleanup = native.curl_share_cleanup
curl_share_cleanup.errcheck = curl_share_errcheck 

# curl_share_init
curl_share_init = native.curl_share_init
curl_share_init.restype = ctypes.POINTER(ctypes.c_void_p)
curl_share_init.errcheck = curl_share_errcheck 

# curl_share_setopt
curl_share_setopt = native.curl_share_setopt
curl_share_setopt.errcheck = curl_share_errcheck

# curl_share_strerror
curl_share_strerror = native.curl_share_strerror
curl_share_strerror.restype = ctypes.c_char_p





curl_slist_append = native.curl_slist_append
curl_slist_free_all = native.curl_slist_free_all

#curl_strequal (deprecated, do not use)
#curl_strnequal (deprecated, do not use)
#curl_unescape (deprecated, do not use)

curl_version = native.curl_version
curl_version.restype = ctypes.c_char_p

curl_version_info = native.curl_version_info
curl_version_info.restype = ctypes.POINTER(const.curl_version_info_data)


def slist2list(obj):
    _list = []

    while obj:
        if obj.data:
            _list.append(obj.data)
        try:
            obj = obj.next.contents
        except ValueError:
            break
        
    return _list


def list2slist(_list):
    slist = const.curl_slist()
    nlist = slist
    for i in xrange(len(_list)):
        nlist.data = _list[i]
        if i < len(_list) - 1:
            nlist.next = ctypes.pointer(const.curl_slist())
            nlist = nlist.next.contents

    return slist

def list2pointer_slist(_list):
    slist = None
    for v in _list:
        slist = native.curl_slist_append(slist, v)

    return slist

    


