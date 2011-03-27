"""Store version info separately for use in __init__.py and setup.py"""
bzr_plugin_name = 'colo'
bzr_plugin_version = (0, 2, 1, 'final', 0)
bzr_minimum_version = (2, 1, 0)

if bzr_plugin_version[3] == 'final':
    __version__ = '%d.%d.%d' % bzr_plugin_version[:3]
else:
    __version__ = '%d.%d.%d%s%d' % bzr_plugin_version

bzr_commands = ['colo-init',
                'colo-branch',
                'colo-branches',
                'colo-fetch',
                'colo-pull',
                'colo-checkout',
                'colo-co',
                'colo-mv',
                'colo-move',
                'colo-rename',
                'colo-prune',
                'colo-delete',
                'colo-clean',
                'colo-ify',
                'colo-fixup',
                'qprune',
                'qdelete',
                'qbranches',
                'colo-sync-from',
                'colo-sync-to',
               ]
