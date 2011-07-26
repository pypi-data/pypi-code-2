#!/usr/bin/python2

''' Gitolite admin manager
'''

import time
import logging

import glconfig
import glkey
import glgroup
import glrule
import gllock
from etc import config

TRY_TIMES = 10
logging.basicConfig(filename=config.LOG_FILENAME,
                    level=logging.DEBUG,
                    format='%(levelname)s:[func:%(funcName)s]%(message)s')

class HTTPException(BaseException):
    ''' HTTP Exception '''
    pass
class HTTPBadRequest(HTTPException):
    ''' HTTP Exception '''
    pass
class HTTPNotFound(HTTPException):
    ''' HTTP Exception '''
    pass
class HTTPConflict(HTTPException):
    ''' HTTP Exception '''
    pass
class HTTPNotImplemented(HTTPException):
    ''' HTTP Exception '''
    pass
class HTTPInternalServerError(HTTPException):
    ''' HTTP Exception '''
    pass

def _transaction(op_type, description, obj, func, *args, **kwargs):
    ''' _transaction for lockable object '''
    finished = False
    for i in range(TRY_TIMES):
        if finished:
            break
        if obj.locker.lock(op_type, description):
            try:
                result = func(*args, **kwargs)
                finished = True
            finally:
                obj.locker.unlock(sync=finished, fallback=not finished)
        if i == TRY_TIMES:
            raise HTTPConflict
        time.sleep(0.1)
    if finished:
        return result

def catch_and_raise(catch_exc, raise_exc):
    ''' Catches some exception and raise the specific exception '''
    def check_exc(func):
        ''' Returns catched function '''
        def new_func(*args, **kwargs):
            ''' Catches exceptions when calling '''
            try:
                return func(*args, **kwargs)
            except catch_exc, exc:
                logging.debug(exc.message)
                raise raise_exc(exc.message)
        return new_func
    return check_exc

class User:
    ''' User API '''
    
    def __init__(self):
        ''' Avoid to call '''
        pass
    
    @staticmethod
    @catch_and_raise(RuntimeError, HTTPInternalServerError)
    def index():
        ''' List all users '''
        return glkey.GLKey.index()

    @staticmethod
    @catch_and_raise(TypeError, HTTPBadRequest)
    @catch_and_raise(ValueError, HTTPBadRequest)
    @catch_and_raise(RuntimeError, HTTPInternalServerError)
    def create(name, pubkey):
        ''' Create a new user and returns its ID '''
        key = glkey.GLKey(name, pubkey)
        if key.exists():
            logging.debug('User %s already exist.' % name)
            raise HTTPConflict('User %s already exist.' % name)
        return _transaction(gllock.OP_CREATE, 'Create User: %s' % name,
                            key, key.create)

    @staticmethod
    def new():
        ''' Form to create a new user '''
        raise HTTPNotImplemented

    @staticmethod
    @catch_and_raise(TypeError, HTTPBadRequest)
    @catch_and_raise(ValueError, HTTPBadRequest)
    @catch_and_raise(RuntimeError, HTTPInternalServerError)
    def update(user_id, newpubkey):
        ''' Update an existing user '''
        key = glkey.GLKey(user_id)
        if not key.exists():
            raise HTTPNotFound
        return _transaction(gllock.OP_UPDATE, 'Update User: %s' % user_id,
                            key, key.update, newpubkey)

    @staticmethod
    @catch_and_raise(TypeError, HTTPBadRequest)
    @catch_and_raise(ValueError, HTTPBadRequest)
    @catch_and_raise(RuntimeError, HTTPInternalServerError)
    def delete(user_id):
        ''' Delete an existing user '''
        key = glkey.GLKey(user_id)
        if not key.exists():
            raise HTTPNotFound
        return _transaction(gllock.OP_DELETE, 'Delete User: %s' % user_id,
                            key, key.delete)

    @staticmethod
    @catch_and_raise(TypeError, HTTPBadRequest)
    @catch_and_raise(ValueError, HTTPBadRequest)
    def show(user_id):
        ''' Show a specific user '''
        key = glkey.GLKey(user_id)
        if not key.exists():
            raise HTTPNotFound
        return key.to_dict()

    @staticmethod
    def edit():
        ''' Form to edit an existing user '''
        raise HTTPNotImplemented

class Group:
    ''' Group API '''
    
    def __init__(self):
        ''' Avoid to call '''
        pass
    
    @staticmethod
    @catch_and_raise(TypeError, HTTPBadRequest)
    @catch_and_raise(ValueError, HTTPBadRequest)
    def index(reponame):
        ''' List all groups '''
        conf = glconfig.GLConfig(reponame)
        if not conf.exists():
            raise HTTPNotFound('Repo %s not found.' % reponame)
        conf.load()
        group_list = [group.get_id()
                      for group in conf.group_list]
        return group_list

    @staticmethod
    @catch_and_raise(TypeError, HTTPBadRequest)
    @catch_and_raise(ValueError, HTTPBadRequest)
    def create(repo_id, name, member_list):
        ''' Create a new group '''
        if not name.startswith('@'):
            raise HTTPBadRequest('Repo name should starts with "@".')
        group_id = '@%s_%s' % (repo_id, name[1:])
        conf = glconfig.GLConfig(repo_id)
        def bind():
            ''' operations binded for create '''
            conf.load()
            if any(group.get_id() == name for group in conf.group_list):
                raise HTTPConflict('Group %s already exists.' % name)
            group = glgroup.GLGroup(group_id, member_list)
            conf.group_list.append(group)
            conf.save()
            return group.get_id()
        return _transaction(gllock.OP_CREATE, 'Create Group: %s' % group_id,
                            conf, bind)

    @staticmethod
    def new():
        ''' Form to create a new group '''
        pass

    @staticmethod
    @catch_and_raise(TypeError, HTTPBadRequest)
    @catch_and_raise(ValueError, HTTPBadRequest)
    def update(repo_id, name, new_member_list):
        ''' Update an existing group '''
        if not name.startswith('@'):
            raise HTTPBadRequest('Repo name should starts with "@".')
        group_id = '@%s_%s' % (repo_id, name[1:])
        conf = glconfig.GLConfig(repo_id)
        if not conf:
            raise HTTPNotFound('Repo %s not found.' % repo_id)
        def bind():
            ''' operations binded for update '''
            conf.load()
            if not any(group.get_id() == name for group in conf.group_list):
                raise HTTPNotFound('Group %s not found.' % name)
            group = conf.find_group(group_id)
            group.member_list = new_member_list
            conf.save()
            return True
        return _transaction(gllock.OP_UPDATE, 'Update Group: %s' % group_id,
                            conf, bind)

    @staticmethod
    @catch_and_raise(TypeError, HTTPBadRequest)
    @catch_and_raise(ValueError, HTTPBadRequest)
    def delete(repo_id, name):
        ''' Delete an existing group '''
        if not name.startswith('@'):
            raise HTTPBadRequest('Repo name should starts with "@".')
        group_id = '@%s_%s' % (repo_id, name[1:])
        conf = glconfig.GLConfig(repo_id)
        def bind():
            ''' operations binded for delete '''
            conf.load()
            group = conf.find_group(group_id)
            if not group:
                raise HTTPNotFound
            result = group.delete()
            conf.save()
            return result
        return _transaction(gllock.OP_DELETE, 'Delete Group: %s' % group_id,
                            conf, bind)

    @staticmethod
    @catch_and_raise(TypeError, HTTPBadRequest)
    @catch_and_raise(ValueError, HTTPBadRequest)
    def show(repo_id, name):
        ''' Show a specific group '''
        if not name.startswith('@'):
            raise HTTPBadRequest('Repo name should starts with "@".')
        group_id = '@%s_%s' % (repo_id, name[1:])
        conf = glconfig.GLConfig(repo_id)
        if not conf.exists():
            raise HTTPNotFound('Repo %s not found.' % repo_id)
        conf.load()
        group = conf.find_group(group_id)
        if not group:
            raise HTTPNotFound('Group %s not found.' % group_id)
        return group.member_list

    @staticmethod
    def edit():
        ''' Form to edit an existing group '''
        pass

class Repo:
    ''' Repo API '''
    
    def __init__(self):
        ''' Avoid to call '''
        pass
    
    @staticmethod
    @catch_and_raise(RuntimeError, HTTPInternalServerError)
    def index():
        ''' List all repos '''
        return glconfig.GLConfig.index()

    @staticmethod
    @catch_and_raise(TypeError, HTTPBadRequest)
    @catch_and_raise(ValueError, HTTPBadRequest)
    def create(name):
        ''' Create a new repo '''
        conf = glconfig.GLConfig(name)
        if _transaction(gllock.OP_CREATE, 'Create Repo: %s' % name,
                        conf, conf.create):
            return name

    @staticmethod
    def new():
        ''' Form to create a new repo '''
        pass

    @staticmethod
    def update():
        ''' Update an existing repo '''
        pass

    @staticmethod
    @catch_and_raise(TypeError, HTTPBadRequest)
    @catch_and_raise(ValueError, HTTPBadRequest)
    def delete(name):
        ''' Delete an existing repo '''
        conf = glconfig.GLConfig(name)
        return _transaction(gllock.OP_DELETE, 'Delete Repo: %s' % name,
                            conf, conf.delete)

    @staticmethod
    def show():
        ''' Show a specific repo '''
        pass

    @staticmethod
    def edit():
        ''' Form to edit an existing repo '''
        pass

class Rule:
    ''' Rule API '''
    
    def __init__(self):
        ''' Avoid to call '''
        pass
    
    @staticmethod
    @catch_and_raise(TypeError, HTTPBadRequest)
    @catch_and_raise(ValueError, HTTPBadRequest)
    def index(reponame):
        ''' List all rules '''
        conf = glconfig.GLConfig(reponame)
        conf.load()
        rule_list = [rule.get_id() for rule in conf.rule_list]
        return rule_list

    @staticmethod
    @catch_and_raise(TypeError, HTTPBadRequest)
    @catch_and_raise(ValueError, HTTPBadRequest)
    def create(reponame, permission, refex_list, member_list):
        ''' Create a new rule '''
        conf = glconfig.GLConfig(reponame)
        def bind():
            ''' operations binded for create '''
            conf.load()
            rule = glrule.GLRule(permission,
                                 refex_list,
                                 member_list)
            if conf.find_rule(refex_list, member_list):
                raise HTTPConflict('Rule already exists.')
            conf.rule_list.append(rule)
            conf.save()
            return rule.get_id()
        return _transaction(gllock.OP_CREATE, 'Create Rule: %s' % reponame,
                            conf, bind)

    @staticmethod
    def new():
        ''' Form to create a new rule '''
        pass

    @staticmethod
    @catch_and_raise(TypeError, HTTPBadRequest)
    @catch_and_raise(ValueError, HTTPBadRequest)
    def update(reponame, rule_id, new_member_list):
        ''' Update an existing rule '''
        refex_list, member_list = glrule.GLRule.parse_id(rule_id)
        conf = glconfig.GLConfig(reponame)
        def bind():
            ''' operations binded for update '''
            conf.load()
            rule = conf.find_rule(refex_list, member_list)
            if not rule:
                raise HTTPNotFound('Rule %s %s not found.' % (refex_list, member_list))
            rule.member_list = new_member_list
            conf.save()
            return True
        return _transaction(gllock.OP_UPDATE, 'Update Rule: %s' % rule_id,
                            conf, bind)

    @staticmethod
    @catch_and_raise(TypeError, HTTPBadRequest)
    @catch_and_raise(ValueError, HTTPBadRequest)
    def delete(reponame, rule_id):
        ''' Delete an existing rule '''
        refex_list, member_list = glrule.GLRule.parse_id(rule_id)
        conf = glconfig.GLConfig(reponame)
        def bind():
            ''' operations binded for delete '''
            conf.load()
            rule = conf.find_rule(refex_list, member_list)
            if not rule:
                raise HTTPNotFound('Rule %s %s not found.' % (refex_list, member_list))
            result = rule.delete()
            conf.save()
            return result
        return _transaction(gllock.OP_DELETE, 'Delete Rule: %s' % rule_id,
                            conf, bind)

    @staticmethod
    @catch_and_raise(TypeError, HTTPBadRequest)
    @catch_and_raise(ValueError, HTTPBadRequest)
    def show(reponame, rule_id):
        ''' Show a specific rule '''
        refex_list, member_list = glrule.GLRule.parse_id(rule_id)
        conf = glconfig.GLConfig(reponame)
        conf.load()
        rule = conf.find_rule(refex_list, member_list)
        if rule:
            return rule.to_dict()
        if (len(refex_list) == 1 and
            len(member_list) == 1):
            rule = conf.match_rule(refex_list[0], member_list[0])
            if rule:
                return rule.to_dict()
        raise HTTPNotFound
    
    @staticmethod
    def edit():
        ''' Form to edit an existing rule '''
        pass

