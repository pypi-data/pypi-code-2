"""
Additional commands for database management:
Commands are:
    
    model create_sql drop_sql
"""

import sys
import os
from pylons import config as pylonsconfig
import pylons.util as util
from pylons.commands import validate_name,check_controller_existence


from paste.script.command import Command, BadCommand
from paste.script.appinstall import SetupCommand
from paste.script.filemaker import FileOp
from paste.util import import_string
from paste import deploy
from tempita import paste_script_template_renderer

try:
    import migrate.versioning.api as migrate_api
    from migrate.versioning.exceptions import KnownError, \
        DatabaseAlreadyControlledError
    use_migrate = True
except ImportError:
    use_migrate = False

class SqlCommand(Command):
    
    min_args = 1
    max_args = 2
    group_name = 'shabti'
    
    default_verbosity = 3
    
    parser = Command.standard_parser(simulate=True)
    
    parser.add_option('--echo',
                      action='store_true',
                      dest='echo',
                      help="Print output to STDOUT")
    
    parser.add_option('--setup',
                      action='store_true',
                      dest='setup',
                      help="Run websetup.py after tables created")
    
    parser.add_option('--table',
                      dest='table',
                      help="Perform action only on given table")
    
    def command(self):
        try:
            
            self.config_file = os.path.abspath(self.args[0])
            
            file_op = FileOp(source_dir=os.path.join(os.path.dirname(__file__)))
            base_package = file_op.find_dir('model', True)[0]
            package = __import__(base_package + '.model')
            model = package.model
            
            app = deploy.loadapp('config:' + self.config_file)
            
            # additional imports ...
            package = __import__(base_package + '.config.environment')
            environment = package.config.environment
            
            here_dir = os.path.dirname(__file__)
            conf_dir = os.path.dirname(os.path.dirname(here_dir))
            
            config_file = os.path.join(conf_dir, self.config_file)
            conf = deploy.appconfig('config:' + config_file)
            pylonsconfig = environment.load_environment(conf.global_conf, conf.local_conf)
            
            from sqlalchemy import engine_from_config
            engine = engine_from_config(pylonsconfig, 'sqlalchemy.')
            
            model.init_model(engine)
            metadata = model.metadata
            
            try:
                table = metadata.tables[self.options.table]
            except:
                table = None
            
            self.sql_command(metadata, table)
        
        except BadCommand, e:
            raise BadCommand('paster: an error occurred. %s' % e)
        except:
            msg = str(sys.exc_info()[1])
            raise BadCommand('paster: an unknown error occurred. %s' % msg)
    

class CreateSqlCommand(SqlCommand):
    """Create all model tables, or a single table
    
    The create_sql command will create all tables defined in the elixir metadata,
    or if a table name is passed it will create that table only.
    
    Example usage::
       yourproj% paster create_sql development.ini
       yourproj% paster create_sql --table=users development.ini
    
    This command will ignore any existing tables. Use the corresponding drop_sql
    command to delete tables.
    """
    
    summary = __doc__.splitlines()[0]
    usage = '\n' + __doc__
    
    def sql_command(self, metadata, table):
        if table is None:
            metadata.create_all()
        else:
            table.create()
        if self.options.setup:
            cmd = SetupCommand('setup-app')
            cmd.run([self.config_file])
    

class DropSqlCommand(SqlCommand):
    """Drop all model tables, or a single table
    
    The drop_sql command will drop all tables defined in the elixir metadata,
    or if a table name is passed it will create that table only.
    
    Example usage::
       yourproj% paster drop_sql development.ini
       yourproj% paster drop_sql --table=users development.ini
    
    Use the corresponding create_sql command to create tables.
    """
    
    summary = __doc__.splitlines()[0]
    usage = '\n' + __doc__
    
    def sql_command(self, metadata, table):
        if raw_input("Are you sure you want to drop these tables, and lose all your data (y/n)? ").lower() == 'y':
            if table is None:
                metadata.drop_all()
            else:
                table.drop()

class ResetSqlCommand(SqlCommand):
    """Drop all tables or selected table and re-creates them.
    
    Example usage::
       yourproj% paster reset_sql development.ini
       yourproj% paster reset_sql --table=users development.ini
    """
    
    summary = __doc__.splitlines()[0]
    usage = '\n' + __doc__
    
    def sql_command(self, metadata, table):
        if raw_input("Are you sure you want to drop these tables, and lose all your data (y/n)? ").lower() == 'y':
            if table is None:
                metadata.drop_all()
                metadata.create_all()
            else:
                table.drop()
                table.create()
            if self.options.setup:
                cmd = SetupCommand('setup-app')
                cmd.run([self.config_file])
    

class ModelCommand(Command):
    """Create a Model and accompanying unit test
    
    
    The model command will create stub files for a module for Elixir model classes
    and corresponding unit test module.
    
    Example usage::
        
        yourproj% paster model user
        Creating yourproj/yourproj/model/user.py
        Creating yourproj/yourproj/tests/unit/test_user.py
        Creating yourproj/yourproj/fixtures/user
    
    If you'd like to have models underneath a directory, just include
    the path as the model name and the necessary directories will be
    created for you::
        
        yourproj% paster model user/permissions
        Creating yourproj/model/user
        Creating yourproj/yourproj/model/user/permissions.py
        Creating yourproj/yourproj/tests/functional/test_user_permissions.py
        Creating yourproj/yourproj/fixtures/user
        Creating yourproj/yourproj/tests/fixtures/user
    
    """
    summary = __doc__.splitlines()[0]
    usage = '\n' + __doc__
    
    min_args = 1
    max_args = 1
    group_name = 'shabti'
    
    default_verbosity = 3
    
    parser = Command.standard_parser(simulate=True)
    parser.add_option('--no-test',
                      action='store_true',
                      dest='no_test',
                      help="Don't create the test; just the model")
    
    def command(self):
        """Main command to create model"""
        try:
            file_op = FileOp(source_dir=os.path.join(os.path.dirname(__file__)))
            try:
                name, directory = file_op.parse_path_name_args(self.args[0])
            except:
                raise BadCommand('No egg_info directory was found')
            
            # Check the name isn't the same as the package
            base_package = file_op.find_dir('model', True)[0]
            if base_package.lower() == name.lower():
                raise BadCommand(
                    'Your model name should not be the same as '
                    'the package name %r.'% base_package
            )
            # Validate the name
            name = name.replace('-', '_')
            validate_name(name)
            
            # Setup the model
            fullname = os.path.join(directory, name)
            model_name = util.class_name_from_module_name(
                name.split('/')[-1])
            if not fullname.startswith(os.sep):
                fullname = os.sep + fullname
            testname = fullname.replace(os.sep, '_')[1:]
            test_model_name = 'Test' + name[0].upper() + name[1:]
            file_op.template_vars.update({'name': model_name,
                                          'version':'0.1',
                                          'fname': os.path.join(directory, name),
                                          'package':base_package,
                                          'test_model_name':test_model_name,
                                          'package_logger':base_package,
                                          'sqlalchemy':True,
                                          'zip_safe':False})
            file_op.copy_file(template='model.py_tmpl',
                              dest=os.path.join('model', directory),
                              filename=name,
                              template_renderer=paste_script_template_renderer)
            file_op.copy_file(template='form.py_tmpl',
                              dest=os.path.join('model', 'forms', directory),
                              filename=name,
                              template_renderer=paste_script_template_renderer)
            file_op.ensure_dir(os.path.join(base_package, 'fixtures', name))
            if not self.options.no_test:
                file_op.copy_file(template='test_model.py_tmpl',
                             dest=os.path.join('tests', 'unit'),
                             filename='test_'+testname,
                              template_renderer=paste_script_template_renderer)
                file_op.ensure_dir(os.path.join(base_package, 'tests', 'fixtures', name))
        
        except BadCommand, e:
            raise BadCommand('An error occurred. %s' % e)
        except:
            msg = str(sys.exc_info()[1])
            raise BadCommand('An unknown error occurred. %s' % msg)
    

class RunnerCommand(Command):
    """Create and run background scripts
    
    To create a new script, type:
    paster runner --create myscript
    
    This creates a script, myscript.py, in a scripts/ directory.
    
    To run the script, type:
    paster runner myscript development.ini
    
    This will call the run() function in the script.
    
    """
    
    summary = __doc__.splitlines()[0]
    usage = '\n' + __doc__
    
    min_args = 1
    max_args = 2
    group_name = 'shabti'
    
    default_verbosity = 3
    
    parser = Command.standard_parser(simulate=True)
    parser.add_option('--create',
                      action='store_true',
                      dest='create',
                      help="Create a new runner script")
    
    def command(self):
        try:
            file_op = FileOp(source_dir=os.path.join(os.path.dirname(__file__)))
            try:
                name, directory = file_op.parse_path_name_args(self.args[0])
            except:
                raise BadCommand('No egg_info directory was found')
            
            # Check the name isn't the same as the package
            base_package = file_op.find_dir('scripts', True)[0]
            if base_package.lower() == name.lower():
                raise BadCommand(
                    'Your script name should not be the same as '
                    'the package name %r.'% base_package)
            # Validate the name
            name = name.replace('-', '_')
            validate_name(name)
            
            # Create the script
            fullname = os.path.join(directory, name)
            if self.options.create:
                if not fullname.startswith(os.sep):
                    fullname = os.sep + fullname
                file_op.template_vars.update({'package':base_package})
                file_op.copy_file(template='script.py_tmpl',
                                  dest=os.path.join('scripts', directory),
                                  filename=name,
                                  template_renderer=paste_script_template_renderer)
            else:
                 try:
                     config_file = os.path.abspath(self.args[1])
                 except IndexError:
                     raise BadCommand('Config filename must be provided')
                 
                 script_name = base_package + '.scripts.' + fullname.replace(os.path.sep, '.')
                 mod = import_string.try_import_module(script_name)
                 if mod is None :
                     raise BadCommand('Script %(name)s does not exist. Run paster runner --create %(name)s to create script',
                         dict(name = name))
                 mod.run(config_file)
        except BadCommand, e:
            raise BadCommand('An error occurred. %s' % e)
        except:
            msg = str(sys.exc_info()[1])
            raise BadCommand('An unknown error occurred. %s' % msg)
    

class MigrateCommand(Command):
    """Runs migration commands
    
    Handles migrate operations. Usage:
    paster migrate config.ini command [--dburi=uri] [--version=version] [--repository=repository] command_options...
    
    The following migrate commands are supported:
    
    script script_path - creates migration script
    test script_path - tests migration script (upgrade and downgrade)
    commit script_path - commits migration script to repository
    source [dest] - prints migration script of version to file or stdout
    version - repository version
    db_version  - database version
    upgrade [--preview_sql] [--preview_py] - upgrades db to next version
    downgrade [--preview_sql] [--preview_py] - downgrades db to previous version
    """
    
    summary = __doc__.splitlines()[0]
    usage = '\n' + __doc__
    
    min_args = 2
    group_name = 'shabti'
    
    default_verbosity = 3
    
    parser = Command.standard_parser(simulate=True)
    parser.add_option('--dburi',
                      dest='dburi',
                      help="Database URI string")
    
    parser.add_option('--repository',
                      dest='repository',
                      help="Repository directory")
    
    parser.add_option('--version',
                      dest='version',
                      help="Database version")
    
    parser.add_option('--version_table',
                      dest='version_table',
                      help="Database version table")
    
    parser.add_option('--preview_py',
                      action='store_true',
                      dest='preview_py',
                      help="Preview Python script before running")
    
    parser.add_option('--preview_sql',
                      action='store_true',
                      dest='preview_sql',
                      help="Preview SQL before running")
    
    def command(self):
        
        if not use_migrate:
            raise BadCommand('Migrate library must be installed to run migration commands')
        
        config_file = os.path.abspath(self.args[0])
        
        try:
            cmd = getattr(self, '_%s_command' % self.args[1])
        except AttributeError:
            raise BadCommand("%s is not a valid migrate command" % self.args[1])
        
        file_op = FileOp(source_dir=os.path.join(os.path.dirname(__file__)))
        app = deploy.loadapp('config:' + config_file)
        
        # create repository
        package_name = file_op.find_dir('.')[0]
        repository = self.options.repository or os.path.join(package_name, 'repository')
        try:
            migrate_api.create(repository, package_name, table = self.options.version_table)
        # except KnownError:
        except:
            pass # repository already created
        
        # add database to version control
        version = self.options.version
        dburi = self.options.dburi or pylonsconfig.get('sqlalchemy.default.uri')
        try:
            migrate_api.version_control(dburi, repository)
        # except DatabaseAlreadyControlledError:
        except:
            pass # database already under control
        
        # run command using pattern _<cmd>_command
        remaining_args = self.args[2:]
        result = cmd(dburi, repository, version, *remaining_args)
        if result: print result
    
    def _script_command(self, dburi, repository, version, script_path):
        return migrate_api.script(script_path, repository)
    
    def _commit_command(self, dburi, repository, version, script_path, database=None, operation = None):
        return migrate_api.commit(script_path, repository, database=database, operation=operation, version = version)
    
    def _test_command(self, dburi, repository, version, script_path):
        return migrate_api.test(script_path, repository, dburi=dburi)
    
    def _version_command(self, dburi, repository, version):
        return migrate_api.version(repository)
    
    def _db_version_command(self, dburi, repository, version):
        return migrate_api.db_version(dburi, repository)
    
    def _source_command(self, dburi, repository, version, dest=None):
        return migrate_api.source(version, dest, repository)
    
    def _upgrade_command(self, dburi, repository, version):
        return migrate_api.upgrade(dburi, repository, version,
                            preview_sql = self.options.preview_sql,
                            preview_py = self.options.preview_py)
    
    def _downgrade_command(self, dburi, repository, version):
        return migrate_api.downgrade(dburi, repository, version,
                            preview_sql = self.options.preview_sql,
                            preview_py = self.options.preview_py)
    
    def _drop_version_control_command(self, dburi, repository, version):
        return migrate_api.drop_version_control(dburi, repository)
    

def validate_name(name):
    """Validate that the name for the model isn't present on the
    path already"""
    if not name:
        # This happens when the name is an existing directory
        raise BadCommand('Please give the name of a model.')

import re
from sqlalchemy import types
#TODO: 1. formencode import and validations of:
#        - password
#        - email

class ScaffoldCommand(Command):
    """Create a RESTcontroller and accompanying mako scaffold templates
    
    The first argument should be the singular form of the REST resource, the
    second argument should be the plural name of the resource.
    """
    # Parser configuration
    summary = __doc__.splitlines()[0]
    usage = '\n' + __doc__
    
    min_args = 2
    max_args = 2
    group_name = "shabti"
    
    default_verbosity = 3
    
    parser = Command.standard_parser(simulate=True)
    parser.add_option('--no-test',
                      action='store_true',
                      dest='no_test',
                      help="Don't create the test; just the controller + views")
    
    
    def _modify_routes_py(self):
        """create routes for the resource"""
        routesfile = open(self.package+'/config/routing.py','r')
        lines = routesfile.readlines()
        routesfile.close()
        
        mapping = '    map.resource(\''+self.singularname+'\',\''+self.pluralname+'\')\n'
        if mapping in lines:
            print 'Warning! Routes mapping was found in routes.py. Please double-check the file!'
        else:
            s = re.compile('\s*#\s*CUSTOM ROUTES HERE')
            ln,found = 0,False
            for line in lines:
                if s.match(line):
                    lines.insert(ln+1,mapping)
                    found=True
                    break
                ln+=1
            
            if not found:
                print '# CUSTOM ROUTES HERE line was not found in the config/routes.py file.'\
                      ' You have to maually add the statement\n' + mapping + \
                      'to your routes.py'
            else:
                routesfile = open(self.package+'/config/routing.py','w')
                routesfile.writelines(lines)
                routesfile.close()
    
    def _form_for(self):
        fields = {  types.Integer       : 'text',
                    types.SmallInteger  : 'text',
                    types.String        : 'text',
                    types.Unicode       : 'text',
                    types.Text          : 'textarea',
                    types.UnicodeText   : 'textarea',
                    types.Time          : 'text',
                    types.Binary        : 'textarea',
                    types.Boolean       : 'checkbox',
                    types.Date          : 'date',
                    types.DateTime      : 'date',
                    types.Float         : 'text'
        }
        
        text = '<table class = "edit_form">\n'
        for col in self.scaffolded_class._sa_class_manager.mapper.c:
            if col.name not in ['id','created_at','updated_at']:
                try:
                    tag = fields[col.type.__class__]
                except KeyError:
                    tag = 'text'
                text+='    <tr>\n'
                text+='        <td>' + col.name + '</td>\n'
                if tag=='textarea':
                    text+='        <td>${c.model_tags.'+tag+'(\''+col.name+'\',cols=30,rows=10)}</td>\n'
                else:
                    text+='        <td>${c.model_tags.'+tag+'(\''+col.name+'\')}</td>\n'
                text+='    </tr>\n'
        text+='</table>\n'
        return text
    
    def _create_form(self,action):
        text = '<%inherit file="base.mako" />\n'
        if action=='new':
            text+="${h.form(h.url('"+self.pluralname+"'))}\n"
        elif action=='edit':
            text+= "${h.form(h.url('"+self.singularname+"',id=c.entry.id),method='put')}\n"
        else:
            raise Exception('unknown form method!')
        text+= self._form_for()
        text+= "${h.submit('Save','Save')}\n"
        return text
    
    def _create_show_template(self):
        text ='<%inherit file="base.mako" />\n'
        text+='<table>\n'
        for col in self.scaffolded_class._sa_class_manager.mapper.c:
            text+='    <tr><td>'+col.name+'</td><td>'+'${c.entry.'+col.name+'} </td></tr>\n'
        text+='</table>\n'
        text+="${h.link_to('List',h.url('"+self.pluralname+"'))}\n"
        text+="${h.link_to('Edit',h.url('edit_"+self.singularname+"',id=c.entry.id))}\n"
        return text
    
    def _create_list_template(self):
        text ='<%inherit file="base.mako" />\n'
        text+='<h1>Listing '+self.pluralclassname+'</h1>\n'
        text+='<table>\n'
        text+='    <tr>\n'
        for col in self.scaffolded_class._sa_class_manager.mapper.c:
            text+='        <th>'+col.name.capitalize()+'</th>\n'
        text+='        <th>Actions</th>\n'
        text+='    </tr>\n'
        text+='    % for entry in c.entries:\n'
        text+='    <tr>\n'
        for col in self.scaffolded_class._sa_class_manager.mapper.c:
            text+='        <td>${entry.' + col.name + '}</td>\n'
        text+='        <td>${h.link_to(\'Show\',h.url(\''+self.singularname+'\', id = entry.id))}'
        text+=' ${h.link_to(\'Edit\',h.url(\'edit_'+self.singularname+'\', id = entry.id))}'
        text+=' ${h.link_to(\'Destroy\',h.url(\''+self.singularname+'\', id = entry.id), '
        #this is taken directly from rails scaffold code (except for the authenticity token)
        text+='onclick="if (confirm(\'Are you sure?\')) '
        text+='{var f = document.createElement(\'form\');f.style.display = \'none\';'+\
              ' this.parentNode.appendChild(f);f.method = \'POST\';f.action = this.href;'+\
              ' var m = document.createElement(\'input\'); m.setAttribute(\'type\', \'hidden\'); '+\
              'm.setAttribute(\'name\', \'_method\'); m.setAttribute(\'value\', \'delete\'); f.appendChild(m);'+\
              ' var s = document.createElement(\'input\'); s.setAttribute(\'type\', \'hidden\'); '+\
              'f.appendChild(s);f.submit(); }; return false;")}'
        text+='</td>\n'
        text+='    </tr>\n'
        text+='    % endfor\n'
        text+='</table>\n'
        text+='${h.link_to(\'New\',h.url(\'new_'+self.singularname+'\'))}'
        return text
    
    def command(self):
        file_op = FileOp(source_dir = os.path.join(
            os.path.dirname(__file__), 'templates/scaffolding'))
        self.singularname = self.args[0]
        self.pluralname = self.args[1]
        
        #check that the controller name is not the same as package name
        self.package = file_op.find_dir('controllers', True)[0]
        if self.package.lower() == self.pluralname.lower():
            raise BadCommand(
                'Your controller name should not be the same as '
                'the package name %r.'% self.package)
        
        #check that the name is OK
        checkname = self.pluralname.replace('-','_')
        validate_name(checkname)
        #check_controller_existance(self.package,checkname)
        
        self.classname = util.class_name_from_module_name(self.singularname)
        self.pluralclassname = util.class_name_from_module_name(self.pluralname)
        
        #import the module class
        exec('from '+self.package+'.model import '+self.classname)
        exec('self.scaffolded_class = '+self.classname)
        
        file_op.template_vars.update(
            {'classname':self.classname,
             'pluralclassname':self.pluralclassname,
             'package':self.package,
             'title':self.package.capitalize(),
             'pluralname':self.pluralname,
             'singularname':self.singularname,
             'columns_list':str(self.scaffolded_class._sa_class_manager.mapper.c.keys()),
             'editable_columns_list':str([x for x in self.scaffolded_class._sa_class_manager.mapper.c.keys() if x not in ('id','created_at','updated_at')])})
        #create the controller
        file_op.copy_file(template='altcontroller.py_tmpl',
                          dest='controllers',
                          filename=self.pluralname.replace('-','_'),
                          template_renderer=paste_script_template_renderer)
        file_op.ensure_dir(self.package+'/templates/'+self.pluralname)
        #copy mako scaffold templates
        for filename in os.listdir(os.path.join(os.path.dirname(__file__),
                                  'templates/scaffolding/templates')):
            print filename
            file_op.copy_file(template='templates/'+filename,
                              filename=filename.split('.')[0]+'.mako',
                              add_py=False,
                              dest='templates/'+self.pluralname+'/',
                              template_renderer=paste_script_template_renderer)
        #copy css
        file_op.ensure_dir(self.package+'/public/css')
        file_op.copy_file(template='scaffold.css_tmpl',
                          dest='public/css',
                          filename='scaffold.css',
                          add_py=False,
                          template_renderer=paste_script_template_renderer)
        
        #copy test file
        if not self.options.no_test:
            file_op.copy_file(
                template='test_restcontroller.py_tmpl',
                dest=os.path.join('tests', 'functional'),
                filename='test_' + self.pluralname,
                template_renderer=paste_script_template_renderer)
        
        
        self._modify_routes_py()
        
        #create templates
        for action in ['new','edit']:
            file_op.ensure_file(self.package+'/templates/'+self.pluralname+'/'+action+'.mako',
                                self._create_form(action)
                                )
        file_op.ensure_file(self.package+'/templates/'+self.pluralname+'/show.mako',
                            self._create_show_template()
                            )
        file_op.ensure_file(self.package+'/templates/'+self.pluralname+'/list.mako',
                            self._create_list_template()
                            )
    
