"""
Pentaho BI Server installation script for Ubuntu.

Currently tested for:
    Pentaho BI Server Community Edition v3.8
    Ubuntu 10.04

"""

# FIXME: URLGrabber does not work with HTTPS certificates
#   not validated by CAs
import urlgrabber
import urlgrabber.progress

from time import sleep
from os.path import exists, join, abspath, dirname

from fabric.api import task
from fabric.colors import red
from fabric.utils import warn, abort
from fabric.operations import put, run, sudo
from fabric.context_managers import cd, settings, hide
from fabric.contrib.files import exists as exists_remotely, \
                                 uncomment, sed, upload_template, contains


__version__ = 0.1


BISERVER_TAR_URL = ('http://cdnetworks-us-2.dl.sourceforge.net/project/'
                    'pentaho/Business%20Intelligence%20Server/3.8.0-stable/'
                    'biserver-ce-3.8.0-stable.tar.gz')

BISERVER_LOCAL_PATH = '/var/tmp/biserver-ce-3.8.0-stable.tar.gz'

BISERVER_INSTALL_PATH = '/srv/pentaho/' # BE CAREFUL: This directoty will 
                                        #   be wiped clean before the 
                                        #   installation starts.

POSTGRES_JDBC_URL = ('http://jdbc.postgresql.org/download/'
                     'postgresql-9.0-801.jdbc4.jar')

POSTGRES_JDBC_LOCAL_PATH = '/var/tmp/postgresql-9.0-801.jdbc4.jar'


def download_biserver():
    """Downloads the Pentaho biserver tarball localy on     
    BISERVER_INSTALL_PATH. Skip in case a file with the same name
    already exists.
    
    """

    if not exists(BISERVER_LOCAL_PATH):
        progress_bar = urlgrabber.progress.text_progress_meter()
        urlgrabber.urlgrab(BISERVER_TAR_URL, 
                           BISERVER_LOCAL_PATH, 
                           progress_obj=progress_bar)


def download_jdbc():
    """Downloads the java JDBC drivers localy on 
    POSTGRES_JDBC_LOCAL_PATH. Skip in case a file with the same name
    already exists.
    
    """

    if not exists(POSTGRES_JDBC_LOCAL_PATH):
        progress_bar = urlgrabber.progress.text_progress_meter()
        urlgrabber.urlgrab(POSTGRES_JDBC_URL, 
                           POSTGRES_JDBC_LOCAL_PATH, 
                           progress_obj=progress_bar)
        

def upload_biserver():
    """Upload the local tarball from BISERVER_LOCAL_PATH to the same
    path on the remote host. Skip in case a file with the same name
    exists in the remote server.
    
    """

    download_biserver()
    if not exists_remotely(BISERVER_LOCAL_PATH):
        put(BISERVER_LOCAL_PATH, BISERVER_LOCAL_PATH)


def uncompress_biserver():
    """Uncompress the tarball located on /var/tmp/ into tne 
    BISERVER_INSTALL_PATH.
    
    """
    
    sudo('rm -r ' + BISERVER_INSTALL_PATH)
    sudo('mkdir -p ' + BISERVER_INSTALL_PATH)
    with cd(BISERVER_INSTALL_PATH):
        sudo('tar xzf ' + BISERVER_LOCAL_PATH)
        sudo('rm biserver-ce/promptuser.sh')


def deb_package_is_installed(pkg_name):
    """Check if the debian package is installed."""

    # FIXME: output based algorithms won't work with localized 
    #   software
    output = run("dpkg-query -W -f='${Status}' " + pkg_name)

    if output == 'install ok installed':
        return True
    
    return False


def install_java():
    """Install java6 and make it the default."""

    # If java packages are already installed just skip
    if deb_package_is_installed('sun-java6-jdk') and \
        deb_package_is_installed('sun-java6-jdk'): 
        return

    # Enable partners repository
    uncomment(
        '/etc/apt/sources.list', 
        'deb http:.*?lucid partner', 
        use_sudo=True
    )
    sudo('apt-get update')
    
    # Accept java SUN license
    accept_license = ('echo "sun-java6-jre shared/accepted-sun-dlj-v1-1 '
                     'boolean true" | sudo debconf-set-selections')
    sudo(accept_license)

    # Install java6
    sudo('apt-get install sun-java6-jdk sun-java6-jre')
    
    # Set this implementation of java as the default
    sudo('update-alternatives --set java /usr/lib/jvm/java-6-sun/jre/bin/java')


def replace_hsqldb_to_psql(file_path):
    """Replace hsqldb configuration by PostgreSQL into the given 
    configuration file_path.

    """

    replace_list = [
        # JDBC drivers
        ('org.hsqldb.jdbcDriver', 'org.postgresql.Driver'),
        
        # JDBC connection URI
        ('jdbc:hsqldb:hsql://localhost[^/]*/', 
         'jdbc:postgresql://localhost:5432/'),
    
        # hibernate dialect
        ('org.hibernate.dialect.HSQLDialect',
         'org.hibernate.dialect.PostgreSQLDialect'),
        
        # hibernate config file
        ('hsql.hibernate.cfg.xml', 'postgresql.hibernate.cfg.xml'),
        
        # Validation query
        ('"select[^"]*"',
         '"select 1"'),
        
        # quartz properties
        ('org.quartz.impl.jdbcjobstore.StdJDBCDelegate',
         'org.quartz.impl.jdbcjobstore.PostgreSQLDelegate'),
    ]
        
    for hsqldb_str, psql_str in replace_list:
        sed(file_path, hsqldb_str, psql_str, use_sudo=True)
          

def switch_from_hsqldb_to_psql(): 
    """Fix all configuration file needed to work with PostgreSQL
    instead of hsqldb.
    
    """   
 
    files_to_fix = [
        ('biserver-ce/pentaho-solutions/system/'
         'applicationContext-spring-security-jdbc.xml'),

        ('biserver-ce/pentaho-solutions/system/'
         'applicationContext-spring-security-hibernate.properties'),
        
        ('biserver-ce/pentaho-solutions/system/'
         'hibernate/hibernate-settings.xml'),

        'biserver-ce/pentaho-solutions/system/quartz/quartz.properties',
        'biserver-ce/tomcat/webapps/pentaho/META-INF/context.xml',
    ] 

    for file_ in files_to_fix:
        file_path = join(BISERVER_INSTALL_PATH, file_)
        replace_hsqldb_to_psql(file_path)

    web_cfg = join(BISERVER_INSTALL_PATH, 
                   'biserver-ce/tomcat/webapps/pentaho/WEB-INF/web.xml')
   
    # Commenting out HSQLDB auto startup 
    sed(web_cfg, '^.*BEGIN HSQLDB.*$', '<!--', use_sudo=True)
    sed(web_cfg, '^.*END HSQLDB.*$', '-->', use_sudo=True)


def configure_postgresql():
    """Install PosgreSQL and configure Pentaho BI Server to
    use it instead of the default Hypersonic DB.
    
    """

    # Install postgresql
    if not deb_package_is_installed('postgresql-8.4'):
        sudo('apt-get install postgresql-8.4')
    
    # Download jdbc drivers
    download_jdbc()
    
    # Place the drives on the biserver and administration-console
    biserver_lib = join(BISERVER_INSTALL_PATH, 'biserver-ce/tomcat/lib/')
    put(POSTGRES_JDBC_LOCAL_PATH, biserver_lib, use_sudo=True)
    console_lib = join(BISERVER_INSTALL_PATH, 'administration-console/jdbc/')
    put(POSTGRES_JDBC_LOCAL_PATH, console_lib, use_sudo=True)
   
    # Get path of initial data SQL scripts
    create_repo_script_path = join(BISERVER_INSTALL_PATH, 
        'biserver-ce/data/postgresql/create_repository_postgresql.sql')
    create_quartz_script_path = join(BISERVER_INSTALL_PATH, 
        'biserver-ce/data/postgresql/create_quartz_postgresql.sql')
    
    # Configure postgres to accept local connections into the
    #   two Pentaho databases 
    config_pg_hba = (
        '# Required by Pentaho BI-Server',
        'local   hibernate   hibuser                           trust',
        'local   quartz      pentaho_user                      trust',
        '',
        '# DO NOT DISABLE!',
    )

    pg_hba_path = '/etc/postgresql/8.4/main/pg_hba.conf'

    # Add the configuration lines into pg_hba.conf
    #   before adding we check if the first line isn't already 
    #   in the file to avoid duplicates
    if not contains(pg_hba_path, config_pg_hba[0], use_sudo=True):  
        sed( 
            pg_hba_path,
            '# DO NOT DISABLE!',
            '\\n'.join(config_pg_hba),
            use_sudo=True,
            flags='m'
        )
        sudo('/etc/init.d/postgresql-8.4 reload')

    # Execute the scripts
    sudo('psql -f ' + create_repo_script_path, user='postgres')
    sudo('psql -f ' + create_quartz_script_path, user='postgres')
  
    switch_from_hsqldb_to_psql() 


def configure_auto_startup():
    """Configure Pentaho BI Server to auto start on boot time."""

    # Replace start by run on tomcat startup script.
    #   This will make sure that the process won't be fork it self
    #   leaving this control to upstart as it requires.
    tomcat_startup_script = join(BISERVER_INSTALL_PATH, 
                                 'biserver-ce/tomcat/bin/startup.sh')
    sed(
        tomcat_startup_script,
        ' start ',
        ' run ',
        use_sudo=True
    )
 
    # Place the init script path into the upstart script and 
    #   install it on /etc/init
    init_script_path = join(BISERVER_INSTALL_PATH, 
                            'biserver-ce/start-pentaho.sh')
    script_template_path = join(abspath(dirname(__file__)), 
                                'upstart-jobs/pentaho-biserver.conf')
    upload_template(
        script_template_path,
        '/etc/init/',
        {'init_script': init_script_path},
        use_sudo=True
    )


def biserver_running():
    """Returns True if there is an instance of pentaho BI-Server 
    already in execution
    
    """
    # FIXME: output based algorithms won't work with localized 
    #   software
    output = run('status pentaho-biserver')
    
    if 'running' in output:
        return True
    return False


def user_data_loaded():
    """Returns True if the users table already exists on the hibernate
    database.
    
    """
    
    with settings(hide('running', 'stdout', 'stderr', 'warnings'), 
                  warn_only=True):
        output = sudo('psql hibernate -c "\d users"', user='postgres')
    
    if output.return_code == 0:
        return True

    return False
   

def disable_sample_users():
    """Disable all sample users which comes with biserver default
    installation.
    
    """
    # Disable sample user combobox on the login modal window
    config_path = join(BISERVER_INSTALL_PATH, 
                       'biserver-ce/pentaho-solutions/system/pentaho.xml')
    sed(
        config_path,
        '<login-show-users-list>[^>]*</login-show-users-list>',
        '<login-show-users-list>false</login-show-users-list>',
        use_sudo=True
    )

    timeout = 60 # Max time to wait for sample data
    time_count = 0

    # Wait until the users table is created
    while not user_data_loaded():
        sleep(1)
        time_count += 1
    
        # Make sure we don't wait for too long
        if time_count >= timeout:
            warn(('Timeout waiting for sample data. '
                  'Could not disable sample users.'))
            return

    # After the table creation it takes few moments until it's 
    #   populated with the sample data. 
    #   FIXME: 5 might be too long or too short. We should use a query 
    #   instead of a sleep
    sleep(5)

    # Disable all sample users except by the admin
    update_query = """UPDATE 
                        users 
                      SET 
                        enabled = False 
                      WHERE 
                        username != 'admin'"""

    sudo('psql hibernate -c "' + update_query + '"', user='postgres')

@task
def set_admin_password(password):
    """Set admin user password"""

    update_query = """UPDATE
                           users
                       SET
                           password = encode('%s', 'base64')
                       WHERE
                           username = 'admin';""" % password

    sudo('psql hibernate -c "' + update_query + '"', user='postgres')


@task
def set_publish_password(publish_password='password'):
    """Set report publishing password

    Setting this we are allowed to publish reports directly from the 
    Pentaho Report Designer desktop application.
    
    """
    
    publish_cfg = join(BISERVER_INSTALL_PATH,
                  'biserver-ce/pentaho-solutions/system/publisher_config.xml')
    sed(
        publish_cfg,
        '<publisher-password>[^<]*</publisher-password>',
        '<publisher-password>' + publish_password + '</publisher-password>',
        use_sudo=True
    )


@task(default=True)
def install_biserver():
    """Download, install and configure BI Server"""

    if biserver_running():
        abort(red(('It looks like there is a Pentaho BI-Server in execution. '
              "Please stop it with the command 'sudo stop pentaho-biserver' "
              'before running this installation script.')))

    install_java()
    upload_biserver()
    uncompress_biserver() 
    configure_postgresql()
    configure_auto_startup()
    set_publish_password()
    
    sudo('start pentaho-biserver')
    disable_sample_users()
    sudo('stop pentaho-biserver')
