'''
Commands Module
===============

Commands are classes that encapsulate a set of actions based on a config.
Each class registers itself on the command line so that it is callable from
there but can also be called programmatically. 
'''

license = ''' Copyright (C) 2011  <see AUTHORS file>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

# E1101: pylint thinks self.LOGGER is undefined, but it's created in the meta class
# pylint: disable=E1101

from py2facer.lib import picasa, image
from py2facer.lib.flickr import FlickrImageManager, FlickrContactManager, \
    FlickrAPIManager, DbProxy
from py2facer.lib.utils import InvalidConfig
import ConfigParser
import argparse
import logging
import os

#: The sort-of global ArgumentParser. This is where all the CLI options end up.
CLI_PARSER = argparse.ArgumentParser()
#: The sort-of global subparser, so that sub commands a-la svn style can exist.
CLI_SUBPARSER = CLI_PARSER.add_subparsers()
LOGGER = logging.getLogger('commands.base')

class Command_Base(type):
    def __init__(cls, name, bases, attrs):
        '''Use metaclass magic for good, not evil.
        
        This metaclass:
        
        * registers each new Command subclass with the :data:`CLI_PARSER` 
        * does some basic validation on the structure of the classes
        
        '''
        
        super(Command_Base, cls).__init__(name, bases, attrs)
        if name == 'BaseCommand':
            return
        if not hasattr(cls, 'COMMAND') or cls.COMMAND is None:
            raise Exception('Class <%s> must define the static var COMMAND' % name)
        if hasattr(cls, 'OPTIONS') and cls.OPTIONS is not None:
            parser = CLI_SUBPARSER.add_parser(cls.COMMAND)
            parser.set_defaults(COMMAND=cls)
            for option in cls.OPTIONS:
                if 'args' not in option:
                    raise Exception('Class <%s> must define args in each option in OPTIONS' % name)
                if 'kwargs' not in option:
                    raise Exception('Class <%s> must define kwargs in each option in OPTIONS' % name)
                parser.add_argument(*(option['args']), **(option['kwargs']))
        if not hasattr(cls, 'LOGGER') or cls.LOGGER is None:
            cls.LOGGER = LOGGER.getChild(name)
        
class BaseCommand(object):
    '''The base from which all CLI commands are derived.
    
        A BaseCommand object must have have several class variables:
        
        * :attr:`COMMAND` **MUST** be a UNIQUE :obj:`str` which will be used as a
          sub-parser of :data:`CLI_SUBPARSER`
        * :attr:`OPTIONS` **MUST** be a :obj:`list` of :obj:`dict` objects. Each
          :obj:`dict` **MUST** be of the form::
          
              {'args' : ('-switch', '--long_switch'), # This may be a 1-tuple
               'kwargs' : {[OPTIONS TO PASS TO parser.add_argument]}
              }
        
        When a Command object is created and executed it 
        
        #. Sets up a basic empty :attr:`cmd_config` with defaults that come
           from :attr:`OPTIONS` (via :meth:`_create_cmd_config`)
        #. Attempts to read the ini config and set options in :attr:`cmd_config`
           base on what it finds. If there is no ini then this is skipped
           (via :meth:`ini_config`)
        #. Set any options that came in from the :meth:`__init__` call (via
           :meth:`api_config`)
        #. Set any options that came in from the command line (via 
           :meth:`cli_config`)
        #. Check that the final resultant config is sane (via 
           :meth:`check_config`)
        #. Actually do the command (via :meth:`do_command`)
        
        Outside users of a Command object are expected to init the object
        (possibly with kwargs if only calling from the API) and then to call
        :meth:`execute`
        
        :ivar cmd_config: A :obj:`dict` of all cleaned settings for tclse Command 
            object.
        :ivar _api_config: A :obj:`dict` of all the kwargs passed in to 
            :meth:`__init__`
        '''
    __metaclass__ = Command_Base
    #: Defines the py2TheFaceR.py COMMAND [options] part of the CLI interface
    COMMAND = ''
    #: Options that are provided to the argparse module via the meta-class
    OPTIONS = [{'args' : ('-c', '--config'), 
                'kwargs' : {'help': 'ini file to use for config options',
                            'action' : 'store',
                            'dest' : 'config'}},
               {'args' : ('--db-url',),
                'kwargs' : {'help' : 'the URL to use for the DB '
                                     '(e.g. sqlite:///file.db',
                            'dest' : 'db_url'}}]
    #: The INI section name additional config may be defined in
    INI_SECTION = ConfigParser.DEFAULTSECT
    #: The keywords to expect in INI_SECTION
    INI_OPTIONS = ['db_url',]
    
    def __init__(self, **kwargs):
        self.cmd_config = {}
        self._create_cmd_config()
        self._api_config = kwargs
    
    def _create_cmd_config(self):
        for option in self.OPTIONS:
            if 'kwargs' in option and 'dest' in option['kwargs']:
                optname = option['kwargs']['dest']
                if 'default' in option['kwargs']:
                    self.cmd_config[optname] = option['kwargs']['default']
                else:
                    self.cmd_config[optname] = None
                        
    def api_config(self, api_config):
        '''Update cmd_config using the destinations defined in :attr:`OPTIONS`
        
        :params api_config: The kwargs passed in to the :meth:`__init__`
        :type api_config: :obj:`dict`
        '''
        
        if api_config is None:
            return
        for option in self.OPTIONS:
            if 'kwargs' in option and 'dest' in option['kwargs']:
                optname = option['kwargs']['dest']
                if optname not in api_config:
                    if 'required' in option['kwargs'] and option['kwargs']['required']:
                        raise InvalidConfig('%s is required via API config' % optname)
                    continue
                self.cmd_config[optname] = api_config[optname]
    
    def ini_config(self, cfg_parser):
        '''Base level parser. This method should be overridden by a child class
        
        :param cfg_parser: One that has already loaded the ini file
        :type cfg_parser: :obj:`ConfigParser.SafeConfigParser`
        '''
        
        if cfg_parser.has_option(ConfigParser.DEFAULTSECT, 'db_url'):
            self.cmd_config['db_url'] = cfg_parser.get(ConfigParser.DEFAULTSECT, 'db_url')
        
    def check_config(self):
        '''Last chance to catch semantic errors in the config before executing
        '''
        
        raise NotImplementedError()
        
    def cli_config(self, cli_settings):
        '''Migrates the config from the argparser to :attr:`cmd_config`
        
        :param cli_settings:
        '''
        
        for option in self.OPTIONS:
            if 'kwargs' in option and 'dest' in option['kwargs']:
                optname = option['kwargs']['dest']
                if not hasattr(cli_settings, optname):
                    continue
                if getattr(cli_settings, optname) != getattr(option['kwargs'], 'default', None):
                    self.cmd_config[optname] = getattr(cli_settings, optname)
    
    def do_command(self):
        raise NotImplementedError()
    
    def execute(self, ini_file=None, cli_args=None):
        # Setting priority (highest to lowest) is CLI, API, INI, Defaults
        if cli_args is not None and cli_args.config is not None:
            self.LOGGER.debug('ini_file set from command line')
            ini_file = cli_args.config
        if ini_file is not None:
            parser = ConfigParser.SafeConfigParser()
            self.LOGGER.debug('Reading ini config %s', ini_file)
            with open(ini_file, 'r+') as ini_fp:
                parser.readfp(ini_fp, filename=ini_file)
            self.ini_config(cfg_parser=parser)
        if len(self._api_config) > 0:
            self.LOGGER.debug('Applying config from API call')
            self.api_config(self._api_config)
        if cli_args is not None:
            self.LOGGER.debug('Applying CLI config')
            self.cli_config(cli_args)
        self.check_config()
        self.do_command()

class SyncContacts(BaseCommand):
    '''Link a set of Google contacts with the corresponding flickr id's 
    '''
    
    COMMAND = 'sync-contacts'
    OPTIONS = BaseCommand.OPTIONS + \
              [{'args' : ('-r', '--recheck'), 
                'kwargs' : {'help' : 'Ask flickr about google contacts that were previously not found',
                            'action' : 'store_true',
                            'dest' : 'recheck',
                            'default' : False}},
                {'args' : ('--contacts',),
                 'kwargs' : {'help' : 'The contacts.xml file to use',
                             'action' : 'store',
                             'dest' : 'contacts_path',
                             'default' : None}}]
    INI_SECTION = 'CONTACTS'
    INI_OPTIONS = ['contacts_path',]
    
    def ini_config(self, cfg_parser):
        super(SyncContacts, self).ini_config(cfg_parser)
        if cfg_parser.has_option(ConfigParser.DEFAULTSECT, 'contact_file'):
            self.cmd_config['contacts_path'] = cfg_parser.get(ConfigParser.DEFAULTSECT, 'contact_file')
            
    def check_config(self):
        if self.cmd_config['db_url'] is None:
            raise InvalidConfig('db_url must be defined to use %s' % self.COMMAND)
        
    def do_command(self):
        contacts_xml = self._get_contacts_file()
        self.LOGGER.info('Parsing contacts file: %s', contacts_xml)
        gcontacts = picasa.ContactParser()
        with open(contacts_xml, 'r') as contacts_file:
            gcontacts.parse_xml(contacts_file)
        db_proxy = DbProxy(db_url=self.cmd_config['db_url'])
        fcm = FlickrContactManager(db_proxy=db_proxy)
        fapi = FlickrAPIManager()
        self.LOGGER.info('Logging into flickr')
        fapi.login()
        self.LOGGER.info('Syncing contacts')
        fcm.sync_flickr(google_contacts=gcontacts, 
                        force_recheck=self.cmd_config['recheck'], 
                        flickr_proxy=fapi)
        
    def _get_contacts_file(self):
        '''Search for a contacts.xml file from CLI, config and in generic locations.
    
        :param cli_args: argparse output
        :param config: ConfigParser instance (which has already read an ini file)
        :return: The full path of the first contacts.xml found
        :rtype: :obj:`str`
        '''
        
        def find(paths):
            if type(paths) not in (tuple, list):
                paths = [paths,]
            for path in paths:
                if os.path.exists(path):
                    return os.path.abspath(path)
                return None
        # Early attempt to find file
        if self.cmd_config['contacts_path'] is not None:
            self.LOGGER.debug('Checking for contacts.xml in %s', self.cmd_config['contacts_path'])
            file_path = find(self.cmd_config['contacts_path'])
            if file_path is not None:
                return file_path
        # Try to find a couple of the default locations for the contacts.xml file
        paths = []
        suffix = 'Google/Picasa2/contacts/contacts.xml'
        envvars = ('LOCALAPPDATA', 'APPDATA')
        for var in envvars:
            if os.environ.has_key(var):
                # Windows machine, but this can map to many places
                paths.append('%s/%s' % (os.environ[var], suffix))
        #TODO: Need to look into where Linux machines stuff this file by default
        self.LOGGER.debug('Further checking for contacts.xml in %s', paths)
        result = find(paths)
        if result is None:
            raise InvalidConfig('Unable to find a contacts.xml file to use')
        return result

class SyncPhotos(BaseCommand):
    '''For a set of photos add the facial data to flickr using the the database
    as a reference for Google contact --> flickr user
    '''
    
    COMMAND = 'sync-photos'
    OPTIONS = BaseCommand.OPTIONS + \
              [{'args' : ('-d', '--dir'),
                'kwargs' : {'help' : 'Add a directory of photos to sync',
                            'action' : 'append',
                            'dest' : 'dirs',
                            'default' : []}},
               {'args' : ('-f', '--file'),
                'kwargs' : {'help' : 'Add a single photo to sync',
                            'action' : 'append',
                            'dest' : 'files',
                            'default' : []}},
               {'args' : ('--contacts',),
                'kwargs' : {'help' : 'The contacts.xml file to use',
                            'action' : 'store',
                            'dest' : 'contacts_path',
                            'default' : None}}]
    
    INI_SECTION = 'CONTACTS'
    INI_OPTIONS = ['contacts_path',]
    
    def ini_config(self, cfg_parser):
        super(SyncPhotos, self).ini_config(cfg_parser)
        if cfg_parser.has_option(ConfigParser.DEFAULTSECT, 'contact_file'):
            self.cmd_config['contacts_path'] = cfg_parser.get(ConfigParser.DEFAULTSECT, 'contact_file')
        
    def check_config(self):
        if self.cmd_config['db_url'] is None:
            raise InvalidConfig('db_url must be defined to use %s' % self.COMMAND)
        
    def do_command(self):
        # First create all the photos objects
        iniparser = picasa.FaceParser()
        #TODO: Make location parsing optional
        self.LOGGER.info('Loading images.')
        images = []
        for directory in self.cmd_config['dirs']:
            images.extend(image.dir_images(directory))
        for filename in self.cmd_config['files']:
            if os.path.splitext(filename)[1].lower() == '.jpg':
                images.append(image.Image(image_path=filename))
        self.LOGGER.info('Loaded %d images', len(images))
        self.LOGGER.info('Parsing facial data from Picasa.')
        iniparser.add_people_to_image(images)
        db_proxy = DbProxy(db_url=self.cmd_config['db_url'])
        api_mgr = FlickrAPIManager()
        img_mgr = FlickrImageManager(db_proxy=db_proxy, flickr_proxy=api_mgr)
        img_mgr.add_photo(images)
        self.LOGGER.info('Finding corresponding images on Flickr')
        img_mgr.link_photos()
        self.LOGGER.info('Pushing facial data to Flickr')
        img_mgr.sync_faces()
