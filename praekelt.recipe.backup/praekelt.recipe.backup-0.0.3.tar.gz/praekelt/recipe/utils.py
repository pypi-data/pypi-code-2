import os
import re
import shutil
from fabric.api import settings, run, local

def cleanup_local(path, count, prefix):
    """
    Returns paths to be removed such that only the latest set of backups remain, limited by count.
    So if count is 5 any backup path older than the latest 5 will be included in the resulting list of paths.
    """
    matching_filenames = []
    for filename in os.listdir(path):
        if re.match('%s_[0-9]{14}' % prefix, filename):
            matching_filenames.append(os.path.join(path, filename))
  
    matching_filenames.sort()
    if count == 0:
        return None
    else:
        matching_filenames = matching_filenames[:-count]

    for cleanup_path in matching_filenames:
        print "Removing %s." % cleanup_path
        shutil.rmtree(cleanup_path)

def create_path(path, host=None):
    """
    Creates path recursively.
    """
    command = run if host else local

    with settings(host_string=host):
        command('mkdir -p %s' % path)
        
def resolve_symlink(path, host=None):
    """
    Resolves a symlink to the file it's pointing to.
    """
    command = run if host else local

    resolved_path = None
    with settings(host_string=host, warn_only=True):
        result = command('ls -l %s' % path)
        if not result.failed:
            resolved_path = result.split('-> ')[-1]
    return resolved_path

def create_symlink(source_path, link_path, host=None):
    """
    Creates a symlink to source_path from link_path.
    Removes an existing symlink beforehand.
    """
    command = run if host else local
    
    with settings(host_string=host, warn_only=True):
        command('rm %s' % link_path)
        command('ln -s %s %s' % (source_path, link_path))

def rsync(storage_path, base_storage_path, source_path, prefix, host=None):
    """
    rsync incrementally using --link-dest, see:
    http://www.sanitarium.net/golug/rsync_backups_2010.html
    Determines previous backup through prefix.current symlink which is created after rsync completes.
    """
    create_path(path=storage_path)
    last_storage_path = resolve_symlink(host=host, path="%s/*.current" % base_storage_path)
   
    original_storage_path = storage_path
    if host:
        storage_path = '%s:%s' % (host, storage_path)

    if last_storage_path:
        os.system('rsync --verbose --archive --human-readable --inplace --numeric-ids --delete --link-dest=%s  %s %s' % (last_storage_path, source_path, storage_path))
    else:
        os.system('rsync --verbose --archive --human-readable --inplace --numeric-ids --delete %s %s' % (source_path, storage_path))
   
    create_symlink(host=host, source_path=original_storage_path, link_path="%s/%s.current" % (base_storage_path, prefix))

def dump_mysql(name, username, password, result_path):
    """
    Dump mysql database to file named mysql.sql in result path.
    """
    result_path = os.path.join(result_path, 'mysql.sql')
    print 'Dumping mysql database "%s" to %s.' % (name, result_path)
    os.system('mysqldump --user %s --password=%s %s > %s' % (username, password, name, result_path)) 
    return result_path

def dump_postgres(name, username, password, result_path):
    """
    Dump postgres database to file named postgres.sql in result path.
    """
    result_path = os.path.join(result_path, 'postgres.sql')
    print 'Dumping postgres database "%s" to %s.' % (name, result_path)
    os.system('export PGPASSWORD=%s;pg_dump --username=%s %s > %s;export PGPASSWORD=""' % (password, username, name, result_path))
    return result_path

def dump_database(engine, name, username, password, result_path):
    """
    Dumps database through engine appropriate dumper.
    """
    if engine == 'mysql':
        return dump_mysql(name, username, password, result_path)    
    if engine == 'postgres':
        return dump_postgres(name, username, password, result_path)    
