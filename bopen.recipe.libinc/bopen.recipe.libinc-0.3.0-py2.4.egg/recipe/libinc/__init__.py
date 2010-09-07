
import os
import logging      

import zc.buildout

class LibInc(object):
    """zc.buildout recipe for parsing unix-config commands"""

    def __init__(self, buildout, name, options):
        libraries = []
        library_dirs = []
        include_dirs = []

        log = logging.getLogger(name)

        for command in options.get('flags-command', '').splitlines():
            if command.strip() is '':
                continue
            command_output = os.popen(command).read().strip()
            log.info('%s -> %s' % (command, command_output))

            command_output_tokens = command_output.split()
            include_dirs += [option[2:] for option in command_output_tokens if option.startswith('-I')]
            library_dirs += [option[2:] for option in command_output_tokens if option.startswith('-L')]
            libraries += [option[2:] for option in command_output_tokens if option.startswith('-l')]

        include_dirs += options.get('include-dirs', '').split()
        library_dirs += options.get('library-dirs', '').split()
        libraries += options.get('libraries', '').split()

        options['cflags'] = ' '.join(['-I%s' % d for d in include_dirs])
        options['ldflags'] = ' '.join(['-L%s' % d for d in library_dirs]) + ' ' + \
            ' '.join(['-l%s' % n for n in libraries])
        options['include-dirs'] = ' '.join(include_dirs)
        options['library-dirs'] = ' '.join(library_dirs)
        options['libraries'] = ' '.join(libraries)
        log_template = \
'''
    include-dirs: %(include-dirs)s
    library-dirs: %(library-dirs)s
    libraries: %(libraries)s
    cflags: %(cflags)s
    ldflags: %(ldflags)s
''' 
        log.info(log_template % options)

    def update(self):
        pass

    def install(self):
        return ()
