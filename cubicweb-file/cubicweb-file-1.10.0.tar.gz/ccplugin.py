"""cubicweb-ctl plugin providing the fsimport command

:organization: Logilab
:copyright: 2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.cwctl import CWCTL

from cubicweb.toolsutils import Command


class FSImportCommand(Command):
    """Import content of a directory on the file system as File/Image entities.
    The instance must use the `file` cube.

    <instance id>
      identifier of the instance where directory's content has to be imported.

    <fs directory>
      directory to import (recursivly)
    """
    name = 'fsimport'
    min_args = max_args = 2
    arguments = '<instance id> <fs directory>'
    options = (
        ("map-folders",
         {'short': 'F', 'action' : 'store_true',
          'default': False,
          'help': 'map file-system directories as Folder entities (requires the `folder` cube).',
          }),
        )

    def run(self, args):
        """run the command with its specific arguments"""
        from cubicweb.server.serverconfig import ServerConfiguration
        from cubicweb.server.serverctl import repo_cnx
        from cubes.file.fsimport import import_directory
        appid = args.pop()
        directory = args.pop()
        config = ServerConfiguration.config_for(appid)
        repo, cnx = repo_cnx(config)
        repo.hm.call_hooks('server_maintenance', repo=repo)
        session = repo._get_session(cnx.sessionid, setpool=True)
        import_directory(session, directory,
                         mapfolders=self.config.map_folders,
                         bfss='data' in repo.system_source._storages.get('File', ()),
                         )
        session.commit()

CWCTL.register(FSImportCommand)
