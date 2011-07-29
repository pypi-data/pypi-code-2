#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Loic Jaquemet loic.jaquemet+python@gmail.com
#

__author__ = "Loic Jaquemet loic.jaquemet+python@gmail.com"

import ctypes,os, types
from struct import pack,unpack
import logging

from haystack.model import *

def test_import():
  ''' replace c_char_p '''
  if ctypes.c_char_p.__name__ == 'c_char_p':
    print('c_char_p is not our CString')
    return False

  ''' keep orig class '''
  if ctypes.Structure.__name__ == 'Structure':
    print('Structure is not our LoadablesMembers')
    return False
  return True

def test_array2bytes():
  return True

def test_bytes2array():
  return True

def test_pointer2bytes():
  return True


class St(ctypes.Structure):
  _fields_ = [ ('a',ctypes.c_int) ]
  
btype = ctypes.c_int(2)
voidp = ctypes.c_void_p(2)
st = St()
stp = ctypes.pointer(st)
arra1 = (ctypes.c_long *4)()
arra2 = (St *4)()
arra3 = (ctypes.POINTER(St) *4)()
string = ctypes.c_char_p()

def test_isBasicType():
  ret = ( isBasicType(btype) and not isBasicType(st) and not isBasicType(string) 
    and not isBasicType(arra1)
    and not isBasicType(arra2)
    and not isBasicType(arra3)
  ) 
  return ret

def test_isStructType():
  return True
  
def test_isPointerType():
  return True

def test_isBasicTypeArrayType():
  ret = ( not isArrayType(btype) and not isArrayType(st) and not isArrayType(string) 
    and isArrayType(arra1)
    and not isArrayType(arra2)
    and not isArrayType(arra3)
  ) 
  return ret

def test_isArrayType():
  ret = ( not isArrayType(btype) and not isArrayType(st) and not isArrayType(string) 
    and isArrayType(arra1)
    and isArrayType(arra2)
    and isArrayType(arra3)
  ) 
  return ret

def test_isFunctionType():
  return True

def test_isCStringPointer():
  return isCStringPointer(string)

def test_isUnionType():
  return True

def testAll():
  return ( test_import()
  and test_array2bytes()
  and test_bytes2array()
  and test_pointer2bytes()
  and test_isBasicType()
  and test_isStructType()
  and test_isPointerType()
  and test_isBasicTypeArrayType()
  and test_isArrayType()
  and test_isFunctionType()
  and test_isCStringPointer()
  and test_isUnionType()
  )


