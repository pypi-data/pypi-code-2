from commandtool import Cmd, handle_command
from sitetool.command import parse_html_config
import os
import logging
log = logging.getLogger('find')

#
# Here are our API functions
#

def name(letters, start_directory=None):
    if start_directory is None:
        start_directory = os.getcwd()
    found = []
    log.info(
        'Finding files in %r whose filenames contain the letters %r', 
        start_directory, 
        letters
    )
    for filename in os.listdir(start_directory):
        if not os.path.isdir(os.path.join(start_directory, filename)):
            log.debug('Trying %r', filename)
            if letters in filename:
                log.debug(
                    'Matched %r', 
                    os.path.join(start_directory, filename)
                )
                found.append(os.path.join(start_directory, filename))
    return found

def content(letters, start_directory=None, file_type='.txt'):
    if start_directory is None:
        start_directory = os.getcwd()
    found = []
    log.info(
        'Finding %r files in %r which contain the letters %r', 
        file_type, 
        start_directory, 
        letters
    )
    for filename in os.listdir(start_directory):
        if not os.path.isdir(os.path.join(start_directory, filename)) and filename.endswith(file_type):
            log.debug('Trying %r', filename)
            fp = open(os.path.join(start_directory, filename), 'r')
            data = fp.read()
            fp.close()
            if letters in data:
                log.debug(
                    'Matched %r', 
                    os.path.join(start_directory, filename)
                )
                found.append(os.path.join(start_directory, filename))
    return found

class Name(Cmd):
    arg_spec=[
        ('LETTERS', 'The letters to seach for'),
    ]
    option_spec = dict(
        help = dict(
            options = ['-h', '--help'],
            help = 'display this message'
        ),
        config = dict(
            options = ['-c', '--config'],
            help = 'the config file to use',
            metavar='CONFIG',
        ),
        start_directory = dict(
            options = ['-s'],
            help = 'the directory to search',
            metavar='START_DIRECTORY',
        ),
    )
    help = {
        'summary': 'search START_DIRECTORY for a filename matching LETTERS'
    }

    def on_run(self, service, args, opts):
        letters = args[0]
        config = None
        start_directory = None
        if opts.has_key('config'):
            config = parse_html_config(opts.config)
        if opts.has_key('start_directory'):
            start_directory = opts.start_directory
        elif config.has_key('START_DIRECTORY'):
            start_directory = config['START_DIRECTORY']
        for found in name(letters, start_directory):
            print found

class Content(Cmd):
    arg_spec=[
        ('LETTERS', 'The letters to seach for'),
    ]
    option_spec = dict(
        help = dict(
            options = ['-h', '--help'],
            help = 'display this message',
        ),
        file_type = dict(
            options = ['-t'],
            help = 'the file types to search',
            metavar='FILE_TYPE',
        ),
        config = dict(
            options = ['-c', '--config'],
            help = 'the config file to use',
            metavar='CONFIG',
        ),
        start_directory = dict(
            options = ['-s'],
            help = 'the directory to search',
            metavar='START_DIRECTORY',
        ),
    )
    help = {
        'summary': 'search START_DIRECTORY for a files containing LETTERS in their content',
    }

    def on_run(self, service, args, opts):
        letters = args[0]
        config = None
        start_directory = None
        file_type = '.txt'
        if opts.has_key('config'):
            config = parse_html_config(opts.config)
        if opts.has_key('start_directory'):
            start_directory = opts.start_directory
        elif config.has_key('START_DIRECTORY'):
            start_directory = config['START_DIRECTORY']
        if opts.has_key('file_type'):
            file_type = opts.file_type
        for found in content(letters, start_directory, file_type):
            print found

if __name__ == '__main__':
    handle_command(
        {
            'name': Name(),
            'content': Content(),
        }
    )

