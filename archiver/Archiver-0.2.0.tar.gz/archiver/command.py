#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""\
Command line interface to the archiver

Used like this:

::

    python -m archiver.command --help

"""

import os
import logging
import sys
from commandtool import Cmd, LoggingCmd, handle_command
from configconvert.internal import eval_import
from archiver.api import make_batch, merge, sizeof_fmt, migrate, extract, numof_fmt

log = logging.getLogger(__name__)

#
# Commands
#

class Archiver(LoggingCmd):
    option_spec = LoggingCmd.option_spec.copy()
    option_spec.update(dict(
        store = dict(
            options = ['-s', '--store'],
            help = 'path to the store to create or use',
            metavar='STORE_PATH',
        ),
    ))
    help = {
        'summary': 'Archive sources of files and directories',
    }
    def run(self, cmd):
        LoggingCmd.run(self, cmd)
        if cmd.opts.get('store'):
            if not os.path.exists(cmd.opts.store):
                print "The source store directory %r is not present, creating it."%(cmd.opts.store,)
            cmd['batch'] = make_batch(cmd.opts.store)
        return 0
 
class Add(Cmd):
    arg_spec=[
        ('DIR', 'Directory to add to the store'),
        ('NAME', 'Identifier for this source eg "Files 1 2002"'),
    ]
    option_spec = dict(
        help = dict(
            options = ['-h', '--help'],
            help = 'display this message',
        ),
        skip_revert_times = dict(
            options = ['--skip-revert-times'],
            help = 'don\'t reset accessed and modified times for files on the source filesystem, useful if you are adding files from a read-only filesystem like a CD-ROM for example, only works if not using --hardlink',
        ),
        hardlink = dict(
            options = ['-l', '--hardlink'],
            help = (
                'use hardlinks to add the files to the store if possible. '
                'CAUTION: this only works if your source is on the same '
                'physical disc as the store and can be slightly faster for '
                'very large files but it means the files added to the store '
                'cannot be made read only as that would also modify the '
                'permission of the originals; with this option if someone '
                'changed the original file, the linked version in store '
                'would be silently changed too but the change would not '
                'be reflected in either the file\'s hash or the store '
                'metadata which could lead to unexpected problems later; '
                'only use this option if you know the source can\'t change, '
                'and even then, only if write performance to your store is '
                'an issue'
            ),
        ),
        extras_function = dict(
            options = ['--extras-function'],
            help = (
                'import path to a function that will decide how to add '
                'extras to files added to the store eg. '
                '`my.module:photo_extras\''
            ),
            metavar='EXTRAS_FUNCTION',
        ),
    )
    help = {
        'summary': 'add a source directory to the store',
    }

    def run(self, cmd):
        if not hasattr(cmd, 'batch'):
            print 'ERROR: No store specified'
            return 1
        source_path = cmd.args[0]
        source_name = cmd.args[1]
        # See if the source already exists
        if source_name in cmd.batch.metadata.source_list():
            print 'ERROR: Source %r already exists'%source_name
            return 1
        if cmd.opts.get('extras_function'):
            try:
                extras_function=eval_import(cmd.opts.extras_function)
            except ImportError:
                print 'ERROR: Could not import the extras function %r'%(cmd.opts.extras_function,)
                return 1
        else:
            extras_function=None 
        errors = cmd.batch.source_add(
            source_path, 
            source_name, 
            hardlink=cmd.opts.hardlink,
            extras_function=extras_function,
            skip_revert_times=cmd.opts.skip_revert_times,
        )
        if errors:
            print "The following files could not be added:"
            for error in errors:
                print error
            print "%s failure(s) in total"%len(errors)
        print "Done"

class Update(Add):
    option_spec = Add.option_spec.copy()
    option_spec.update(dict(
        skip_failures = dict(
            options = ['--skip-failures'],
            help = 'don\'t try to add any files which couldn\'t be added in previous attempts',
        ),
    ))
    help = {
	'summary': (
            'update an existing source by adding new files, useful if there '
            'was an error adding the source the first time; files present '
            'in the store but no longer present in the filesystem are NOT '
             'deleted from the store'
        )
    }

    def run(self, cmd):
        if not hasattr(cmd, 'batch'):
            print 'ERROR: No store specified'
            return 1
        source_path = cmd.args[0]
        source_name = cmd.args[1]
        if source_name not in cmd.batch.metadata.source_list():
            print 'ERROR: No such source %r, did you mean to use `add\'?'%source_name
            return 1
        if cmd.opts.has_key('extras_function'):
            try:
                extras_function=eval_import(cmd.opts.extras_function)
            except ImportError:
                print 'ERROR: Could not import the extras function %r'%(cmd.opts.extras_function,)
                return 1
        else:
            extras_function=None 
        errors = cmd.batch.source_add(
            source_path, 
            source_name,
            hardlink=cmd.opts.hardlink, 
            skip_failures=cmd.opts.skip_failures,
            extras_function=extras_function,
            skip_revert_times=cmd.opts.skip_revert_times,
            update=True,
        )
        if errors:
            print "There following %s files could not be added:"%len(errors)
            for error in errors:
                print "    ", error
        print "Done"

class ExtrasUpdate(Cmd):
    arg_spec=[
        (
            'EXTRAS_FUNCTION', 
            (
                'import path to a function that will decide how to add '
                'extras to files added to the store eg. '
                '`my.module:photo_extras\''
            )
        ),
        ('SOURCE', 'Source name'),
        ('DIR', 'Directory where the source files can be found (in case the extras function needs to inspect them)'),
    ]
    option_spec = dict(
        help = dict(
            options = ['-h', '--help'],
            help = 'display this message',
        ),
    )
    help = {
        'summary': 'reapply extras based on the stored file and directory metadata',
    }
    def run(self, cmd):
        if not hasattr(cmd, 'batch'):
            print 'ERROR: No store specified'
            return 1
        source_name = cmd.args[1]
        if source_name not in cmd.batch.metadata.source_list():
            print 'ERROR: No such source %r'%source_name
            return 1
        try:
            extras_function=eval_import(cmd.args[0])
        except ImportError:
            print 'ERROR: Could not import the extras function %r'%(cmd.opts.extras_function,)
            return 1
        cmd.batch.extras_update(
            source_name,
            extras_function=extras_function,
            path=cmd.args[1],
        )
        print "Done"

class ExtrasShow(Cmd):
    arg_spec=[
        ('SOURCE', 'Name of the source'),
        ('FILE_PATH', 'The path of file whose extras are to be listed'),
    ]
    option_spec = dict(
        help = dict(
            options = ['-h', '--help'],
            help = 'display this message',
        ),
    )
    help = {
        'summary': 'print a display of the extras for a file in particular source',
    }
    def run(self, cmd):
        if not hasattr(cmd, 'batch'):
            print 'ERROR: No store specified'
            return 1
        source_name = cmd.args[0]
        source__uid = cmd.batch.metadata.source_exists(source_name)
        if not source__uid:
            print 'ERROR: No such source %r'%source_name
            return 1
        file__uid =  cmd.batch.metadata._file__uid(
            cmd.args[1],
            source__uid,
        )
        extras = cmd.batch.metadata.extras(file__uid)
        for name in extras:
            print '%s: %s'%(name, extras[name])


class Sources(Cmd):
    option_spec = dict(
        help = dict(
            options = ['-h', '--help'],
            help = 'display this message',
        ),
        skip_stats = dict(
            options = ['--no-stats'],
            help = 'don\'t print size of the source, number of files or number of errors',
        ),
    )
    help = {
        'summary': 'list all the sources in the store',
    }
    def run(self, cmd):
        if not hasattr(cmd, 'batch'):
            print 'ERROR: No store specified'
            return 1
        sources = cmd.batch.metadata.source_list()
        for source in sources:
            if cmd.opts.skip_stats:
                print source
            else:
                source__uid = cmd.batch.metadata.source_exists(source)
                errors = cmd.batch.metadata.connection.execute("SELECT count(*) from file where source__uid=? and hash=''", source__uid).first()[0]
                files = cmd.batch.metadata.connection.execute("SELECT count(*) from file where source__uid=?", source__uid).first()[0]
                size = sizeof_fmt(cmd.batch.metadata.connection.execute('SELECT sum(size) from file where source__uid=?', source__uid).first()[0])
                print source+": %s %s file(s) %s error(s)"%(
                    size,
                    files,
                    errors,
                )

class Failures(Cmd):
    option_spec = dict(
        help = dict(
            options = ['-h', '--help'],
            help = 'display this message',
        ),
        skip_paths = dict(
            options = ['--skip-paths'],
            help = 'don\'t show individual failed paths',
        ),
        skip_counts = dict(
            options = ['--skip-counts'],
            help = 'don\'t calculate error counts for each source, implies --skip-paths too',
        ),
    )
    help = {
        'summary': 'list all files which couldn\'t be copied into the store',
    }
    def run(self, cmd):
        if not hasattr(cmd, 'batch'):
            print 'ERROR: No store specified'
            return 1
        sources = cmd.batch.metadata.source_list()
        sources_with_errors = [x for x in cmd.batch.metadata.connection.execute("SELECT distinct source__uid, source.name from file join source on file.source__uid = source.uid where hash=''")]
        print "%s/%s source(s) with errors..."%(len(sources_with_errors), len(sources))
        for source__uid, source in sources_with_errors:
            if cmd.opts.skip_counts:
                print "  ", source
            else: 
                errors = [x for x in cmd.batch.metadata.connection.execute("SELECT path from file where source__uid=? and hash=''", source__uid)]
                if errors:
                    print "  %s - %s errors(s)"%(source, len(errors))
                    if not cmd.opts.skip_paths:
                        for error in errors:
                            print "    ", error.path

class Stats(Cmd):
    help = {
        'summary': 'summary statistics',
    }
    option_spec = dict(
        help = dict(
            options = ['-h', '--help'],
            help = 'display this message',
        ),
    )
    def run(self, cmd):
        if not hasattr(cmd, 'batch'):
            print 'ERROR: No store specified'
            return 1
        print "%s sources(s)"%(
            cmd.batch.metadata.connection.execute('SELECT count(*) from source').first()[0],
        )
        num_files = cmd.batch.metadata.connection.execute('SELECT count(*) from file').first()[0]
        print "comprised of %s files(s)"%(
            numof_fmt(num_files),
        )
        print "and %s directories(s)"%(
            numof_fmt(cmd.batch.metadata.connection.execute('SELECT count(*) from directory').first()[0]),
        )
        print "originally %s"%(
            sizeof_fmt(cmd.batch.metadata.connection.execute('SELECT sum(size) from file').first()[0]),
        )
        num_objects = cmd.batch.metadata.connection.execute('select count(*) FROM (SELECT distinct hash from file)').first()[0]
        print "stored as %s unique binary object(s) with %s duplicate(s)"%(
            numof_fmt(num_objects),
            numof_fmt(num_files-num_objects),
        )
        data = cmd.batch.metadata.connection.execute('select sum(size) FROM (SELECT hash, size, count(uid) from file group by hash, size)').first()[0]
        metadata = os.stat(os.path.join(cmd.chain[-1].opts.store, 'paths.db')).st_size
        print "and now using %s for the data and %s for metadata."%(
            sizeof_fmt(data),
            sizeof_fmt(metadata),
        )
        
class Files(Cmd):
    help = {
        'summary': 'print a list of files in a source',
    }
    arg_spec=[
        ('SOURCE_NAME', 'the name of the source'),
    ]
    option_spec = dict(
        help = dict(
            options = ['-h', '--help'],
            help = 'display this message',
        ),
    )
    def run(self, cmd):
        if not hasattr(cmd, 'batch'):
            print 'ERROR: No store specified'
            return 1
        source = cmd.args[0]
        if not source in cmd.batch.metadata.source_list():
            print "ERROR: No such source %r"%source
            return 1
        file_records = cmd.batch.metadata.file_list(source)
        size = 0
        for file in file_records:
            size += file.size
            print u'%s %-9s %s'%(file.hash, sizeof_fmt(file.size), file.path)
        print "%s file(s) in total with a generated size of %s"%(len(file_records), sizeof_fmt(size))

class Migrate(Cmd):
    help = {
        'summary': 'migrate a store to use a new version of archiver',
    }
    arg_spec=[
        ('SRC', 'store path to migrate from'),
        ('DST', 'store path to migrate to'),
        ('FROM', 'version number of the store at the moment'),
        ('TO', 'version to migrate to'),
    ]
    option_spec = dict(
        help = dict(
            options = ['-h', '--help'],
            help = 'display this message',
        ),
    )
    def run(self, cmd):
        migrate('%s->%s'%(cmd.args[2], cmd.args[3]), cmd.args[0], cmd.args[1])
        print "Done."

class BinaryUnique(Cmd):
    help = {
        'summary': 'print information about the number of unique binary files in a store from a particular source (not unique file paths)',
    }
    arg_spec=[
        ('SOURCE_NAME', 'the name of the source'),
    ]
    option_spec = dict(
        help = dict(
            options = ['-h', '--help'],
            help = 'display this message',
        ),
    )
    def run(self, cmd):
        if not hasattr(cmd, 'batch'):
            print 'ERROR: No store specified'
            return 1
        source = cmd.args[0]
        if not source in cmd.batch.metadata.source_list():
            print "ERROR: No such source %r"%source
            return 1
        unique_files = cmd.batch.unique_files(source)
        size = 0
        for file in unique_files:
            print file.hash, ' ', file.path
            size += file.size
        print "%s unique binary file(s) added to the store from the %r source, adding %s"%(len(unique_files), source, sizeof_fmt(size))

class Diff(Cmd):
    help = {
        'summary': 'find files in a different metadata source that aren\'t present in this one',
    }
    arg_spec=[
        ('METADATA_PATH', 'the path to the folder containing the \'paths.db\' file to compare'),
    ]
    option_spec = dict(
        help = dict(
            options = ['-h', '--help'],
            help = 'display this message',
        ),
        no_size = dict(
            options = ['--no-size'],
            help = 'don\'t display the size in the output',
        ),
        show_paths = dict(
            options = ['--show-paths'],
            help = 'show full paths to the objects, not just the hash',
        ),
    )
    def run(self, cmd):
        if not hasattr(cmd, 'batch'):
            print 'ERROR: No store specified'
            return 1
        other = make_batch(cmd.args[0])
        res = [x[0] for x in cmd.batch.metadata.connection.execute('select distinct hash from file')]
        size = 0
        if x:
            unique = [(x[0], x[1]) for x in other.metadata.connection.execute('select distinct hash, size from file where hash not in (%s)'%(('? ,'*len(x))[:-2]), x)]
            for hash_, size_ in unique:
                if cmd.opts.show_paths:
                    path = os.path.join(cmd.args[0], hash_[:4]+'/'+hash_)
                else:
                    path = hash_
                if cmd.opts.no_size:
                    print path
                else:
                    print path, size_
                size += size_
        else:
            unique = []
        print "%s store object(s) are unique to %r"%(
            len(unique), 
            #cmd.chain[-1].opts.store, 
            cmd.args[0],
        )
        if not cmd.opts.no_size:
            print "Total size: %s"%(
                sizeof_fmt(size)
            )

class Remove(Cmd):
    help = {
        'summary': 'remove a source from the store, deleting its metadata and any files which aren\'t being used by other sources',
    }
    arg_spec=[
        ('SOURCE_NAME', 'the name of the source to delete'),
    ]
    option_spec = dict(
        help = dict(
            options = ['-h', '--help'],
            help = 'display this message',
        ),
        skip_files = dict(
            options = ['--skip-files'],
            help = 'don\'t remove the files from the store, just remove the source metadata',
        ),
    )
    def run(self, cmd):
        if not hasattr(cmd, 'batch'):
            print 'ERROR: No store specified'
            return 1
        source = cmd.args[0]
        if not source in cmd.batch.metadata.source_list():
            print "ERROR: No such source %r"%source
            return 1
        unique_files, size = cmd.batch.source_remove(source, cmd.opts.skip_files)
        print "Successfully removed metadata for %s"%(source,)
        if not cmd.opts.skip_files:
            if len(unique_files):
                print "Also removed %s binary object files from the store freeing %s"%(len(unique_files), sizeof_fmt(size))
            else:
                print "No binary object files needed to be removed from the store"

class Restore(Cmd):
    help = {
        'summary': 'restore a source directory structure from the store',
    }
    arg_spec=[
        ('DST', 'where to start the directory structure'),
    ]
    option_spec = dict(
        help = dict(
            options = ['-h', '--help'],
            help = 'display this message',
        ),
        hardlink = dict(
            options = ['--hardlink'],
            help = 'instead of copying the files and setting the original permissions, just hardlink to the copy in the store to create a readonly restore',
        ),
        source = dict(
            options = ['--source'],
            help = 'the name of the source to restore (can be specified multiple times, will restore all sources if no --source option is specified)',
            multiple=True,
            metavar='PATH',
        ),
    )
    def run(self, cmd):
        if not hasattr(cmd, 'batch'):
            print 'ERROR: No store specified'
            return 1
        if not cmd.opts.get('source'):
            sources = cmd.batch.metadata.source_list()
        else:
            sources = cmd.opts.source
        for source in sources:
            print "Restoring %r to %r"%(source, cmd.args[0])
            cmd.batch.browse(cmd.args[0], source, hardlink=cmd.opts.hardlink)
        print "Done."

class Merge(Cmd):
    arg_spec=[
        ('DST', 'path where the merged store should be created. eg `/arc/merge/store\''),
        (1, 'path to one of the stores to merge', 'At least one stores must be specified', 'STORE'),
    ]
    option_spec = dict(
        help = dict(
            options = ['-h', '--help'],
            help = 'display this message',
        ),
        skip_files = dict(
            options = ['--skip-files'],
            help = 'if you are sure you have already copied all files into the new store you can skip the check, then only the metadata merge will occur',
        ),
        allow_update = dict(
            options = ['--update'],
            help = 'merge into DST even if it already contains data, this will fail if any of the sources already have a source name present in the destination store',
        ),
    )
    help = {
        'summary': 'merge one or more stores into a new store',
    }
    def run(self, cmd):
        if not cmd.opts.allow_update and os.path.exists(os.path.join(cmd.args[0], 'paths.db')):
            print "ERROR: destination %r already contains a `paths.db' file, use `--update' to update anyway"%cmd.args[0]
            return 1
        if not os.path.exists(cmd.args[0]):
            os.mkdir(cmd.args[0])
        for store in cmd.args[1:]:
            if not os.path.exists(store):
                print "ERROR: store %r does not exist"%store
                return 1
            if not os.path.isdir(store):
                print "ERROR: store %r is not a directory"%store
                return 1
        merge(cmd.args[0], cmd.args[1:], cmd.opts.skip_files)
        print "Done."

class Extract(Cmd):
    arg_spec=[
        ('SRC', 'path to the current store'),
        ('DST', 'path to the where the extracted store should be created'),
        (1, 'names of one or more sources from the SRC store to extract', 'At least one source must be specified', 'SOURCE'),
    ]
    option_spec = dict(
        help = dict(
            options = ['-h', '--help'],
            help = 'display this message',
        ),
        skip_files = dict(
            options = ['--skip-files'],
            help = 'if you are sure you have already copied all files into the new store you can skip the check, then only the metadata merge will occur',
        ),
    )
    help = {
        'summary': 'copy one or more sources from an existing store into a new one',
    }
    def run(self, cmd):
        if os.path.exists(os.path.join(cmd.args[1], 'paths.db')):
            print "ERROR: destination %r already contains a `paths.db' file"%cmd.args[1]
            return 1
        if not os.path.exists(cmd.args[1]):
            os.mkdir(cmd.args[1])
        extract(cmd.args[0], cmd.args[1], cmd.args[2:], cmd.opts.skip_files)
        print "Done."

if __name__ == '__main__':
    from pipestack.app import pipe, command, App
    class Archiver(App):
        commands = [
            command(None           , Archiver    ),
            command('add'          , Add         ),
            command('update'       , Update      ),
            command('remove'       , Remove      ),
            command('merge'        , Merge       ),
            command('extract'      , Extract     ),
            command('restore'      , Restore     ),

            command('sources'      , Sources     ),
            command('stats'        , Stats       ),
            command('files'        , Files       ),
            command('extras'       , [
                (None, Cmd),
                ('update', ExtrasUpdate),
                ('show', ExtrasShow),
            ]),
            command('failures'     , Failures    ),

            command('binary-unique', BinaryUnique),
            command('diff'         , Diff        ),

            command('migrate'      , Migrate     ),
        ]
    Archiver().handle_command_line(program='python -m archiver.command')
    

