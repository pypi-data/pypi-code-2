#-------------------------------------------------------------------------------
# Name:        main
# Purpose:
#
# Author:      Sergey Pikhovkin (s@pikhovkin.ru)
#
# Created:     27.01.2011
# Copyright:   (c) Sergey Pikhovkin 2011
# Licence:     MIT
#-------------------------------------------------------------------------------
#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import md5, hmac
from hashlib import sha1
import base64
from datetime import datetime
from rfc822 import formatdate, mktime_tz, parsedate_tz
from urllib import urlencode

from client import APIClient
from data import JSON2Obj


class AttributeError(Exception):
    pass


class ClientError(Exception):
    pass


class Megaplan(object):
    """
    """
    debug = False

    HOST = '{account}.megaplan.ru/'
    SIGNATURE = '{method}\n{md5content}\n{contenttype}\n{date}\n{host}{uri}'

    _CommonApi = 'BumsCommonApiV01/'
    _TaskApi = 'BumsTaskApiV01/'
    _StaffApi = 'BumsStaffApiV01/'
    _ProjectApi = 'BumsProjectApiV01/'

    AUTHORIZE = _CommonApi + 'User/'
    COMMENT = _CommonApi + 'Comment/'
    TASK = _TaskApi + 'Task/'
    SEVERITY = _TaskApi + 'Severity/'
    DEPARTMENT = _StaffApi + 'Department/'
    EMPLOYEE = _StaffApi + 'Employee/'
    PROJECT = _ProjectApi + 'Project/'

    code = 'utf-8'

    _FolderType = ('incoming', 'responsible', 'executor', 'owner', 'auditor', 'all',)
    _StatusType = ('actual', 'inprocess', 'new', 'overdue', 'done', 'delayed', 'completed', 'failed', 'any',)
    _ActionType = ('act_accept_task', 'act_reject_task', 'act_accept_work', 'act_reject_work', 'act_done', 'act_pause', 'act_resume', 'act_cancel', 'act_expire', 'act_renew',)
    _SubjectType = ('task', 'project',)
    _OrderType = ('asc', 'desc',)

    @property
    def Account(self):
        return self._Account

    @Account.setter
    def Account(self, account):
        self._Account = account
        self._host = self.HOST.format(account=account)
        self._MPQuery = 'https://{host}'.format(host=self._host) + '{uri}'

    @property
    def Login(self):
        return self._Login

    @Login.setter
    def Login(self, login):
        self._Login = login

    @property
    def Password(self):
        return self._Password

    @Password.setter
    def Password(self, password):
        self._Password = password

    def __init__(self, account='', login='', password=''):
        self.Account, self.Login, self.Password = account, login, password

        self._client = APIClient()
        self._data = str()

        self._AccessId = str()
        self._SecretKey = str()
    # / def __init__(self):

    def TimeAsRfc822(self, dt):
        return formatdate(mktime_tz(parsedate_tz(dt.strftime('%a, %d %b %Y %H:%M:%S'))))
    # /

    def _GetResponseObject(f):
        """
        Decorator
        """
        def wrapper(self):
            obj = JSON2Obj(self._data)
            if 'error' == obj.status['code']:
                if 'message' in obj.status:
                    raise Exception(obj.status['message'])
            return f(self, obj)

        return wrapper
    # / def _GetResponseObject(f):

    @_GetResponseObject
    def _AuthorizeHandle(self, obj):
        self._AccessId = obj.data['AccessId']
        self._SecretKey = obj.data['SecretKey']

        if self.debug:
            self._MPQuery = 'http://{host}'.format(host=self._host) + '{uri}'
    # /

    def _Authorize(self):
        uri = self.AUTHORIZE + 'authorize.api'
        md5pass = md5.new(self.Password).hexdigest()
        params = {
            'Login': self.Login,
            'Password': md5pass
        }
        self._data = \
            self._client.Request(self._MPQuery.format(uri=uri), params)
        self._AuthorizeHandle()

    def _Auth(f):
        def wrapper(self, *args, **kwargs):
            if (self._AccessId == '') or (self._SecretKey == ''):
                self._Authorize()
            return f(self, *args, **kwargs)
        return wrapper
    # /

    def _GetSignature(self, method, uri, params={}):
        self._rfcdate = self.TimeAsRfc822(datetime.now())
        self._md5content = ''
        contenttype = ''
        if 'POST' == method:
            self._md5content = md5.new(urlencode(params)).hexdigest()
            contenttype = 'application/x-www-form-urlencoded'
        sign = {
            'method': method,
            'md5content': self._md5content,
            'contenttype': contenttype,
            'date': self._rfcdate,
            'host': self._host,
            'uri': uri
        }
        q = self.SIGNATURE.format(**sign)
        h = hmac.HMAC(self._SecretKey.encode(self.code), q, sha1)
        return base64.encodestring(h.hexdigest()).strip()
    # /

    def _GetHeaders(self, uri, params={}):
        method = 'GET'
        if params:
            method = 'POST'
        signature = self._GetSignature(method, uri, params)
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.0; ru; rv:1.9.1.7) Gecko/20091221 Firefox/3.5.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru,en-us;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Charset': 'utf-8;q=0.7,*;q=0.7',
            'Keep-Alive': '300',
            'Connection': 'keep-alive',
            'Date': self._rfcdate,
            'X-Authorization': '{0}:{1}'.format(self._AccessId, signature)
        }
        if method == 'GET':
            header['Accept'] = 'application/json'
        elif method == 'POST':
            header['Content-MD5'] = self._md5content
        return header
    # /

    @_GetResponseObject
    def _ResponseHandle(self, obj):
        return obj
    # /

    @_Auth
    def _GetData(self, uri, params={}):
        headers = self._GetHeaders(uri, params)
        self._data = self._client.Request(
            self._MPQuery.format(uri=uri), params=params, headers=headers)
        if self._client.Status in (400, 401, 403, 404, 500):
            raise ClientError(
                '{0} {1}'.format(self._client.Status, self._client.Reason))
        return self._ResponseHandle()
    # /

    def GetTasks(self, Folder='all', Status='any', FavoritesOnly=False, Search=''):
        if (Folder not in self._FolderType) or (Status not in self._StatusType):
            raise AttributeError('Invalid parameter value')

        uri = '{0}list.api?Folder={1}&Status={2}&FavoritesOnly={3}&Search={4}'
        uri = uri.format(self.TASK, Folder, Status, int(FavoritesOnly), Search)
        return self._GetData(uri)
    # /

    def GetTaskCard(self, Id):
        uri = '{0}card.api?Id={1}'.format(self.TASK, Id)
        return self._GetData(uri)
    # /

    def SetTaskCreate(self, **kwargs):
        uri = '{0}create.api'.format(self.TASK)
        return self._GetData(uri, kwargs)
    # /

    def SetTaskEdit(self, Id, **kwargs):
        uri = '{0}edit.api'.format(self.TASK)
        if isinstance(Id, (str, unicode)):
            kwargs['Id'] = Id
        else:
            kwargs['Id'] = str(Id)
        self._GetData(uri, kwargs)
    # /

    def SetTaskAction(self, Id, Action):
        if (Action not in self._ActionType):
            raise AttributeError('Invalid parameter value')

        uri = '{0}action.api'.format(self.TASK)
        params = dict()
        if isinstance(Id, (str, unicode)):
            params['Id'] = Id
        else:
            params['Id'] = str(Id)
        params['Action'] = Action
        return self._GetData(uri, params)
    # /

    def GetTaskAvailableActions(self, Id):
        uri = '{0}availableActions.api?Id={1}'.format(self.TASK, Id)
        return self._GetData(uri)
    # /

    def SetTaskMarkAsFavorite(self, Id, Value=True):
        uri = '{0}markAsFavorite.api'.format(self.TASK)
        params = dict()
        if isinstance(Id, (str, unicode)):
            params['Id'] = Id
        else:
            params['Id'] = str(Id)
        params['Value'] = str(int(Value))
        self._GetData(uri, params)
    # /

    def GetProjects(self, Folder='all', Status='any', FavoritesOnly=False, Search=''):
        if (Folder not in self._FolderType) or (Status not in self._StatusType):
            raise AttributeError('Invalid parameter value')

        uri = '{0}list.api?Folder={1}&Status={2}&FavoritesOnly={3}&Search={4}'
        uri = uri.format(self.PROJECT, Folder, Status, int(FavoritesOnly), Search)
        return self._GetData(uri)
    # /

    def GetProjectCard(self, Id):
        uri = '{0}card.api?Id={1}'.format(self.PROJECT, Id)
        return self._GetData(uri)
    # /

    def SetProjectCreate(self, **kwargs):
        uri = '{0}create.api'.format(self.PROJECT)
        return self._GetData(uri, kwargs)
    # /

    def SetProjectEdit(self, Id, **kwargs):
        uri = '{0}edit.api'.format(self.PROJECT)
        if isinstance(Id, (str, unicode)):
            kwargs['Id'] = Id
        else:
            kwargs['Id'] = str(Id)
        self._GetData(uri, kwargs)
    # /

    def SetProjectAction(self, Id, Action):
        if (Action not in self._ActionType):
            raise AttributeError('Invalid parameter value')

        uri = '{0}action.api'.format(self.PROJECT)
        params = dict()
        if isinstance(Id, (str, unicode)):
            params['Id'] = Id
        else:
            params['Id'] = str(Id)
        params['Action'] = Action
        return self._GetData(uri, params)
    # /

    def SetProjectMarkAsFavorite(self, Id, Value=True):
        uri = '{0}markAsFavorite.api'.format(self.PROJECT)
        params = dict()
        if isinstance(Id, (str, unicode)):
            params['Id'] = Id
        else:
            params['Id'] = str(Id)
        params['Value'] = str(int(Value))
        self._GetData(uri, params)
    # /

    def GetSeverities(self):
        uri = '{0}list.api'.format(self.SEVERITY)
        return self._GetData(uri)
    # /

    def GetEmployees(self, Department=0):
        uri = '{0}list.api?Department={1}'.format(self.EMPLOYEE, Department)
        return self._GetData(uri)
    # /

    def GetEmployeeCard(self, Id):
        uri = '{0}card.api?Id={1}'.format(self.EMPLOYEE, Id)
        return self._GetData(uri)
    # /

    def GetComments(self, SubjectType, SubjectId, Order='asc'):
        if (SubjectType not in self._SubjectType) or \
            (Order not in self._OrderType):
            raise AttributeError('Invalid parameter value')

        uri = '{0}list.api?SubjectType={1}&SubjectId={2}&Order={3}'
        uri = uri.format(self.COMMENT, SubjectType, SubjectId, Order)
        return self._GetData(uri)
    # /

    def SetCommentCreate(self, SubjectType, SubjectId, **kwargs):
        if SubjectType not in self._SubjectType:
            raise AttributeError('Invalid parameter value')

        uri = '{0}create.api'.format(self.COMMENT)
        if isinstance(SubjectId, (str, unicode)):
            kwargs['SubjectId'] = SubjectId
        else:
            kwargs['SubjectId'] = str(SubjectId)
        kwargs['SubjectType'] = SubjectType
        return self._GetData(uri, kwargs)
    # /

    def GetDepartments(self):
        uri = '{0}list.api'.format(self.DEPARTMENT)
        return self._GetData(uri)
    # /

# / class Megaplan(object):


def main():
    pass

if __name__ == '__main__':
    main()