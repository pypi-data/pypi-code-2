# -*- coding: utf-8 -*-
import os
import sys


def configure(app_id, config_file='conf.yaml'):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    fh = open(os.path.join(current_dir, config_file), 'r')
    config = yaml.load(fh)
    fh.close()
    config['settings']['app_id'] = app_id
    return config


def execute_from_command_line():
    args = sys.argv[1:]
    if len(args) < 1:
        print 'Usage: startappengineproject [app_id]'
        sys.exit(-1)
    
    config = configure(args[0])
    
#    file_mapping = config['files'] # destination: template
#    local_file_mapping = config.get('local_files', []) # destination: template
#    directories = config['directories'] # list of shortcut: path
#    copy_dirs = config['copy'] # dirs to copy into new env
#    config = config['settings'] # move settings to top level
#    
#    # create a django context to use for rendering project templates
#    context = Context(config)
#    
#    # create a new virtualenv for the project
#    print 'Creating a virtualenv for the project'
#    os.system('cd %(base_site)s && virtualenv --no-site-packages %(site_name)s' % context)

#    # create the directory structure for the site
#    for directory_dict in directories:
#        for k, v in directory_dict.items():
#            try:
#                os.makedirs(v % context)
#            except OSError, e:
#                if e.errno != 17:
#                    raise

#    # write all files
#    for destination, template_name in file_mapping.items():
#        write_template(template_name, destination, context)

#    # write local versions of the config files
#    context['local'] = True
#    for destination, template_name in local_file_mapping.items():
#        write_template(template_name, destination, context)

#    for src, dest in copy_dirs.items():
#        dest = dest % config
#        print 'Copying %s' % src
#        os.system('cp -R %s %s' % (src, dest))

    print 'Done!'

