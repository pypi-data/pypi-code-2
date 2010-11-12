def initialize(context):
    from AccessControl.Permissions import manage_users
    from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin
    from pas.plugins.userdeletedevent import plugin
    
    registerMultiPlugin(plugin.UserDeletedEventPlugin.meta_type)
    context.registerClass(plugin.UserDeletedEventPlugin,
            permission=manage_users,
            constructors=(plugin.manage_addUserDeletedEventPlugin,
                          plugin.addUserDeletedEventPlugin),
            visibility=None)
