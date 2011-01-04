###############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id:$
"""

from zope.app.appsetup.product import _configs as productConfigs


def configureTMPStorage(local_conf):
    storage = local_conf.get('storage')
    if storage is None:
        raise ValueError(
            "Missing p01.tmp 'storage' configuration in paste *.ini file")
    productConfigs.update({'p01.tmp': {'storage':storage}})
