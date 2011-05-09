#!/usr/bin/python

# Copyright (c) 2011. All Right Reserved, http://chart.io/
#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY 
# KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

import ConfigParser
import getpass
import os
import random
import string
import subprocess
import sys
import time
import urllib
import urllib2

try:
    import json
except:
    import simplejson as json

KEY = 'FEUUB1JB4MHNHZ474R14VW3K62XGNP466GPRMD1N3WF5ER047DTOXUO190KXR2VFBO31XTDOODU2H7XNDRL6EA8D5F5HUC52LMHW'
BASE_URL = 'https://chart.io'
VERSION = 1
SSH_KEY = '/etc/chartio/sshkey/id_rsa'
CONFIG_FILE = '/etc/chartio/chartio.cfg'


class TermColor(object):
    """ Print colored text to terminal """
    CLRS = {
        'blue': '\033[94m',
        'green': '\033[92m',
        'red': '\033[91m',
    }

    END = '\033[0m'

    @classmethod
    def print_clr(cls, color, txt, newline=True):
        sys.stdout.write(cls.CLRS.get(color, '') + txt + cls.END)
        if newline:
            sys.stdout.write('\n')

    @classmethod
    def print_header(cls, txt, newline=True):
        cls.print_clr('blue', txt, newline)

    @classmethod
    def print_ok(cls, txt, newline=True):
        cls.print_clr('green', txt, newline)

    @classmethod
    def print_error(cls, txt, newline=True):
        cls.print_clr('red', txt, newline)

    @classmethod
    def print_delay(cls, txt, newline=True):
        cls.print_clr('red', '==> ', False)
        cls.print_ok(txt, newline)


def get_choice(question, choices, default=None):
    """ 
    list a question and a bunch of choices for them
    
    choice = get_choice('What fruit do you want?', ['apples', 'oranges'], 'apples')
    print "choice", choice
    """
    TermColor.print_header(question)

    for i, c in enumerate(choices):
        TermColor.print_ok("    %d." % (i + 1), False)
        print " %s" % c

    prompt = ": "
    if default is not None:
        prompt = "[%d]: " % (choices.index(default) + 1)
    
    try:
        num = int(raw_input(prompt)) - 1
    except (TypeError, ValueError), e:
        return default or get_choice(question, choices, default)
    
    
    if num < 0 or num >= len(choices):
        TermColor.print_error("ERROR: choice not in range\n")
        return get_choice(question, choices, default)

    return choices[num]


def get_value(name, default=None, validate=None, validate_explination=None, 
        password=False):
    """ propmpts for a value from the user """

    if validate is None:
        validate = lambda x: bool(x)
        
    prompt = "%s: " % name
    if default:
        prompt = "%s [%s]: " % (name, default)

    TermColor.print_header(prompt, False)
    if password:
        r = getpass.getpass('')
    else:
        r = raw_input()
        
    if validate:
        if not validate(r):
            if default:
                return default
            TermColor.print_error(validate_explination or 
                "Invalid Input.  Please try again.")
            return get_value(name, default, validate, validate_explination)
        
    return r


class DatasourceConfig(object):
    """ Configuration steps class. kvs in self.settings get sent as post 
        params """

    def __init__(self):
        self.settings = {}
        self.temp = {}

    def get_steps(self):
        return []

    def run_steps(self):
        for step in self.get_steps():
            step()

    @staticmethod
    def get_random_password(length=10):
        pw = []
        chars = string.letters + string.digits
        for c in range(length):
            pw.append(random.choice(chars))
        return ''.join(pw)


class MysqlConfig(DatasourceConfig):

    def get_steps(self):
        return [
            self.welcome,
            self.get_username,
            self.get_password,
            self.get_dbname,
            self.get_port,
            self.create_user
        ]

    def welcome(self):
        TermColor.print_header("MySQL database setup.")

    def get_username(self):
        TermColor.print_header("Please enter the database administrator's name\n"
            "This will only be used during setup to create a read-only user.")
        self.temp['superuser'] = get_value('Database username')

    def get_password(self):
        TermColor.print_header("Please enter the password for this account")
        self.temp['superuser_pw'] = get_value('Administrator\'s pasword', 
                                        password=True)

    def get_databases(self):
        sql = 'SHOW DATABASES'
        tbls = self._run_sql(sql)
        if tbls is None:
            TermColor.print_error("Could not load database tables using "
                "SHOW DATABASES command")
            sys.exit(1)
        out = tbls.split()
        return out[1:] # strip "Database" field

    def get_dbname(self):
        TermColor.print_header("Select which database to add.")
        self.settings['name'] = get_choice('Database name', 
                                    self.get_databases())

    def get_port(self):
        port = get_value('Database port', '3306')
        self.settings['port'] = port
        write_conf('localport', port)

    def create_user(self):
        TermColor.print_delay('Creating read-only user')
        dbname = self.settings['name']
        user = 'chartio'
        password = self.get_random_password()

        sql = "GRANT SELECT ON %(dbname)s.* TO `%(user)s`@`localhost` " \
              "IDENTIFIED BY '%(password)s'" % self._sanitize_sql_dict(locals())
        out = self._run_sql(sql)
        if out is None:
            TermColor.print_error("Creating read-only user failed.")
            print "Please execute the following command to create the user:"
            print "    ", sql
        else:
            TermColor.print_ok("Read only user created.")

        self.settings['user'] = user
        self.settings['passwd'] = password

    
    def _sanitize_sql_dict(self, dict_):
        out = {}
        for k, v in dict_.items():
            if isinstance(v, basestring):
                v = v.replace("'", "''")
            out[k] = v

        return out

    def _run_sql(self, sql, dbname=None):
        if 'superuser' not in self.temp:
            raise RuntimeError("Can only run after setting up superuser")
        cmd = [
            'mysql', 
            '-u', self.temp['superuser'],
            '--password=%s' % self.temp['superuser_pw']
            ]
        if dbname:
            cmd.append(dbname)
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, 
                stdout=subprocess.PIPE)
        proc.stdin.write(sql)
        proc.stdin.close()
        out = proc.stdout.read()
        proc.wait()

        if proc.poll() > 0:
            return None

        return out


class PostgresConfig(DatasourceConfig):
    
    def get_steps(self):
        return [
            self.welcome,
            self.get_dbname,
            self.get_port,
            self.create_user
        ]

    def welcome(self):
        TermColor.print_header("PostgreSQL database setup.")

    def get_dbname(self):
        self.settings['name'] = get_value('Database name')

    def get_port(self):
        port = get_value('Database port', '5432')
        self.settings['port'] = port
        write_conf('localport', port)

    def create_user(self):
        create_read_only = True
        while create_read_only:
            print "Please enter a user with the ability to add additional users"


def post(opener, url, data=None):
    """ just a simple post request wrapper """

    if data is None:
        data = {}

    if not url.count('http'):
        url = BASE_URL + url
        
    data['key'] = KEY

    encoded_args = urllib.urlencode(data)
    try:
        response = opener.open(url, encoded_args)
    except urllib2.HTTPError, e:
        TermColor.print_error("Error connecting to Chart.io's server. Please "
                              "try again later.")
        sys.exit(1)
    
    return response.read()


def write_conf(key, value, section='SSHTunnel'):
    ''' Write a config key and value to the SSHTunnel section '''
    conf = ConfigParser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        conf.read(CONFIG_FILE)
    if section not in conf.sections():
        conf.add_section(section)
    conf.set(section, key, value)
    f = open(CONFIG_FILE, 'w')
    conf.write(f)
    f.close()


def get_conf(key, section='SSHTunnel'):
    """ Get a config value, or None """
    conf = ConfigParser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        return None
    conf.read(CONFIG_FILE)
    try:
        return conf.get(section, key)
    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError), e:
        return None


def main():

    print 'Welcome to the chart.io setup wizard.'

    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    urllib2.install_opener(opener)
    
    email = get_value('Enter the email address registered with chart.io',
            validate = lambda x: x.count('@') > 0, 
            validate_explination = 'This is not a correct email')
    password = get_value('Enter your chart.io password', password = True)

    # Login user
    response = post(opener, '/connectionclient/login/', {
        'email': email,
        'password': password,
    })

    if response != 'success':
        TermColor.print_error(response)
        sys.exit(1)

    if os.path.exists(SSH_KEY):
        TermColor.print_ok("SSH key found. Using the existing ssh key.")
    else:
        TermColor.print_ok("Generating keys for ssh tunneling")
        ret = subprocess.call([
            'ssh-keygen',
            '-q', # shhh!
            '-N', '', # No passphrase
            '-C', 'chart.io ssh tunneling',
            '-t', 'rsa',
            '-f', SSH_KEY,
        ])

        if ret != 0:
            TermColor.print_error(
                    "Failed to generate ssh key. Please confirm you have " \
                    "ssh-keygen installed.")
            sys.exit(1)
        TermColor.print_ok("Done")

    if not get_conf('client_id'):
        TermColor.print_delay("Creating tunnel account on chart.io's server. " \
              "This will take a moment.")
        ssh_key = open('%s.pub' % SSH_KEY).read()
        response = post(opener, '/connectionclient/create/', { 
            'email': email,
            'password': password,
            'ssh_key': ssh_key,
            'version': VERSION
        })
            
        response = json.loads(response)

        write_conf('remotehost', response['connection']['server_hostname'])
        write_conf('remoteuser', response['connection']['server_username'])
        write_conf('remoteport', response['connection']['port'])
        write_conf('client_id', response['connection']['connectionclient_id'])
    else:
        TermColor.print_ok("Connection tunnel already set up")
    
    # Get the project
    projects = json.loads(post(opener, '/connectionclient/projects/')).get('projects')
    if not projects:
        print "No projects for your account. You must define a project " \
              "through the chart.io web interface"
        sys.exit(1)

    project = projects[0]
    if len(projects) > 1:
        project_name = get_choice("You have multiple projects. " 
                "Which project would you like to attatch this database to?", 
                [p['name'] for p in projects])
        
        for p in projects:
            if p['name'] == project_name:
                project = p
                break

    # Get the type of database
    response = json.loads(post(opener, '/connectionclient/databasetypes/'))
    databases = response.get('databasetypes', [])
    db_name = get_choice("What type of database are you hooking up?", 
            [dt['name'] for dt in databases], default='MySQL')
    db = databases[0]
    for d in databases:
        if d['name'] == db_name:
            db = d
            break
    
    connection = response.get('connection', {})

    # Run through datasource config class
    config_cls = {
        'MySQL': MysqlConfig,
        'PostgreSQL': PostgresConfig,
    }[db_name]

    settings = {}
    if config_cls:
        conf = config_cls()
        conf.run_steps()
        settings = conf.settings

    register_args = {
        'project_id': project['id'], 
        'type': db['id'],
        'connectionclient_id': get_conf('client_id'), 
    }
    register_args.update(settings)

    # Launching chartio connect
    TermColor.print_ok('Launching chartio_connect')
    subprocess.Popen(['chartio_connect.py', '-d'])
    time.sleep(5) # Let connection get established
    TermColor.print_ok('chartio_connect running')
    
    reg_response = post(opener, '/connectionclient/register/', register_args)

    if reg_response == 'success':
        TermColor.print_ok("Datasource registered. chartio_connect is running.")
        TermColor.print_ok("To ensure chartio reconnects after a reboot, add it to your crontab by typing:")
        print "crontab -e"
        TermColor.print_ok("and entering this as an entry:")
        print "@reboot /usr/local/bin/chartio_connect.py -d"
        TermColor.print_ok("And then go to https://chart.io/ to see you data.")
    else:
        TermColor.print_error("Erroring setting up your datasource. If this "
                            "continues, please contact support@chart.io")


if __name__ == "__main__":
    main()
