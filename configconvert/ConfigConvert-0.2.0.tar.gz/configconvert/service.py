import getopt
import sys
import os
import logging
import logging.config
import warnings

from bn import absimport, AttributeDict, uniform_path
from configconvert import existingDirectory, existingFile, parse_config,\
   handle_option_error, handle_section_error, split_options

#
# Helpers
#

#def create_config(config_file, logging=True):
#    if not os.path.exists(config_file):
#        raise getopt.GetoptError('No such file %r'%config_file)
#    options = parse_config(config_file)
#    if not options.has_key('app.package'):
#        raise getopt.GetoptError(
#            "No 'app.package' option found in config file specified"
#        )
#    # Set some key parts and move to the correct directory
#    set_up_app_options(options, config_file)
#    # Load the config object
#    config = absimport(
#        options['app.package']+'.framework.config',
#    ).on_load_config(options)
#    if logging:
#        set_up_logging(config)
#    return config
#
#def set_up_logging(config, logging_file=None):
#    if logging_file is None:
#        if config.option_group.has_key('logging'):
#            logging_file = config.option_group['logging'].get('filename')
#    if logging_file is None:
#        logging_file = config.app.config_file[:-5]+'.logging'
#    if not os.path.exists(logging_file):
#        raise getopt.GetoptError(
#            "Could not find logging configutaion file %r"%logging_file
#        )
#    logging.config.fileConfig(logging_file)
#    logging_handlers = []
#    in_loggers = False
#    fp = open(logging_file)
#    for line in fp:
#        if line.startswith('[loggers]'):
#            in_loggers = True
#        if in_loggers and line.startswith('keys') and '=' in line:
#            for handler in line[line.find('=')+1:].strip().split(','):
#                logging_handlers.append(handler.strip())
#            break
#    fp.close()
#    if not 'flows' in logging_handlers:
#        warnings.warn(
#            "The 'flows' module does not have a logger set up"
#        )
#    config['logging'] = AttributeDict(handlers=logging_handlers)
#
#def set_up_app_options(options, config_file):
#    # Set the app settings
#    for auto_generated in [
#        'app.app_dir', 
#        'app.deploy_dir', 
#        'app.config_file'
#    ]:
#        if options.has_key(auto_generated):
#            raise Exception(
#                'The option %r is auto-generated and should not appear in '
#                'the config file'%(auto_generated,)
#            )
#    options['app.app_dir'] = __import__(options['app.package']).__path__[0]
#    options['app.config_file'] = uniform_path(config_file)
#    options['app.deploy_dir'] = os.path.split(options['app.config_file'])[0]
#    os.chdir(options['app.deploy_dir'])

#def parse_and_split_options_change_dir(service, filename):
#    """\
#    This function is where you can set up your settings. Ordinarily, 
#    settings which you want end users to configure should go in the 
#    config file, settings which the developer needs control over can
#    go here.
#    """
#    if not os.path.exists(filename):
#        raise getopt.GetoptError('No such file %r'%filename)
#    os.chdir(os.path.join(*os.path.split(os.path.abspath(filename))[:-1]))
#    #print os.getcwd()
#    options = parse_config(filename)
#    # Split up the setting into parts
#    option_group = split_options(options)
#    return option_group

#def configFromFile():
#    def configFromFile_constructor(service):
#        name = service.name
#        def start(service):
#            def parse_config(service, filename):
#                service.boot['option'].update(parse_and_validate_options(service, filename))
#            service[name] = parse_config
#        return AttributeDict(start=start)
#    return configFromFile_constructor
        

