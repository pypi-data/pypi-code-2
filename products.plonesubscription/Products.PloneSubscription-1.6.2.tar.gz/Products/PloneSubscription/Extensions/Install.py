# -*- coding: utf-8 -*-
## PloneSubscription
## A Plone tool supporting different levels of subscription and notification
## Copyright (C)2006 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
$Id: Install.py 227919 2010-12-01 11:43:20Z glenfant $
"""
__author__  = ''
__docformat__ = 'restructuredtext'

# Python imports
from StringIO import StringIO

# Zope imports
from Products.ExternalMethod.ExternalMethod import manage_addExternalMethod


# CMF imports
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ManagePortal, View

# Archetypes
from Products.Archetypes.Extensions.utils import installTypes
from Products.Archetypes.public import listTypes

# Product import
from Products.PloneSubscription.SubscriptionTool import SubscriptionTool
from Products.PloneSubscription.SubscriptionPermissions import \
     ViewSubscriptionRole, ViewSubscriptionContent, ManageSubscriptionContent
from Products.PloneSubscription.config import PROJECTNAME, GLOBALS, \
    subscription_prefs_configlet, subscription_task_id, subscription_script_id, \
    zope_DEPS, plone_DEPS
from Products.PloneSubscription.workflows.subscription_content_workflow import create_subscription_content_workflow

from Products.PloneSubscription.installers.utils import InstallationRunner, InstallationContext
from Products.PloneSubscription.installers.RoleInstaller import RoleInstaller
from Products.PloneSubscription.installers.ActionsInstaller import ActionsInstaller
from Products.PloneSubscription.installers.StandardPropertiesInstaller import StandardPropertiesInstaller
from Products.PloneSubscription.installers.ToolInstaller import ToolInstaller
from Products.PloneSubscription.installers.SkinLayersInstaller import SkinLayersInstaller
from Products.PloneSubscription.installers.ConfigletsInstaller import ConfigletsInstaller
#from Products.PloneSubscription.installers.PortletInstaller import PortletInstaller
from Products.PloneSubscription.installers.WorkflowInstaller import WorkflowInstaller
from Products.PloneSubscription.installers.CatalogInstaller import CatalogInstaller

from Products.PloneSubscription.SubscriptionCatalog import SubscriptionCatalog
from Products.PloneSubscription.SubscriptionCatalog import manage_addSubscriptionCatalog


# Only here for uninstall
# TODO : uninstall from generic setup
def getRunners():

    installers = []

    # grouped subscription needs a role
    ri = RoleInstaller(ViewSubscriptionRole, model='Anonymous',
                       allowed=(ViewSubscriptionContent, View))
    installers.append(ri)

    # PloneSubscription actions - portal_actions
    pf_actions = (
        {
            'id': 'my_subscriptions',
            'name': 'action_my_subscriptions',
            'action':'string:${portal_url}/my_subscriptions',
            'condition': 'python:member and portal.portal_subscription.hasSubscription()',
            'permission': View,
            'category':'user',
            'visible': 1
            },
        {
            'id': 'addSubscription',
            'name': 'action_add_to_subscriptions',
            'action':'string:${object_url}/addSubscription',
            'condition': 'python:member and portal.portal_subscription.getShow_document_action() and portal.portal_subscription.getProvider() is not None and not (not portal.portal_subscription.getAuthorize_root_subscription() and (object.portal_type == portal.portal_type or folder.portal_type == portal.portal_type))',
            'permission': View,
            'category':'document_actions',
            'visible': 1
            },
        {
            'id': 'addGroupSubscription',
            'name': 'action_add_group_subscriptions',
            'action':'string:${object_url}/grouped_subscription_add_form',
            'condition': "python: member and portal.portal_subscription.getProvider() is not None",
            'permission': ManageSubscriptionContent,
            'category':'object',
            'visible': 1
            },
        {
            'id': 'mailing',
            'name': 'action_subscription_mailing',
            'action':'string:${object_url}/subscription_mailing',
            'condition': "python: member and portal.portal_subscription.getProvider() is not None",
            'permission': ManageSubscriptionContent,
            'category':'object',
            'visible': 1
            },
        {
            'id': 'addSubscriptionProvider',
            'name': 'action_add_subscription_provider',
            'action':'string:${object_url}/addSubscriptionProvider',
            'condition': "python: portal.portal_subscription.getShow_actions() and 'subscription_provider' not in object.objectIds()",
            'permission': ManagePortal,
            'category':'folder',
            'visible': 1
            },
        {
            'id': 'addTemplatesProvider',
            'name': 'action_add_templates_provider',
            'action':'string:${object_url}/addTemplatesProvider',
            'condition': "python: portal.portal_subscription.showActions() and 'subscription_templates' not in object.objectIds()",
            'permission': ManagePortal,
            'category':'folder',
            'visible': 1
            },
        )
        
    ai = ActionsInstaller(pf_actions, actions_provider='portal_actions')
    installers.append(ai)

    pf_navtree_props =(
        ('metaTypesNotToList',
         ('SubscriptionTool',
          'SubscriptionProvider',
          'TemplatesProvider',
          )
         ),
        )
    spi = StandardPropertiesInstaller('navtree_properties', pf_navtree_props)
    installers.append(spi)

    sti = ToolInstaller(SubscriptionTool)
    installers.append(sti)

    si = SkinLayersInstaller()
    installers.append(si)

    ci = ConfigletsInstaller(subscription_prefs_configlet)
    installers.append(ci)

    #pi = PortletInstaller(('here/portlet_keywords_subscription/macros/portlet',),
    #                       slot_prop_name='left_slots')
    #installers.append(pi)

    #pi = PortletInstaller(('here/portlet_subscription/macros/portlet',),
    #                      slot_prop_name='right_slots')
    #installers.append(pi)

    wfi = WorkflowInstaller(workflow_name='subscription_content_workflow',
                            portal_types=('FolderSubscription',
                                          'KeywordsSubscription',
                                          'ContentSubscription',
                                          'ExactSearchSubscription'),
                            old_workflow=None,
                            module_name='Install',
                            function_name='create_subscription_content_workflow',
                            defaultWorkflow=False)
    installers.append(wfi)

    return InstallationRunner(*tuple(installers))

# only here for uninstall
def manageMaintenanceTask(self, action='install'):
    """Add all needed stuff in portal_maintenance"""
    mtool = getToolByName(self, 'portal_maintenance', None)
    if not mtool:
        return
    if action in ('install', 'reinstall'):
        # Plone Catalog update script
        manage_addExternalMethod(mtool.scripts, subscription_script_id,
                                 'Mailing subscriptions',
                                 PROJECTNAME + '.MaintenanceToolbox',
                                 'runMailing')

        try:
            mtool.tasks.manage_addProduct['PloneMaintenance'].addMaintenanceTask(subscription_task_id)
        except:
            pass
        subscription_task = mtool.tasks.subscription_task
        subscription_task.setScheduled_minute('0')
        subscription_task.setScript_name(subscription_script_id)
    else:
        if subscription_task_id in mtool.tasks.objectIds():
            mtool.tasks.manage_delObjects(ids=[subscription_task_id,])
        if subscription_script_id in mtool.scripts.objectIds():
            mtool.scripts.manage_delObjects(ids=[subscription_script_id,])


def install(self, reinstall=False):
    out = StringIO()
    """
    We need it for installing providers
    since GS importSiteStructure doesn't allow multiple level content structure import
    And this must be done after all installations (not in setupHandlers) 
    """
    
    # Generic Setup Installation
    portalsetup=getToolByName(self, "portal_setup")
    portalsetup.runAllImportStepsFromProfile(
        "profile-Products.PloneSubscription:default",
        purge_old=False)
        
    # providers + tool installation
    portalsetup=getToolByName(self, "portal_setup")
    portalsetup.runAllImportStepsFromProfile(
        "profile-Products.PloneSubscription:providers",
        purge_old=False)    
    
    provider = getToolByName(self, 'portal_selenium', None)
    if provider:
        # Functional Tests
        action = {'id':PROJECTNAME.lower(),
                  'name':PROJECTNAME,
                  'action':'string:here/get_%s_ftests'%PROJECTNAME.lower(),
                  'condition': '',
                  'permission': 'View',
                  'category':'ftests',
                  'visible': 1}
        provider.addAction(**action)

    out.flush()
    return


# TODO : uninstall providers + subscription catalog
def uninstall(self):

    manageMaintenanceTask(self, 'uninstall')

    ai=getToolByName(self, 'portal_actionicons')
    try:
        ai.removeActionIcon('plone', 'addSubscription')
    except KeyError:
        pass #Missing definition!

    # Always start with the creation of the InstallationContext
    ic = InstallationContext(self, GLOBALS)

    # Runs the uninstallation and return the report
    report = getRunners().uninstall(ic, auto_reorder=True)

    return report

