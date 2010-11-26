from datetime import datetime
import sys
import zc.recipe.egg

from praekelt.recipe import utils

class Backup:
    """
    File and database backup Buildout recipe.
    """
    def __init__(self, buildout, name, options):
        self.script_args = {}
        
        self.script_args['prefix'] = options['prefix']
        self.script_args['source_path'] = options.get('source_path', buildout['buildout']['directory'])
       
        # Collect database options.
        self.script_args['database_engine'] = options.get('database_engine', None)
        self.script_args['database_name'] = options.get('database_name', None)
        self.script_args['database_username'] = options.get('database_username', None)
        self.script_args['database_password'] = options.get('database_password', None)
        
        # Collect local options.
        self.script_args['local_count'] = int(options.get('local_count', 3))
        self.script_args['local_storage_path'] = options['local_storage_path']
        
        # Collect remote options.
        self.script_args['remote_host'] = options.get('remote_host', None)
        self.script_args['remote_storage_path'] = options.get('remote_storage_path', None)
        
        # General buildout setup.
        self.name = name
        self.buildout = buildout
        self.options = options
        self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)

    def create_manage_script(self, ws):
        args = []
        for k,v in self.script_args.items():
            if v.__class__ == str:
                args.append('%s="%s"' % (k, v))
            else:
                args.append('%s=%s' % (k, v))

        return zc.buildout.easy_install.scripts(
            [(self.name, 'praekelt.recipe.backup', 'script')],
            ws, 
            sys.executable, 
            self.options['bin-directory'],
            arguments=', '.join(args),
        )
   
    def install(self):
        requirements, ws = self.egg.working_set()
        self.create_manage_script(ws)
        script_paths = []
        # Create backup script.
        script_paths.extend(self.create_manage_script(ws))
        return script_paths

    def update(self):
        return

def script(prefix, local_storage_path, source_path, database_engine=None, database_name=None, database_username=None, database_password=None, local_count=None, remote_host=None, remote_storage_path=None):
    
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    timestamped_local_storage_path = '%s/%s_%s' % (local_storage_path, prefix, timestamp)
    timestamped_remote_storage_path = '%s/%s_%s' % (remote_storage_path, prefix, timestamp)

    # Create local rsync.
    utils.rsync(prefix=prefix, base_storage_path=local_storage_path, source_path=source_path, storage_path=timestamped_local_storage_path)

    # Dump database to local rsynced path.
    if database_engine and database_name and database_username and database_password:
        utils.dump_database(engine=database_engine, name=database_name, username=database_username, password=database_password, result_path=timestamped_local_storage_path)
    
    # Create remote rsync.
    if remote_host and remote_storage_path:
        utils.rsync(host=remote_host, prefix=prefix, base_storage_path=remote_storage_path, source_path='%s/' % timestamped_local_storage_path, storage_path=timestamped_remote_storage_path)
   
    # Cleanup local path to only have the latest local_count backups.
    if local_count:
        utils.cleanup_local(local_storage_path, local_count, prefix)
