# -*- coding: utf-8 -*-  
"""
    tabledown.tdxls
    ~~~~~~~~~~~~~~~~

    Extract data from spreadsheets to collections(lists, and hashes), and vice versa.

    :copyright: Copyright 2011 by T.C. Chou.
    :license: BSD, see LICENSE for details.
"""
from tabledown import *

try:
    import xlrd, xlwt
except ImportError:
    raise TDException("The xlrd/xlwt package is needed to run the TDXls.")

from xlrd import open_workbook,cellname
from xlwt import Utils, Workbook
#import xlutils.copy  

import re
from types import FunctionType, DictType, IntType, ListType, StringType, UnicodeType
from operator import itemgetter
from itertools import groupby

defines={
    '_':['master','contacts'],
    'master':{'company':['A^1',u'公司'],'area':['A^2',u'地區'],'country':['A^3',u'國別']},
    'contacts':{
        '*':{'name':['A1',u'姓名',lambda x:x['value'] is not None], 'sex':['B1',u'性別'], ':':None},
        'methods':{
            '*':{'type':['B1',u'連絡',lambda x:x['value'] in [u'手機',u'公司',u'住家',u'分機']], 'data':['C1',u'資料']}
        }
    },
}

rawdata={
    'master': {'company': u'\u7532\u516c\u53f8'},
    'contacts': [
        {'methods': [{'data': u'0912-123456', 'type': u'\u624b\u6a5f'},
            {'data': u'#1010', 'type': u'\u5206\u6a5f'},
            {'data': u'\u65b0\u7af9\u5e02', 'type': u'\u516c\u53f8'},
            {'data': u'\u6843\u5712', 'type': u'\u4f4f\u5bb6'}], 
            'name': u'\u7532\u65b9', 'sex': u'\u7537'},
        {'methods': [{'data': u'0918-123456', 'type': u'\u624b\u6a5f'},
            {'data': u'#2020', 'type': u'\u5206\u6a5f'},
            {'data': u'\u53f0\u5317\u5e02', 'type': u'\u516c\u53f8'}],
            'name': u'\u4e59\u65b9', 'sex': u'\u5973'}
        ]
}

re_ssloc = re.compile(r'([A-Z]+|@)(\^*)([0-9]+)(\^*)')

def str2rowcell(str):
    loc = re_ssloc.match(str).groups()
    rc_str = loc[0]+loc[2]
    rc = (Utils.cell_to_rowcol2(rc_str))
    rc_n = (len(loc[3]), len(loc[1]))
    return (rc, rc_n)

class TDMetaCell(object):
    def __init__(self,key,rowcol,to_rowcol=None,next_rowcol=None,name=None,checkit=None):
        self.key = key
        self.rowcol = rowcol
        self.to_rowcol = to_rowcol
        self.next_rowcol = next_rowcol
        self.name = name
        self.checkit = checkit
        self.value = None
    def newData(key, data):
        if (type(data) is ListType and len(data) in [2,3]) or (type(data) is StringType and data.find(':')==-1):
            checkit=None
            if type(data) is ListType:
                data_value=data[0]
                name=data[1]
                if len(data)==3 and type(data[2]) is FunctionType: checkit=data[2]
            else:
                data_value=data
                name=None
            try:
                rc = str2rowcell(data_value)
                return TDMetaCell(key=key,rowcol=rc[0],next_rowcol=rc[1],name=name,checkit=checkit)
            except:
                raise TDException('Invalid data: key(%s), data(%s)' % (key, data_value))
        elif type(data) is StringType and data.find(':')>0:
            data_lst=data.split(':')
            try:
                rc1 = str2rowcell(data_lst[0])
                rc2 = str2rowcell(data_lst[1])
                return TDMetaCell(key=key,rowcol=rc1[0],to_rowcol=rc2[0])
            except:
                raise TDException('Invalid range: key(%s), data(%s)' % (key,data))
        elif key==':':
            if data==None: return TDMetaCell(key=':',rowcol=(-1,-1),to_rowcol=(-1,-1))
            elif type(data) is IntType: return TDMetaCell(key=key,rowcol=(-1,-1),to_rowcol=(data,-1))
            else: raise TDException('Invalid detail range: key(%s), data(%s)' % (key,data))
        else:
            raise TDException('Invalid cell: key(%s), data(%s)' % (key, repr(data)))
    def __repr__(self):
        return """key: %s
    rowcol: %s
    to_rowcol: %s
    next_rowcol: %s
    name: %s
    checkit: %s\n""" % (self.key, self.rowcol, self.to_rowcol, self.next_rowcol, repr(self.name), repr(self.checkit))
    newData = staticmethod(newData)

class TDMetaGroup(object):
    def __init__(self, config_map):
        if type(config_map) is not DictType:
            raise TDException('Invalid config map for master: %s' % config_map)
        self.config_map = config_map
        self.proc_list = []
        self.range = None
        for key in self.config_map:
            tdmc = TDMetaCell.newData(key, self.config_map[key])
            if key==':': self.range = tdmc
            else: self.proc_list.append(tdmc)
        self.proc_list.sort(lambda x,y: cmp(x.rowcol, y.rowcol))
        self.proc_group=groupby(self.proc_list, lambda x:x.rowcol[0])
    def data(self):
        return self.proc_list
    def __repr__(self):
        return repr(self.proc_list)

class TDXls(object):
    def __init__(self, defs):
        self.processDefinitions(defs)
    def dict2xls(self, data, filename):
        book = Workbook()
        sheet = book.add_sheet('Sheet 1')
        self.current_row = -1
        for dkey in self.orders:
            if dkey in self.masters and data.has_key(dkey):
                self.dict2master(sheet, self.pdefs[dkey], data[dkey])
            elif dkey in self.details:
                self.dict2detail(sheet, self.pdefs[dkey], data[dkey])
        book.save(filename)
    def dict2detail_outputTitle(self, sheet, defs):
        cols = 0
        for tdc in defs['*'].proc_list:
            if tdc.name:
                if not self.detailTitle:
                    self.detailTitle = True
                    self.current_row += 1
                row = (self.current_row,0)
                sheet.write(*self.addLoc(row,tdc.rowcol), label=tdc.name)
                cols += 1
        if cols>0: self.current_row += 1
        cdefs_orders = defs.has_key('_') and defs['_'] or [k for k in defs.keys() if k!='*']
        for ckey in cdefs_orders:
            cdefs = defs[ckey]
            if cdefs.has_key('*'): self.dict2detail_outputTitle(sheet, cdefs)
    def dict2detail_outputData(self, sheet, defs, data):
        cdefs_orders = defs.has_key('_') and defs['_'] or [k for k in defs.keys() if k!='*']
        for item in data:
            # output data
            row = (self.current_row,0)
            cols = 0
            for tdc in defs['*'].proc_list:
                if item.has_key(tdc.key):
                    sheet.write(*self.addLoc(row,tdc.rowcol), label=item[tdc.key])
                    cols += 1
            if cols>0: self.current_row += 1
            # process childs
            for ckey in cdefs_orders:
                cdefs = defs[ckey]
                if item.has_key(ckey) and cdefs.has_key('*'):
                    self.dict2detail_outputData(sheet, cdefs, item[ckey])
    def dict2detail(self, sheet, defs, data):
        # outputs detail title
        self.detailTitle = False
        self.dict2detail_outputTitle(sheet, defs)
        self.dict2detail_outputData(sheet, defs, data)
    def dict2master(self, sheet, defs, data):
        for tdc in defs.proc_list:
            if data.has_key(tdc.key):
                if self.current_row<0: self.current_row=0
                row = (self.current_row,0)
                if tdc.next_rowcol is None:
                    _rc = self.addLoc(row,tdc.rowcol)
                else:
                    _rc1 = self.addLoc(row,tdc.rowcol)
                    sheet.write(*_rc1, label=tdc.name)
                    _rc = self.addLoc(_rc1,tdc.next_rowcol)
                sheet.write(*_rc, label=data[tdc.key])
                if _rc[0]>self.current_row: self.current_row=_rc[0]
    def xls2dict(self, filename):
        book = open_workbook(filename, on_demand=True, formatting_info=True)
        rets = {}
        self.current_row = -1
        for sheet_name in book.sheet_names():
            sheet = book.sheet_by_name(sheet_name)
            rets[sheet_name]=self.sheet2dict(sheet)
        return rets
    def sheet2dict(self, sheet):
        rets = {}
        for dkey in self.orders:
            if dkey in self.masters:
                rets[dkey]=self.master2dict(sheet, self.pdefs[dkey])
            elif dkey in self.details:
                n1_dkey_idx = self.orders.index(dkey)+1 # index of next one dkey
                n1_dkey = n1_dkey_idx<len(self.orders) and self.pdefs[n1_dkey_idx] or None
                n1_pdefs = n1_dkey in self.details and self.pdefs[n1_dkey] or None
                r=self.detail2dict(sheet, dkey, self.pdefs[dkey], n1_pdefs)
                if r is not None: rets[dkey]=r
        return rets    
    def isValidDetail(self,sheet,defs,func_only=False,detail2nd=False):
        row = (self.current_row,0)
        rets = True
        matches = 0
        for d in defs.proc_list:
            if type(d) is TDMetaCell:
                x={'value':sheet.cell(*self.addLoc(row,d.rowcol)).value}
                if x['value']=='': x['value']=None
                if not func_only and not detail2nd and type(d.name) is UnicodeType:
                    if x['value']==d.name: matches = matches + 1
                    else: rets = False
                if rets is True and func_only and type(d.checkit) is FunctionType:
                    rets = d.checkit(x)
            if not rets: break
        if matches==len(defs.proc_list): self.current_row = self.current_row + 1 # for detail's column names
        if not detail2nd and not rets and matches==0:
            # skip 2nd detail no title
            return True
        return rets
    def detailRow2dict(self, cnt, sheet, defs):
        row = (self.current_row,0)
        for d in defs.proc_list:
            if type(d) is TDMetaCell:
                value = sheet.cell(*self.addLoc(row,d.rowcol)).value
                cnt[d.key] = value
    def master2dict(self, sheet, defs):
        rets={}
        for tdc in defs.proc_list:
            if tdc.next_rowcol is not None:
                if type(tdc.name) is UnicodeType and sheet.cell(*tdc.rowcol).value==tdc.name:
                    dataLoc = self.addLoc(tdc.rowcol,tdc.next_rowcol)
                    rets[tdc.key]=sheet.cell(*dataLoc).value
                    self.current_row = dataLoc[1]
        self.current_row = self.current_row + 1
        return rets
    def detail2dict_validateTitle(self, sheet, defs, child_orders):
        if not self.isValidDetail(sheet, defs['*'], detail2nd=False): return False
        for ckey in child_orders:
            cdefs = defs[ckey]
            if cdefs.has_key('*') and not self.isValidDetail(sheet, cdefs['*'], detail2nd=False): return False
            cdefs_orders = cdefs.has_key('_') and cdefs['_'] or [k for k in cdefs.keys() if k!='*']
            if cdefs_orders and not self.detail2dict_validateTitle(sheet, cdefs, cdefs_orders): return False
        return True
    def detail2dict(self, sheet, dkey, defs, n1_defs, detail2nd=False):
        child_orders = defs.has_key('_') and defs['_'] or [k for k in defs.keys() if k!='*']
        # check child details
        if not detail2nd and not self.detail2dict_validateTitle(sheet, defs, child_orders): return True
        rets=[]
        drange = defs['*'].range
        c_rets=None
        while self.current_row < sheet.nrows:
            # check: current detail or next one
            if self.isValidDetail(sheet, defs['*'], func_only=True, detail2nd=True):
                c_rets={}
                self.detailRow2dict(c_rets, sheet, defs['*'])
                rets.append(c_rets)
                self.current_row = self.current_row + 1
            elif n1_defs is not None and self.ifValideDetail(sheet, n1_defs):
                break
            elif len(child_orders)==0:
                break
            else:
                # check: detail of childs
                for ckey in child_orders:
                    n1_ckey_idx = child_orders.index(ckey)+1 # index of next one ckey
                    n1_ckey = n1_ckey_idx<len(child_orders) and defs[n1_ckey_idx] or None
                    n1_defs = n1_ckey is not None and defs[n1_ckey] or None
                    r=self.detail2dict(sheet, ckey, defs[ckey], n1_defs, detail2nd=True)
                    if r is not None:
                        c_rets[ckey]=r
        return rets
    def addLoc(self, a, b):
        return (a[0]+b[0],a[1]+b[1])
    def processDetail(self, parent_defs, dkey, ddata):
        for ckey in ddata:
            if ckey=='*':
                parent_defs[ckey]=TDMetaGroup(ddata[ckey])
            else:
                parent_defs[ckey]={}
                self.processDetail(parent_defs[ckey], ckey, ddata[ckey])
    def processDefinitions(self, defs):
        if type(defs) is not DictType:
            raise TDException('Invalid defs: not map')
        elif defs['_']:
            self.pdefs={}
            self.orders=defs['_']
            self.masters=[]
            self.details=[]
            for dkey in defs['_']:
                if not defs.has_key(dkey):
                    raise TDException('Invalid defs: not existed key(%s)' % dkey)
                if type(defs[dkey]) is not DictType:
                    raise TDException('Invalid defs: key(%s) not map' % dkey)
                ddata = defs[dkey]
                if not defs[dkey].has_key('*'):
                    # it's master
                    self.masters.append(dkey)
                    self.pdefs[dkey]=TDMetaGroup(ddata)
                else:
                    # it's detail
                    self.details.append(dkey)
                    self.pdefs[dkey]={}
                    self.processDetail(self.pdefs[dkey], dkey, ddata)

class TD4Contacts(TDXls):
    def __init__(self, name):
        print '..TD4Contacts'
        self.defs = defines
        TDXls.__init__(self, self.defs)

if __name__ == '__main__':
    #m = TDMetaCell.newData('company','')
    #print m
    #m = TDMetaGroup(defines['master'])
    #
    #m = TDMetaGroup(defines['contacts']['*'])
    #print m
    #for k, items in m.proc_group:
    #    print 'Group(%s)' % k
    #    for i in items:
    #        print " ", i
    tdx = TDXls(defines)
    #td4c = TD4Contacts(u"ob-contacts.xls")
    tdx.dict2xls(rawdata, 'output.xls')
    #tdx.xls2dict(u"ob-contacts.xls")
    """
    template = u"ob-contacts.xls"  
    book = open_workbook(template, on_demand=True, formatting_info=True)  
    print book.sheet_names()
    sheet = book.sheet_by_index(0)

    print sheet.name 
    print sheet.nrows
    print sheet.ncols
    
    is_lines = False
    for row_index in range(sheet.nrows):
        for col_index in range(sheet.ncols): 
            print cellname(row_index,col_index),'-', 
            val = sheet.cell(row_index,col_index).value
            if row_index<3:
                if val == u'專案': print 'Project !!!'
            else:
                print val
    #workBook = xlutils.copy.copy(book)  
    #sheet = book.get_sheet(0)  
    #sheet.write(0, 0, 'changed!111')  
    #workBook.save('1.xls')  
    """