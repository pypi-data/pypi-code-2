import sys
import zc.recipe.egg

class Backup:
    """
    File and database backup Buildout recipe.
    """
    def __init__(self, buildout, name, options):
        self.script_args = {}
        
        self.script_args['archive_prefix'] = options['archive_prefix']
       
        # Collect database options.
        self.script_args['database_enabled'] = options.get('database_enabled', False)
        if self.script_args['database_enabled']:
            self.script_args['database_engine'] = options['database_engine']
            self.script_args['database_name'] = options['database_name']
            self.script_args['database_username'] = options['database_username']
            self.script_args['database_password'] = options['database_password']
        
        # Collect local storage options.
        self.script_args['local_count'] = int(options.get('local_count', 3))
        self.script_args['local_location'] = options['local_location']
        
        # Collect backup path options.
        self.script_args['path_enabled'] = options.get('path_enabled', False)
        if self.script_args['path_enabled']:
            self.script_args['path'] = options.get('path', buildout['buildout']['directory'])
        
        # Collect scp options.
        self.script_args['scp_enabled'] = options.get('scp_enabled', False)
        if self.script_args['scp_enabled']:
            self.script_args['scp_username'] = options['scp_username']
            self.script_args['scp_host'] = options['scp_host']
            self.script_args['scp_path'] = options['scp_path']
        
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

def script(archive_prefix, local_location, database_enabled, scp_enabled, path_enabled, database_engine=None, database_name=None, database_username=None, database_password=None, local_count=None, path=None, scp_username=None, scp_host=None, scp_path=None):
    from praekelt.recipe import utils
    from datetime import datetime
    result_path = '%s/%s_%s.tar.gz' % (local_location, archive_prefix, datetime.now().strftime('%Y%m%d%H%M%S'))
    
    archive_paths = []
    cleanup_paths = []

    # Dump database and add resulting file to paths to be archived.
    if database_enabled:
        dbdump_path = utils.dump_database(engine=database_engine, name=database_name, username=database_username, password=database_password)
        archive_paths.append(dbdump_path)
        cleanup_paths.append(dbdump_path)

    # If path backup is enabled add path to paths to be archived.
    if path_enabled:
        archive_paths.append(path)

    # Create archive.
    utils.archive_paths(archive_paths, result_path)

    # SCP arhive to remote host.
    if scp_enabled:
        utils.scp(username=scp_username, host=scp_host, source_path=result_path, remote_path=scp_path)
    
    # Add stale archives to cleanup paths.
    cleanup_paths.extend(utils.get_local_cleanup_paths(local_location, local_count, archive_prefix))

    # Remove cleanup paths.
    utils.cleanup(cleanup_paths)
