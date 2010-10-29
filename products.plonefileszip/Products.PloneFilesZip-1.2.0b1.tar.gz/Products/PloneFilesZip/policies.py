# -*- coding: utf-8 -*-
# Copyright (c) 2003-2006 Ingeniweb SAS

# This software is subject to the provisions of the GNU General Public
# License, Version 2.0 (GPL).  A copy of the GPL should accompany this
# distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY,
# AGAINST INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE

# More details in the ``LICENSE`` file included in this package.

"""
    ZipStructurePolicy defines how the downloaded zip inner tree is built
"""

from os.path import join

from AccessControl import ClassSecurityInfo
from interfaces import IZipStructurePolicy

# #######################################
#         POLICIES MANAGEMENT           #
# #######################################

class PolicyRegistry:
    ''' provides an object
        that contains instances of all inner zip structure policies
    '''
    _policies = dict()

    def registerPolicy(self,policy):
        ''' puts a policy instance of policy in the registry
        the parameter policy is the id
        '''
        if IZipStructurePolicy not in policy.__implements__:
            raise TypeError, "you must register a ZipStructure policy. %s type can't be registered" % type(policy)
        if self._policies.get(policy.id):
            raise ValueError, "the policy %s has ever been registered" % policy.id
        self._policies[policy.id] = policy()

    def getPoliciesInfos(self):
        ''' returns a dictionary of policies ids and policies infos
        'id', 'label', 'label_msgid', 'help', 'help_msgid'
        of registered policies
        '''
        infos_mapping = dict()
        for policy in self._policies.keys():
            infos_mapping[policy] = dict()
            for info in ['id', 'label', 'label_msgid', 'help', 'help_msgid']:
                infos_mapping[policy][info] = getattr(self._policies[policy], info)
        return infos_mapping

    def getPoliciesZMIVocabulary(self):
        ''' returns a ZMI vocabulary of policies '''
        return tuple(self._policies.keys()) # TODO

    def getPolicy(self,policy_id):
        ''' returns the policy instance of id policy_id '''
        try:
            return self._policies[policy_id]
        except AttributeError:
            raise KeyError, "The %s zip structure policy does not exist" % policy_id

PolicyRegistry = PolicyRegistry()


# ###############################################
#                   POLICIES                    #
# ###############################################


class AbstractZipStructurePolicy:
    ''' Abstract class of an inner zip structure policy '''
    security = ClassSecurityInfo()

    security.declarePrivate("getZipFilePath")
    def getZipFilePath(self,**kwargs):
        raise NotImplementedError

    security.declarePrivate("getRdfZipPath")
    def getRdfZipPath(self,content_relative_path):
        raise NotImplementedError

class DeepZipStructurePolicy(AbstractZipStructurePolicy):
    '''
        The inner structure of the zip file
        corresponds to the inner structure of the objects.
    '''
    __implements__ = (IZipStructurePolicy,)
    id = 'deep_inner_zip_structure'
    label = "Deep zip inner structure policy"
    label_msgid = 'deep_inner_zip_structure'
    help = "The inner structure of the zip file corresponds to the inner structure of the objects. There can be no duplicated names. It is the most secure option"
    help_msgid = "deep_structure_policy_help"


    def getZipFilePath(self,
                     container_path=None,
                     file_name=None,
                     field_path=None,
                     **kwargs):
        ''' returns the path of the file in the zip file
            with its location in the zodb in regards to the context
        '''
        unset = [(param, value) for param, value in [("container_path", container_path), ("field_path", field_path), ("file_name", file_name)] if value is None]
        for param in unset:
            raise TypeError, str(unset) + "have to be setup"

        return join(container_path.lstrip("/"),
                    file_name,
                    field_path.lstrip("/"),)

    def getRdfZipPath(self,content_relative_path):
        return content_relative_path.lstrip("/") + ".rdf"

PolicyRegistry.registerPolicy(DeepZipStructurePolicy)



class SimpleZipStructurePolicy(AbstractZipStructurePolicy):
    '''
        The inner structure of the zip file corresponds to the site structure as visitors conceive it.
        Folder structure is reproduced and files are stored in a directory of their document's name.
    '''
    __implements__ = (IZipStructurePolicy,)
    id = 'simple_inner_zip_structure'
    label = "Simple zip inner structure policy"
    label_msgid = 'simple_inner_zip_structure'
    help = "The inner structure of the zip file corresponds to the site structure as visitors conceive it. Folder structure is reproduced and files are stored in a directory of their document's name. Duplicated field names are renamed"
    help_msgid = 'simple_structure_policy_help'

    def getZipFilePath(
                     self,
                     container_path=None,
                     file_name=None,
                     **kwargs):
        ''' returns the path of the file in the zip file
                built with the location of its document container in regards to the context
        '''
        unset = [(param, value) for param, value in [("container_path", container_path,),
                                                   ("file_name", file_name)] if value is None]
        for param, value in unset:
            raise TypeError, param + " have to be setup"

        return join(container_path.lstrip("/"),
                            file_name,
                            )
    def getRdfZipPath(self,content_relative_path):
        return DeepZipStructurePolicy.getRdfZipPath(self,content_relative_path)


PolicyRegistry.registerPolicy(SimpleZipStructurePolicy)

class ContentZipStructurePolicy(AbstractZipStructurePolicy):
    '''
    The inner structure of the zip file corresponds to the site structure as visitors conceive it.
    Folder structure is reproduced and files are stored in a directory of their document's name.
    '''

    __implements__ = (IZipStructurePolicy,)
    id = 'content_inner_zip_structure'
    label = "Content zip inner structure policy"
    label_msgid = 'content_inner_zip_structure'
    help = "The inner structure of the zip file corresponds to the site structure as visitors conceive it. Folder structure is reproduced and files are stored in a directory of their document's name. Duplicated field names are renamed. Id of content is also included."
    help_msgid = 'content_inner_zip_structure_policy_help'

    def getZipFilePath(
                     self,
                     container_path=None,
                     content_id=None,
                     file_name=None,
                     **kwargs):
        ''' returns the path of the file in the zip file
                built with the location of its document container in regards to the context
        '''
        unset = [(param, value) for param, value in [("container_path", container_path,),
                                                   ("file_name", file_name)] if value is None]
        for param, value in unset:
            raise TypeError, param + " have to be setup"

        return join(container_path.lstrip("/"), content_id, )

    def getRdfZipPath(self,content_relative_path):
        return DeepZipStructurePolicy.getRdfZipPath(self,content_relative_path)

PolicyRegistry.registerPolicy(ContentZipStructurePolicy)

class FsLikeZipStructurePolicy(AbstractZipStructurePolicy):
    '''
        The files are directly stored in their container folder.
    '''
    __implements__ = (IZipStructurePolicy,)
    id = 'fs_like_inner_zip_structure'
    label = "File system like zip inner structure policy"
    label_msgid = 'fs_like_inner_zip_structure'
    help = "The files are directly stored in their container folder. Duplicated names are renamed."
    help_msgid = "fs_like_structure_policy_help"

    def getZipFilePath(self, container_path=None, **kwargs):
        ''' returns the path of the file in the zip file
            with the location of its folder in regards to the context
        '''
        unset = [(param, value) for param, value in [("container_path", container_path)] if value is None]
        for param in unset:
            raise TypeError, str(unset) + "have to be setup"

        return container_path.lstrip("/")

    def getRdfZipPath(self,content_relative_path):
        return DeepZipStructurePolicy.getRdfZipPath(self,content_relative_path)

PolicyRegistry.registerPolicy(FsLikeZipStructurePolicy)


class FlatZipStructurePolicy(AbstractZipStructurePolicy):
    '''
        All files are saved at zip root
    '''
    __implements__ = (IZipStructurePolicy,)
    id = 'flat_inner_zip_structure'
    label = "Flat zip inner structure policy"
    label_msgid = 'flat_inner_zip_structure'
    help = "All files are saved at zip root"
    help_msgid = "flat_structure_policy_help"

    def getZipFilePath(self,**kwargs):
        return ""

    def getRdfZipPath(self,content_relative_path):
        return DeepZipStructurePolicy.getRdfZipPath(self,content_relative_path)

PolicyRegistry.registerPolicy(FlatZipStructurePolicy)
