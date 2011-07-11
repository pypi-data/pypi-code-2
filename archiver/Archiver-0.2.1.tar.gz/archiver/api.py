# -*- encoding: utf8 -*-
"""\
Archive files

Todo
----

Testing update:

* Get a broken CD
* Add it but stop half way through
* Update it ensuring it continues where it left off but stop after a read error
* Update it again with --skip-failures and ensure it ignores the read error, getting to the end

  :: 

      python -m archiver.command -v -s cd add --skip-revert-times /media/Applications_4/Palm/Palm\ Apps/ CD1
      python -m archiver.command -v -s cd failures
      python -m archiver.command -v -s cd update --skip-revert-times /media/Applications_4/Palm/Palm\ Apps/ CD1
      python -m archiver.command -v -s cd failures
      python -m archiver.command -v -s cd update --skip-revert-times --skip-failures /media/Applications_4/Palm/Palm\ Apps/ CD1
      python -m archiver.command -v -s cd failures

* Restore it 
* Touch one file and one directory to modify it
* Update again, but from the restored place, ensuring the metadata for the previous ones is correct

  :: 

      sudo env/bin/python -m archiver.command -v -s cd restore --source CD1 cd_restore
      python -m archiver.command -v -s cd update --skip-revert-times /media/Applications_4/Palm/Palm\ Apps/ cd_restore/CD1
      python -m archiver.command -v -s cd failures
      python -m archiver.command -v -s cd update --skip-revert-times --skip-failures /media/Applications_4/Palm/Palm\ Apps/ CD1
      python -m archiver.command -v -s cd failures

* Restore it 

Create:
* Integrity command
* Compact command
"""

from __future__ import unicode_literals

import datetime
import hashlib
import logging
import os
import shutil
import time
import uuid

from bn import relpath, uniform_path, AttributeDict
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey,\
    DateTime, Enum, select, and_, create_engine
from sqlalchemy.sql import func

from archiver.helper import sha1, set_time

log = logging.getLogger(__name__)


#
# Schema
#

def schema2():
    metadata = MetaData()
    return AttributeDict(
        metadata = metadata,
        file_records = Table('file', metadata,
            Column('uid', Integer, primary_key=True),
            Column('source__uid', None, ForeignKey('source.uid')),
            Column('hash', String),
            Column('path', String), # Never ends in a /
            Column('modified', DateTime),
            Column('accessed', DateTime),
            Column('owner', Integer),
            Column('group', Integer),
            Column('permission', Integer),
            Column('size', Integer),
            Column('link', String),
        ),
        directory_records = Table('directory', metadata,
            Column('uid', Integer, primary_key=True),
            Column('source__uid', None, ForeignKey('source.uid')),
            Column('path', String), # Always ends in a /
            Column('modified', DateTime),
            Column('accessed', DateTime),
            Column('owner', Integer),
            Column('group', Integer),
            Column('permission', Integer),
            Column('link', String),
        ),
        source_records = Table('source', metadata,
            Column('uid', Integer, primary_key=True),
            Column('name', String),
            Column('created', DateTime, default=datetime.datetime.now),
        ),
        # No-one was using tag or file_tag so skipping those tables
    )

metadata = MetaData()
file_records = Table('file', metadata,
    Column('uid', String, primary_key=True),
    Column('source__uid', None, ForeignKey('source.uid')),
    Column('hash', String),
    Column('path', String), # Never ends in a /
    Column('modified', DateTime),
    Column('accessed', DateTime),
    Column('owner', Integer),
    Column('group', Integer),
    Column('permission', Integer),
    Column('size', Integer),
    Column('link', String),
)
directory_records = Table('directory', metadata,
    Column('uid', String, primary_key=True),
    Column('source__uid', None, ForeignKey('source.uid')),
    Column('path', String), # Always ends in a /
    Column('modified', DateTime),
    Column('accessed', DateTime),
    Column('owner', Integer),
    Column('group', Integer),
    Column('permission', Integer),
    Column('link', String),
)
source_records = Table('source', metadata,
    Column('uid', String, primary_key=True),
    Column('name', String),
    Column('created', DateTime, default=datetime.datetime.now),
)
extra_records = Table('extra', metadata,
    # We can have duplicate uids for files
    Column('uid', String),
    Column('key', String),
    Column('value', String),
    Column('type', String),
)

#
# Helpers
#

try:
    chmod = os.lchmod
except AttributeError:
    chmod = os.chmod
    log.debug('No os.lchmod found, using os.chmod instead')

def make_uid():
    return str(uuid.uuid4())

def sizeof_fmt(num):
    if num < 1024:
        return '%s bytes'%num
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0

def numof_fmt(num):
    result = []
    num = str(num)
    while len(num)>3:
        result.append(num[-3:])
        num = num[:-3]
    if num:
        result.append(num)
    result.reverse()
    return ','.join(result)

def to_date(string):
    try:
        return datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        return datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")

def time_now():
    return str(datetime.datetime.now())[11:19]

def make_batch(store_path, md=metadata):
    if not os.path.exists(store_path):
        os.mkdir(store_path)
    created=False
    sqlite_path = os.path.join(store_path, 'paths.db')
    if not os.path.exists(sqlite_path):
        created=True
    engine = create_engine('sqlite:///%s'%sqlite_path, echo=False)
    md.create_all(engine)
    connection = engine.connect()
    if created:
        log.info('Creating the directory index...')
        connection.execute(''' create index directory_index on directory('source__uid', 'path')''')
        log.info('Creating the file index...')
        connection.execute(''' create index file_index on file('source__uid', 'path')''')
    batch = Batch(
        source = FileSystemSource(),
        store = FileSystemStore(store_path),
        metadata = SQLite3Metadata(connection),
    )
    return batch

def apply_metadata(path, permission, owner, group, accessed, modified):
    os.lchown(path, owner, group)
    if not os.path.islink(path):
        # On linux we can't set the permissions or time of symbolic link
        # directories, just their owner
        chmod(path, permission)
        set_time(path, accessed, modified)

# We use 16*1024 as the size because that's what shutil.copyfileobj() uses,
# so it should be a sensible default.
def copy_without_accessing(src, dst, size=16*1024, with_hash=False, skip_revert_times=False):
    log.debug('Copying without accessing %r', src)
    if with_hash:
        h = hashlib.new('sha1')
    stat_src = os.stat(src)
    if os.path.exists(dst):
        os.remove(dst)
    f = open(src, "rb")
    d = open(dst, "wb")
    try:
        chunk = f.read(size)
        while chunk: # EOF condition
            if with_hash:
                h.update(chunk)
            d.write(chunk)
            chunk = f.read(size)
    except Exception, e:
        log.error('Could not copy %r. Error was %r', src, e)
        raise
    else:
        # Put the source time back to how it was. @@@ is this a good idea?
        if not skip_revert_times:
            try:
                set_time(
                    src, 
                    stat_src.st_atime, 
                    stat_src.st_mtime,
                )
            except Exception, e:
                log.error(
                    'Could not reset the modification time on %r. Error was %r', 
                    src, 
                    e,
                )
        if with_hash:
            return h.hexdigest()
    finally:
        f.close()
        d.close()

#
# Global functionality
#

def migrate(step, src, dst):
    if step=='1->2':
        # This migration is mainly about removing the source_file and
        # source_directory metadata tables. No-one has files in the 
        # old format now, could be removed.
        # We don't migrate tags
        src_engine = create_engine('sqlite:///%s'%src)
        dst_batch = make_batch(dst)
        files = []
        for row in src_engine.execute('''
            SELECT 
                source_file.uid,
                source_file.source__uid,
                file.hash,
                file.path,
                file.modified,
                file.accessed,
                file.owner,
                file."group",
                file.permission,
                file.size,
                file.link
            FROM source_file 
            JOIN file ON source_file.file__uid = file.uid
        '''):
            res = dict(row)
            res['accessed'] = to_date(res['accessed'])
            res['modified'] = to_date(res['modified'])
            files.append(res)
            print 'f',
        directories = []
        for row in src_engine.execute('''
            SELECT 
                source_directory.uid,
                source_directory.source__uid,
                directory.path,
                directory.modified,
                directory.accessed,
                directory.owner,
                directory."group",
                directory.permission,
                directory.link
            FROM source_directory
            JOIN directory ON source_directory.directory__uid = directory.uid
        '''):
            res = dict(row)
            res['accessed'] = to_date(res['accessed'])
            res['modified'] = to_date(res['modified'])
            directories.append(res)
            print 'd',
        sources = []
        for row in src_engine.execute('''
            SELECT uid, name, created 
            FROM source
        '''):
            res = dict(row)
            res['created'] = to_date(res['created'])
            sources.append(res)
            print 's',
        trans = dst_batch.metadata.connection.begin()
        try:
            log.info('Copying sources...')
            print 'sources'
            dst_batch.metadata.connection.execute(
                source_records.insert(), 
                sources,
            )
            print 'directories'
            dst_batch.metadata.connection.execute(
                directory_records.insert(),
                directories,
            )
            print 'files'
            dst_batch.metadata.connection.execute(
                file_records.insert(), 
                files,
            )
            trans.commit()
        except:
            trans.rollback()
            raise
            print "Failed"
        else:
            print "Success"
    elif step=='2->3':
        # This migration is mainly about replacing tags with extras and using
        # guids instead of ids for the uid. It roughly doubles the size of
        # the database and halves the speed
        old_schema = schema2()
        src_batch = make_batch(src, md=old_schema.metadata)
        dst_batch = make_batch(dst)
        files = src_batch.metadata.connection.execute(
            select([old_schema.file_records])
        )
        directories = src_batch.metadata.connection.execute(
            select([old_schema.directory_records])
        )
        sources = src_batch.metadata.connection.execute(
            select([old_schema.source_records])
        )
        trans = dst_batch.metadata.connection.begin()
        try:
            log.info('Updating sources...')
            # Set the new source uids
            source_mapper = dict()
            for source in sources:
                print 's',
                source_mapper[source.uid] = source.name
                data = dict(source)
                data['source'] = data['name']
                del data['name']
                del data['uid']
                dst_batch.metadata.source_add(**data)
            for directory in directories:
                print 'd',
                data = dict(directory)
                del data['uid']
                data['source'] = source_mapper[data['source__uid']]
                del data['source__uid']
                dst_batch.metadata.directory_add(**data)
            for file in files:
                print 'f',
                data = dict(file)
                del data['uid']
                data['source'] = source_mapper[data['source__uid']]
                del data['source__uid']
                data['hash_str'] = data['hash']
                del data['hash']
                dst_batch.metadata.file_add(**data)
            trans.commit()
        except:
            trans.rollback()
            print "Failed"
            raise
        else:
            print "Success"
    elif step=='3->4':
        dst_batch = make_batch(src)
        trans = dst_batch.metadata.connection.begin()
        try:
            log.info('Creating the directory index...')
            trans.connection.execute(''' create index directory_index on directory('source__uid', 'path')''')
            log.info('Creating the file index...')
            trans.connection.execute(''' create index file_index on file('source__uid', 'path')''')
            log.info('Committing...')
            trans.commit()
        except:
            trans.rollback()
            print "Failed"
            raise
        else:
            print "Success"
    elif step=='4->5':
        # This removes duplicate files and directories in the source with ID 15afc8dd-d332-4be9-94a0-4e2b4eeef97c
        dst_batch = make_batch(src)
        trans = dst_batch.metadata.connection.begin()
        try:
            log.info('Finding all duplicate directories...')
            to_delete = []
            for dup_row in trans.connection.execute("""
                select distinct path from directory
                where source__uid='15afc8dd-d332-4be9-94a0-4e2b4eeef97c' 
                group by path having count(uid) > 1
            """):
                uids = []
                for row in trans.connection.execute("""
                    select distinct uid from directory
                    where source__uid='15afc8dd-d332-4be9-94a0-4e2b4eeef97c' 
                    and path=?
                """, (dup_row[0],)):
                    uids.append(row[0])
                for item in uids[1:]:
                    to_delete.append(item)
            num = 100
            log.info('%s directory record(s) to delete', len(to_delete))
            if to_delete and raw_input('Really delete [y/N] ').lower() =='y':
                while len(to_delete):
                    chunk = to_delete[:num]
                    to_delete = to_delete[num:]
                    print ".",
                    trans.connection.execute(
                        """
                        delete from directory
                        where uid in (%s)
                        """%(('?,'*len(chunk))[:-1],),
                        tuple(chunk),
                    )
            log.info('Finding all duplicate files...')
            to_delete = []
            all_ = []
            for dup_row in trans.connection.execute("""
                select distinct path from file
                where source__uid='15afc8dd-d332-4be9-94a0-4e2b4eeef97c' 
                group by path having count(uid) > 1
            """):
                res = trans.connection.execute("""
                    select * from file
                    where source__uid='15afc8dd-d332-4be9-94a0-4e2b4eeef97c' 
                    and path=?
                """, (dup_row[0],))
                all_.append([x for x in res])
                uids = []
                for row in trans.connection.execute("""
                    select distinct uid from file
                    where source__uid='15afc8dd-d332-4be9-94a0-4e2b4eeef97c' 
                    and path=?
                """, (dup_row[0],)):
                    uids.append(row[0])
                for item in uids[:-1]:
                    to_delete.append(item)
            log.info('%s file record(s) to delete', len(to_delete))
            print '\n'.join([str(x) for x in all_[:10]])
            if to_delete and raw_input('Really delete [y/N] ').lower() =='y':
                while len(to_delete):
                    chunk = to_delete[:num]
                    to_delete = to_delete[num:]
                    print ".",
                    trans.connection.execute(
                        """
                        delete from file
                        where uid in (%s)
                        """%(('?,'*len(chunk))[:-1],),
                        tuple(chunk),
                    )
            log.info('Committing...')
            trans.commit()
        except:
            trans.rollback()
            print "Failed"
            raise
        else:
            print "Success"
    else:
        raise Exception('Unknown step %s'%step)

def compare(src, dst, binary=False):
    if binary:
        os.system('diff -qru "%s" "%s"'%(src, dst))
    else:
        os.system('rsync -aHxv --numeric-ids --delete --dry-run -i "%s/" "%s/"'%(src, dst))

def extract(src, dst, sources, skip_files=False):
    dst_batch = make_batch(dst)
    copy_store_metadata(src, dst, sources)
    if not skip_files:
        hashes = [row[0] for row in dst_batch.metadata.connection.execute(
            select(
                [file_records.c.hash],
                source_records.c.name.in_(sources),
                from_obj=[
                    file_records.join(source_records),
                ],
            ).distinct()
        )]
        copy_store_data(src, dst, hashes)

def merge(dst, stores, skip_files=False):
    file_counts = []
    if uniform_path(dst) in [uniform_path(store) for store in stores]:
        raise Exception('You can\'t merge %r into itself'%dst)
    log.info(
        "Querying stores to discover the number of files they represent...",
    )
    sqlite_path = os.path.join(dst, 'paths.db')
    log.info('  Connecting to %s', 'sqlite:///%s'%sqlite_path)
    engine = create_engine('sqlite:///%s'%sqlite_path, echo=False)
    connection = engine.connect()
    metadata.create_all(engine)
    dst_sources = []
    for source in connection.execute('SELECT name from source'):
        dst_sources.append(source[0])
    sources = []
    for store in stores:
        sqlite_path = os.path.join(store, 'paths.db')
        log.info('  Connecting to %s', 'sqlite:///%s'%sqlite_path)
        engine = create_engine('sqlite:///%s'%sqlite_path, echo=False)
        connection = engine.connect()
        result = connection.execute('SELECT count(*) from file')
        num_source_files = result.first()[0]
        log.info('    %s source files', num_source_files)
        if not store == dst:
            file_counts.append((num_source_files, store))
        result = connection.execute('SELECT name from source')
        for source_list in result:
            if source_list[0] in dst_sources:
                raise Exception(
                    'The merge target store already contains a store named '
                    '%r so you cannot merge %r into it' % (
                        source_list[0],
                        store,
                    )
                )
            if source_list[0] in sources:
                raise Exception(
                    'Cannot merge because the source named %r exists in '
                    'two stores, please rename it or remove it from '
                    'one of them' % (
                        source_list[0],
                    )
                )
            else:
                sources.append(source_list[0])
    file_counts.sort()
    if not dst_sources:
        # We can copy an existing database as a starting point
        path_to_use = os.path.join(file_counts[-1][1], 'paths.db')
        log.info(
            "Chosen %r as the base for the metadata merge later", 
            path_to_use,
        )
    if not skip_files:
        log.info('Hardlinking files (store with the fewest files first)...')
        counter = 0
        for file_num, store in file_counts:
            counter += 1
            log.info(
                "  Copying store data for %s source files from "
                " %r -> %r [%s/%s]", 
                file_num, 
                store, 
                dst,
                counter,
                len(file_counts),
            )
            copy_store_data(store, dst)
    else:
        log.info("File check skipped due to `--skip-files' option. [SKIP]")
    log.info("Starting metadata merge...")
    if not dst_sources:
        log.info(
            "  Copying store database (%s files) from %r -> %r [1/%s]",
            file_counts[-1][0], 
            file_counts[-1][1],
            dst,
            len(file_counts),
        )
        shutil.copy(
            path_to_use,
            os.path.join(dst, 'paths.db'),
        )
        left_to_merge = file_counts[:-1]
        counter = 1
    else:
        left_to_merge = file_counts
        counter = 0
    for file_num, store in left_to_merge:
        counter += 1
        log.info(
            "  Copying store metadata (%s files) from %r -> %r [%s/%s]", 
            file_num,
            store, 
            dst,
            counter,
            len(file_counts),
        )
        store_batch = make_batch(store)
        copy_store_metadata(store, dst, store_batch.metadata.source_list())

def copy_store_metadata(store, dst, sources):
    file_count = 0
    next_file_print = 8
    store_batch = make_batch(store)
    dst_batch = make_batch(dst)
    for source in sources:
        data = store_batch.metadata.source(source)
        trans = dst_batch.metadata.connection.begin()
        try:
            source__uid = dst_batch.metadata.source_add(source, data.created)
            for directory_record in store_batch.metadata.directory_list(source):
                log.debug("    Adding directory %s", directory_record.path)
                directory_data = dict(directory_record)
                del directory_data['uid']
                del directory_data['source__uid']
                dst_batch.metadata.directory_add(
                    source=source,
                    **directory_data
                )
            for file_record in store_batch.metadata.file_list(source):
                file_count += 1
                if file_count == next_file_print:
                    log.info('    Added metadata for %s files so far [%s]', file_count, time_now())
                    if next_file_print < 2000:
                        next_file_print = int(next_file_print * 1.3)
                    else:
                        next_file_print = file_count + 2000
                extras=store_batch.metadata.extras(file_record.uid)
                log.debug("    Adding file %s with extras %r", file_record.path, extras)
                file_data = dict(file_record)
                del file_data['uid']
                del file_data['source__uid']
                hash_str=file_data['hash']
                del file_data['hash']
                dst_batch.metadata.file_add(
                    source=source,
                    extras=extras,
                    hash_str=hash_str,
                    **file_data
                )
            trans.commit()
        except:
            trans.rollback()
            raise

def copy_store_data(src, dst, hashes=None):
    if not hashes:
        hashes = []
        log.info('Getting a list of all the hashes in the store...')
        for root, dirs, files in os.walk(unicode(src)):
            for filename in files:
                if filename != 'paths.db':
                    hashes.append(filename)
        log.info('Done.')
    real_file_count = 0
    linked_file_count = 0
    next_file_print = 8
    log.info('Hardlinking store files...')
    for hash in hashes:
        real_file_count += 1
        if real_file_count == next_file_print:
            log.info('    Checked %s files, %s linked so far [%s]', real_file_count, linked_file_count, time_now())
            if next_file_print < 2000:
                next_file_print = int(next_file_print * 1.3)
            else:
                next_file_print = file_count + 2000
        dst_dir = os.path.join(dst, hash[:4])
        if not os.path.exists(dst_dir):
            os.mkdir(dst_dir)
        src_file = os.path.join(src, hash[:4], hash)
        dst_file = os.path.join(dst_dir, hash)
        if not os.path.exists(dst_file):
            log.debug("    File: %s -> %s", src_file, dst_file)
            linked_file_count += 1
            os.link(src_file, dst_file) 

#
# Be able to archive files in a filesytem
#

class FileSystemSource(object):

    def metadata(self, file_path):
        stat = os.lstat(file_path) # This stats a symlink, not the file it points to
        # We have st_mode, st_ino, st_dev, st_nlink, st_uid, st_gid, st_size, st_atime, st_mtime, st_ctime
        if os.path.islink(file_path):
            link = os.readlink(file_path)
        else:
            link = None
        return dict(
            modified   = datetime.datetime.fromtimestamp(stat.st_mtime),
            accessed   = datetime.datetime.fromtimestamp(stat.st_atime),
            owner      = stat.st_uid,
            group      = stat.st_gid,
            permission = stat.st_mode,
            size       = stat.st_size,
            link       = link,
        )

#
# Store files by their hash in a filesystem
#

class FileSystemStore(object):
    def __init__(self, store_path):
        self.store_path = store_path
        if not os.path.exists(store_path):
            os.mkdir(store_path)

    def add(
        self, 
        source_path, 
        base_path,
        hardlink=False,
        hash_str=None,
        skip_revert_times=False,
    ):
        copy = True
        src = os.path.join(base_path, source_path)
        if hardlink:
            copy = False
            if os.path.islink(src):
                #src = os.readlink(src)
                #directory = '/'.join(os.path.split('/')[:-1])
                src = os.path.abspath(os.path.join(os.path.split(os.path.abspath(src))[0], os.readlink(src)))
                copy=True
                #raise Exception('Code handling hardlinking to symlinks has not been tested, remove this exception to test it')
            else:
                if not hash_str:
                    hash_str = sha1(os.path.join(base_path, source_path), skip_revert_times=skip_revert_times)
                store_dir = os.path.join(self.store_path, hash_str[0:4])
                if not os.path.exists(store_dir):
                    os.mkdir(store_dir)
                # Get the dst path to hardlink later in this function
                dst = os.path.join(store_dir, hash_str)
        if copy:
            hash_str = copy_without_accessing(
                src,
                os.path.join(self.store_path, 'copy_in_progress_%s'%(os.getpid(),)),
                with_hash = True,
                skip_revert_times=skip_revert_times,
            )
            store_dir = os.path.join(self.store_path, hash_str[0:4])
            if not os.path.exists(store_dir):
                os.mkdir(store_dir)
            dst = os.path.join(store_dir, hash_str)
        if os.path.exists(dst):
            log.info('File %r already exists in the store as %r', source_path, dst)
            if copy:
                # Remove the temporary file we created for the hash
                os.remove(os.path.join(self.store_path, 'copy_in_progress_%s'%(os.getpid(),)))
        else:
            log.debug('File %r will be added to the store as %r', source_path, dst)
            if hardlink:
                # There is a chance here that the dst path is a relative symlink. We don't want to link to that, instead we want to link to the file the symlink resolves to
                os.link(
                    src,
                    dst,
                )
                # @@@ Note we aren't changing the permissions here because
                # that would affect the source files
            else:
                # Move the temp file into the store
                os.rename(os.path.join(self.store_path, 'copy_in_progress_%s'%(os.getpid(),)), dst)
                # Make the destination read and execute only
                chmod(dst, 500)
        return hash_str

    def remove(self, h):
        store_dir = os.path.join(self.store_path, h[0:4])
        if not os.path.exists(os.path.join(store_dir, h)):
            log.warning('Could not remove %r because it doesn\'t exist', os.path.join(store_dir, h))
        else:
            os.remove(os.path.join(store_dir, h))
        if os.path.exists(store_dir) and os.path.isdir(store_dir) and not os.listdir(store_dir):
            os.rmdir(store_dir)

#   
# Store metadata in an SQLite3 database
#

class SQLite3Metadata(object):

    def __init__(self, connection):
        self.connection = connection

    def file_update(
        self,
        uid,
        path,
        hash_str,
        modified,
        accessed,
        owner,
        group,
        permission,
        size,
        source='default',
        extras=None,
        link=None,
    ):
        # First delete the current file
        self.connection.execute('DELETE from file WHERE uid = ?;', uid)
        # Then add the new ones
        return self.file_add(
            path=path,
            hash_str=hash_str,
            modified=modified,
            accessed=accessed,
            owner=owner,
            group=group,
            permission=permission,
            size=size,
            source=source,
            extras=extras,
            link=link,
        )

    def file_add(
        self,
        path,
        hash_str,
        modified,
        accessed,
        owner,
        group,
        permission,
        size,
        source='default',
        extras=None,
        link=None,
    ):
        source__uid = self.source_exists(source)
        if source__uid is None:
            source__uid = self.source_add(source)
        if not isinstance(path, unicode):
            raise Exception('Expected a unicode string for %r'%path)
        file__uid = self.connection.execute(
            file_records.insert().values(
                uid=make_uid(),
                source__uid=source__uid,
                path=path,
                hash=hash_str,
                modified=modified,
                accessed=accessed,
                owner=owner,
                group=group,
                permission=permission,
                size=size,
                link=link,
            )
        ).inserted_primary_key[0]
        if extras is not None:
            self.update_extras(file__uid, extras)
        return file__uid

    def update_extras(self, file__uid, extras):
        # First delete any current extras
        self.connection.execute('DELETE from extra WHERE uid = ?;', file__uid)
        # Then add the new ones
        if isinstance(extras, dict):
            extras = extras.items()
        for extra in extras:
            d = {'uid': file__uid, 'key': extra[0], 'value': extra[1], 'type': len(extra)>2 and extra[2] or None}
            self.connection.execute(
                extra_records.insert().values(d)
            )

    def extras(self, file__uid):
        result = {}
        for extra in self.connection.execute(
            select(
                [extra_records],
                and_(
                    extra_records.c.uid==file__uid,
                ),
            )
        ):
            value = extra.value
            if extra.type:
                if extra.type == 'int':
                    value=int(value)
                elif extra.type == 'datetime':
                    value = to_date(value)
            result[extra.key] = value
        return result

    def _file__uid(
        self,
        path,
        source__uid,
    ):
        result = self.connection.execute(
            select(
                [file_records],
                and_(
                    file_records.c.path==path,
                    file_records.c.source__uid==source__uid,
                ),
            )
        ).first()
        if result:
            return result['uid']

    def _file_path_exists(
        self,
        path,
        source__uid,
    ):
        return self.connection.execute(
            select(
                [file_records],
                and_(
                    file_records.c.path==path,
                    file_records.c.source__uid==source__uid,
                ),
            )
        ).first() and True or False

    def _directory_metadata_exists(
        self,
        path,
        #modified,
        #accessed,
        #owner,
        #group,
        #permission,
        source__uid,
        #link,
    ):
        s = select(
            [directory_records],
            and_(
                directory_records.c.source__uid==source__uid,
                directory_records.c.path==path,
                #directory_records.c.modified==modified,
                #directory_records.c.owner==owner,
                #directory_records.c.group==group,
                #directory_records.c.permission==permission,
                #directory_records.c.link==link,
            ),
        ).limit(1)
        res = [f for f in self.connection.execute(s)]
        if not res:
            return None
        return res
    
    def _file_metadata_exists(
        self,
        path,
        #modified,
        #accessed,
        #owner,
        #group,
        #permission,
        #size,
        source__uid,
        #link,
    ):
        s = select(
            [file_records],
            and_(
                file_records.c.source__uid==source__uid,
                file_records.c.path==path,
                #file_records.c.modified==modified,
                #file_records.c.owner==owner,
                #file_records.c.group==group,
                #file_records.c.permission==permission,
                #file_records.c.size==size,
                #file_records.c.link==link,
            ),
        ).limit(1)
        res = [f for f in self.connection.execute(s)]
        if not res:
            return None
        return res
    
    def file_list(self, source):
        """\
        Return a list of paths in this directory source
        """
        source__uid = self.source_exists(source)
        if not source__uid:
            raise Exception('No such source %r'%source)
        res = self.connection.execute(
            select(
                [file_records],
                file_records.c.source__uid==source__uid,
            ).order_by(file_records.c.path.desc())
        )
        return [x for x in res]

    def directory_update(
        self,
        uid,
        path,
        modified,
        accessed,
        owner,
        group,
        permission,
        source='default',
        link=None,
    ):
        # First delete the current file
        self.connection.execute('DELETE from directory WHERE uid = ?;', uid)
        # Then add the new ones
        return self.directory_add(
            path,
            modified,
            accessed,
            owner,
            group,
            permission,
            source,
            link,
        )

    def directory_add(
        self,
        path,
        modified,
        accessed,
        owner,
        group,
        permission,
        source='default',
        link=None,
    ):
        source__uid = self.source_exists(source)
        if source__uid is None:
            source__uid = self.source_add(source)
        if not isinstance(path, unicode):
            raise Exception('Expected a unicode string for %r'%path)
        directory__uid = self.connection.execute(
            directory_records.insert().values(
                uid=make_uid(),
                source__uid = source__uid,
                path=path,
                modified=modified,
                accessed=accessed,
                owner=owner,
                group=group,
                permission=permission,
                link=link,
            )
        ).inserted_primary_key[0]
        return directory__uid

    def directory_list(self, source, path=None):
        """\
        Return a list of paths in this directory source
        """
        source__uid = self.source_exists(source)
        if not source__uid:
            raise Exception('No such source %r'%source)
        
        res = self.connection.execute(
            select(
                [directory_records],
                directory_records.c.source__uid==source__uid,
            ).order_by(directory_records.c.path.asc())
        )
        return [x for x in res]

    def source_add(self, source, created=None):
        if self.source_exists(source):
            raise Exception('A source named %r already exists'%source)
        if '/' in source and self.source_exists(source.replace('/', '_')):
            raise Exception("When sources are restored, '/' characters are replaced with '_' characters. A source named %r already exists so you can't use this name"%source.replace('/', '_'))
        d = dict(
            uid=make_uid(),
            name=source,
            created=created or datetime.datetime.now(),
        )
        res = self.connection.execute(source_records.insert().values(d))
        assert d['uid'] == res.inserted_primary_key[0], [d['uid'], res.inserted_primary_key[0]]
        return res.inserted_primary_key[0]

    def source_exists(self, source):
        res = self.connection.execute(select([source_records], source_records.c.name==source)).first()
        if res:
            return res.uid
        return None

    def source_list(self):
        return [row[0] for row in self.connection.execute(select([source_records.c.name]))]

    def source(self, source):
        res = self.connection.execute(select([source_records], source_records.c.name==source)).first()
        if res:
            return res
        else:
            raise Exception('No such source %r'%source)

class Batch(object):
    def __init__(self, source, store, metadata):
        self.store = store
        self.source = source
        self.metadata = metadata

    def unique_files(self, source):
        source__uid = self.metadata.source_exists(source)
        if not source__uid:
            raise Exception('No such source %r'%source)
        return [x for x in self.metadata.connection.execute('''
            SELECT uid, hash, path, size from file where hash in (
                SELECT hash FROM file WHERE source__uid = ?
                EXCEPT 
                SELECT hash from file where source__uid != ?
            ) order by path desc;
            ''', 
            (source__uid, source__uid),
        )]

    def source_remove(self, source, skip_files=False):
        source__uid = self.metadata.source_exists(source)
        if not source__uid:
            raise Exception('No such source %r'%source)
        # Get a list of hashes in this source that aren't in any other source
        trans = self.metadata.connection.begin()
        size = 0
        try:
            # Remove the physical files
            if not skip_files:
                unique_files = self.unique_files(source)
                unique_hashes = []
                for unique_file in unique_files:
                    if not unique_file.hash in unique_hashes:
                        size+=unique_file.size
                        unique_hashes.append(unique_file.hash)
                counter = 0
                for unique_hash in unique_hashes:
                    counter += 1
                    log.info('Removing object %s [%s/%s]', unique_hash, counter, len(unique_hashes))
                    self.store.remove(unique_hash)
            # Now remove all the metadata
            # Extras
            self.metadata.connection.execute('DELETE from extra WHERE uid in (SELECT uid FROM file WHERE source__uid=?);', source__uid)
            # Files
            self.metadata.connection.execute(
                file_records.delete(
                    file_records.c.source__uid==source__uid
                )
            )
            # Directories
            self.metadata.connection.execute(
                directory_records.delete(
                    directory_records.c.source__uid==source__uid
                )
            )
            # The source
            self.metadata.connection.execute(
                source_records.delete().where(
                    source_records.c.uid==source__uid,
                )
            )
            trans.commit()
        except:
            trans.rollback()
            raise
        else:
            if not skip_files:
                return unique_files, size
            return None, None

    def source_add(
        self, 
        base_path, 
        source, 
        exclude=None, 
        base=None, 
        extras_function=None, 
        update=False, 
        hardlink=False, 
        skip_failures=False, 
        # Shouldn't we revert directory times too as part of this?
        skip_revert_times=False,
        ignore_new_symlink_times=False,
    ):
        """\
        ``base`` can be used to determine which part of the path shouldn't be stored for this command.
        """
        source__uid = self.metadata.source_exists(source)
        if source__uid is None:
            source__uid = self.metadata.source_add(source)
        errors = []

        num_files = 0
        num_dirs = 0
        num_binary_add = 0
        num_binary_error = 0
        num_file_metadata_add = 0
        num_file_metadata_replace = 0
        num_directory_metadata_add = 0
        num_directory_metadata_replace = 0

        metadata = self.source.metadata(base_path)
        del metadata['size']
        for root, dirs, files in os.walk(unicode(base_path)):
            dirs.sort()
            for directory in dirs:
                num_dirs += 1
                path = os.path.join(root, directory)
                log.debug('Inspecting directory %r to add to source %r', relpath(path, base_path), source)
                metadata = self.source.metadata(path)
                del metadata['size']
                add_directory_metadata = True
                replace_directory_metadata = False
                if update:
                    directory_records = self.metadata._directory_metadata_exists(
                        relpath(path, base_path),
                        source__uid=source__uid,
                        #**metadata
                    )
                    if directory_records:

                        # There are existing directories with this path
                        if len(directory_records) > 1:
                            raise Exception(
                                'Found two directory rows in the database with the same path for the same directory. %s'%(
                                    [(directory.uid, directory.path) for directory in directory_records]
                                )
                            )
                        directory_record = directory_records[0]
                        # If the metadata exists, we don't need to add the metadata again
                        add_directory_metadata=False
                        # Unless
                        metadata_format = [
                            source__uid,
                            relpath(path, base_path),
                            metadata['modified'],
                            metadata['owner'],
                            metadata['group'],
                            metadata['permission'],
                            metadata['link'],
                        ]
                        db_format = [directory_records[0][1]] + list(directory_records[0][2:3]) + [directory_records[0][3]] + list(directory_records[0][5:])
                        if metadata_format != db_format:
                            log.info(
                                'Updating the existing directory metadata for %r',
                                relpath(path, base_path)
                            )
                            replace_directory_metadata=True
                            add_directory_metadata=False
                if add_directory_metadata:
                    log.info('Adding directory %r to source %r', relpath(path, base_path), source)
                    self.metadata.directory_add(
                        relpath(path, base_path),
                        source=source,
                        **metadata
                    )
                    num_directory_metadata_add += 1
                elif replace_directory_metadata:
                    log.info('Replacing directory %r in source %r', relpath(path, base_path), source)
                    # @@@ This gets run a lot if you update from a restored source, because archiver does not set the directory modified time
                    self.metadata.directory_update(
                        uid=directory_records[0].uid,
                        path=relpath(path, base_path),
                        source=source,
                        **metadata
                    )
                    num_directory_metadata_replace += 1
                else:
                    log.debug('Directory %s is already present, skipping', relpath(path, base_path))
            files.sort()
            for filename in files:
                num_files += 1
                path = os.path.join(root, filename)
                log.debug('Inspecting file %r to add to %r', path, source)
                metadata = self.source.metadata(path)
                log.debug('Obtained metadata %r', metadata)
                add_file = True
                add_file_metadata = True
                replace_file_metadata = False
                hash_str = ''
                extras = None
                if update:
                    file_records = self.metadata._file_metadata_exists(
                        relpath(path, base_path),
                        source__uid=source__uid,
                        #**metadata
                    )
                    if file_records:
                        # There are existing files with this path
                        if len(file_records) > 1:
                            raise Exception(
                                'Found two file rows in the database with the same path for the same file. %s'%(
                                    [(file.uid, file.path) for file in file_records]
                                )
                            )
                        file_record = file_records[0]
                        # If the metadata exists, we don't need to add the file or metadata again
                        add_file=False
                        add_file_metadata=False
                        # Unless
                        # 1. There is no hash (and it isn't a link) and we aren't skipping failures, in which case we replace the metadata
                        if not file_record.hash and not skip_failures and not file_record.link:
                            # XXX What about link dsts with errors? They'd have a missing hash too (how about hash '' vs None)
                            add_file=True
                            replace_file_metadata=True
                            add_file_metadata=False
                            hash_str = file_record.hash
                        # 2. the metadata has changed 
                        metadata_format = [
                            source__uid, 
                            relpath(path, base_path), 
                            metadata['modified'], 
                            metadata['owner'], 
                            metadata['group'], 
                            metadata['permission'],
                            metadata['size'],
                            metadata['link'],
                        ]
                        db_format = [file_records[0][1]] + list(file_records[0][3:4]) + [file_records[0][4]] + list(file_records[0][6:])
                        # Don't compare the microseconds part of a modified time
                        db_format[2] = datetime.datetime(
                            db_format[2].year,
                            db_format[2].month,
                            db_format[2].day,
                            db_format[2].hour,
                            db_format[2].minute,
                            db_format[2].second,
                        )
                        metadata_format[2] = datetime.datetime(
                            metadata_format[2].year,
                            metadata_format[2].month,
                            metadata_format[2].day,
                            metadata_format[2].hour,
                            metadata_format[2].minute,
                            metadata_format[2].second,
                        )
                        if metadata_format != db_format:
                            if metadata['link'] and ignore_new_symlink_times and metadata_format[0:2]+metadata_format[3:] == db_format[0:2]+db_format[3:]:
                                log.warning('Ignoring the new metadata for the symlink %r', relpath(path, base_path))
                            else:
                                log.info(
                                    'Updating the existing metadata for %r', 
                                    relpath(path, base_path)
                                )
                                replace_file_metadata=True
                                add_file_metadata=False
                if (replace_file_metadata or add_file_metadata) and extras_function is not None:
                    extras = extras_function(
                        self,
                        path,
                        AttributeDict(
                            path=relpath(path, base_path),
                            hash_str=hash_str,
                            **metadata
                        )
                    )
                if add_file:
                    if os.path.islink(path) and not os.path.exists(path):
                        # This is a symbolic link to a path that doesn't exist
                        # rather than raise an error, we want to add the metadata,
                        # but not the data. We treat this as a file, whether it points
                        # to a directory or not because we can't tell
                        log.error('The symlink path %r doesn\'t exist', path) 
                    else:
                        try:
                            hash_str = self.store.add(
                                relpath(path, base_path), 
                                base_path, 
                                hardlink=hardlink, 
                                skip_revert_times=skip_revert_times,
                            )
                        except Exception, e:
                            errors.append(path)
                            log.error('Error adding file %s', e)
                            log.debug('Now %s errors, %s file(s) succesfully copied'%(len(errors), num_files))
                            num_binary_error += 1
                        else:
                            log.info('Successfully added %s', path)
                            num_binary_add += 1
                else:
                    log.debug('File binary for %s is already present, skipping', relpath(path, base_path))
                if replace_file_metadata:
                    log.warning('Updating exising metadata for %r', relpath(path, base_path))
                    self.metadata.file_update(
                        uid=file_records[0].uid,
                        path=relpath(path, base_path),
                        hash_str=hash_str,
                        source=source,
                        extras=extras,
                        **metadata
                    )
                    num_file_metadata_replace += 1
                if add_file_metadata:
                    self.metadata.file_add(
                        relpath(path, base_path),
                        hash_str=hash_str,
                        source=source,
                        extras=extras,
                        **metadata
                    )
                    num_file_metadata_add += 1
                if not replace_file_metadata and not add_file_metadata:
                    log.debug('File metadata for %s is already present, skipping', relpath(path, base_path))
        results = dict(
            stats = (
                num_files,
                num_binary_add,
                num_binary_error,
                num_file_metadata_add,
                num_file_metadata_replace,
                num_dirs,
                num_directory_metadata_add,
                num_directory_metadata_replace,
            ),
            errors = errors
        )
        return results

    def browse(self, browse_path, source, dst=None, hardlink=False, metadata=False):
        """\
        """
        directory_metadata = []
        file_metadata = []

        if dst is None:
            dst = source
        if not os.path.exists(browse_path):
            os.mkdir(browse_path)
        base = os.path.join(browse_path, dst.replace('/', '_'))
        source_time = None
        if not os.path.exists(base):
            os.mkdir(base)
        source_time = self.metadata.source(source).created
        file_records = self.metadata.file_list(source)
        directory_records = self.metadata.directory_list(source)
        for directory_record in directory_records:
            path = os.path.join(base, directory_record.path)
            if not os.path.lexists(path):
                # @@@ We don't support exapnding directories to the real directories and files the way we do below for files.
                if not os.path.lexists(path):
                    log.debug('Making %r', path)
                    if directory_record.link is not None:
                        os.symlink(directory_record.link, path)
                    else:
                        os.mkdir(path)
                # Now keep the metadata to apply later
                if not hardlink and metadata:
                    directory_metadata.append(
                        dict(
                            path=path, 
                            permission=directory_record.permission,
                            owner=directory_record.owner,
                            group=directory_record.group,
                            accessed=directory_record.accessed,
                            modified=directory_record.modified,
                        )
                    )
        for file_record in file_records:
            path = os.path.join(base, file_record.path)
            if not os.path.lexists(path):
                if not file_record.hash:
                    if file_record.link:
                        # It must be a broken symlink to a file or directory
                        os.symlink(file_record.link, path)
                        if metadata:
                            file_metadata.append(
                                dict(
                                    path=path, 
                                    permission=file_record.permission,
                                    owner=file_record.owner,
                                    group=file_record.group,
                                    accessed=file_record.accessed,
                                    modified=file_record.modified,
                                )
                            )
                        continue
                    else:
                        # It could be from a file which couldn't be read from the source material
                        log.warning('No data for source file %r, writing an empty file', file_record.path)
                        fp = open(path, 'w')
                        fp.write('')
                        fp.close()
                        continue
                src = os.path.join(self.store.store_path, file_record.hash[:4], file_record.hash)
                if file_record.link is not None and self.metadata._file_path_exists(
                    # It is a symlink to a file we can link to in the store
                    os.path.join('/'.join(
                        file_record.path.split('/')[:-1]), 
                        file_record.link
                    ),
                    self.metadata.source_exists(source)
                ):
                    os.symlink(file_record.link, path)
                    if metadata:
                        file_metadata.append(
                            dict(
                                path=path, 
                                permission=file_record.permission,
                                owner=file_record.owner,
                                group=file_record.group,
                                accessed=file_record.accessed,
                                modified=file_record.modified,
                            )
                        )
                else:
                    if hardlink:
                        log.debug('Linking %r to %r', src, path)
                        os.link(src, path)
                    else:
                        log.debug('Copying %r to %r', src, path)
                        copy_without_accessing(src, path)
                        # Now try to apply the metadata
                        if metadata:
                            file_metadata.append(
                                dict(
                                    path=path, 
                                    permission=file_record.permission,
                                    owner=file_record.owner,
                                    group=file_record.group,
                                    accessed=file_record.accessed,
                                    modified=file_record.modified,
                                )
                            )
        for f in file_metadata:
            try:
                log.debug('Applying metadata to %r', f['path'])
                apply_metadata(**f)
            except Exception, e:
                log.error('Could not apply metadata to file %r; %r', directory_record.path, e)
        depth_first = []
        for d in directory_metadata:
            parts = d['path'].split('/')
            depth_first.append([-len(parts), d['path'], d])
            depth_first.sort()
        for a, b, d in depth_first:
            try:
                log.debug('Applying metadata to %r', d['path'])
                apply_metadata(**d)
            except Exception, e:
                log.error('Could not apply metadata to directory %r; %r', directory_record.path, e)
        if source_time:
            set_time(base, source_time, source_time)

    def extras_update(
        self, 
        source, 
        extras_function, 
        path,
    ):
        source__uid = self.metadata.source_exists(source)
        if source__uid is None:
            source__uid = self.metadata.source_add(source)
        for file_record in self.metadata.file_list(source):
            log.debug('Updating extras for file %r', file_record.path)
            self.metadata.update_extras(
                file_record.uid, 
                extras_function(
                    self, 
                    os.path.join(path, file_record.path),
                    file_record,
                )
            )

