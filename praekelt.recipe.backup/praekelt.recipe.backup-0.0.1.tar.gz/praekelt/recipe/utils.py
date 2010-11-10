import os
import re
import tarfile
import tempfile

def archive_paths(source_paths, result_path):
    """
    Create tarball from source paths to result path.
    """
    print "Archiving %s to %s." % (', '.join(source_paths), result_path)
    tar = tarfile.open(result_path, "w:gz")
    for source_path in source_paths:
        tar.add(source_path, os.path.split(source_path)[-1])
    tar.close()

def get_local_cleanup_paths(path, count, prefix):
    """
    Returns paths to be removed such that only the latest set of backups remain, limited by count.
    So if count is 5 any backup path older than the latest 5 will be included in the resulting list of paths.
    """
    matching_filenames = []
    for filename in os.listdir(path):
        if re.match('%s_[0-9]{14}.tar.gz' % prefix, filename):
            matching_filenames.append(os.path.join(path, filename))
  
    matching_filenames.sort()
    if count == 0:
        return matching_filenames
    else:
        return matching_filenames[:-count]

def scp(username, host, source_path, remote_path):
    """
    Uploads source_path to remote host via scp.
    TODO: Add password support, for now we only support key based logins setup on the OS level.
    """
    print "Uploading %s to %s@%s via scp:" % (source_path, username, host)
    os.system("scp %s %s@%s:%s" % (source_path, username, host, remote_path))

def dump_mysql(name, username, password):
    """
    Dump mysql database to tempfile and return path to tempfile.
    """
    result_path = tempfile.mkstemp(prefix="mysqldump")[1]
    print 'Dumping mysql database "%s" to %s.' % (name, result_path)
    os.system('mysqldump --user %s --password=%s %s > %s' % (username, password, name, result_path)) 
    return result_path

def dump_postgres(name, username, password):
    """
    Dump postgres database to tempfile and return path to tempfile.
    """
    result_path = tempfile.mkstemp(prefix="pg_dump")[1]
    print 'Dumping postgres database "%s" to %s.' % (name, result_path)
    os.system('export PGPASSWORD=%s;pg_dump --username=%s %s > %s;export PGPASSWORD=""' % (password, username, name, result_path))
    return result_path

def dump_database(engine, name, username, password):
    """
    Dumps database through engine appropriate dumper.
    Returns path to file containing database dump.
    """
    if engine == 'mysql':
        return dump_mysql(name, username, password)    
    if engine == 'postgres':
        return dump_postgres(name, username, password)    

def cleanup(cleanup_paths):
    """
    Removes/deletes provided paths.
    """
    for cleanup_path in cleanup_paths:
        print "Removing %s." % cleanup_path
        os.remove(cleanup_path)
