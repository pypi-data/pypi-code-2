from datetime import datetime
from optparse import OptionParser
import os
import sys
import zc.recipe.egg

from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import append
from fabric.state import connections

class Deploy:
    """
    Buildout recipe making versioned remote deploys trivial.
    """
    def __init__(self, buildout, name, options):
        self.script_args = {}
       
        # Collect script args.
        self.script_args['as_user'] = options.get('as_user', 'www-data')
        self.script_args['python_exec'] = options.get('python_exec', 'python')
        self.script_args['root_path'] = options['root_path']
        self.script_args['git_url'] = options['git_url']
        self.script_args['git_branch'] = options.get('git_branch', None)
        self.script_args['conf_file'] = options.get('conf_file', 'buildout.cfg')
        self.script_args['deploy_key_path'] = options.get('deploy_key_path', None)
        self.script_args['host'] = options['host']
        self.script_args['update_supervisor'] = options.get('update_supervisor', False)

        self.script_args['shared_resources'] = []
        for shared_resource in options.get('shared_resources', '').split('\n'):
            if shared_resource:
                self.script_args['shared_resources'].append(shared_resource)
        
        self.script_args['initd_commands'] = []
        for initd_command in options.get('initd_commands', '').split('\n'):
            if initd_command:
                self.script_args['initd_commands'].append(initd_command)
        
        self.script_args['cron_commands'] = []
        for cron_command in options.get('cron_commands', '').split('\n'):
            if cron_command:
                self.script_args['cron_commands'].append(cron_command)

        # General buildout setup.
        self.name = name
        self.buildout = buildout
        self.options = options
        self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)

    def create_manage_script(self, ws):
        args = []
        for k,v in self.script_args.items():
            if v.__class__ == str:
                args.append('%s="%s"' % (k, v))
            else:
                args.append('%s=%s' % (k, v))

        return zc.buildout.easy_install.scripts(
            [(self.name, 'praekelt.recipe.deploy', 'script')],
            ws, 
            sys.executable, 
            self.options['bin-directory'],
            arguments=', '.join(args),
        )
   
    def install(self):
        requirements, ws = self.egg.working_set()
        self.create_manage_script(ws)
        script_paths = []

        # Create script.
        script_paths.extend(self.create_manage_script(ws))

        return script_paths

    def update(self):
        return

def get_current_release_path(path, as_user):
    with cd(path):
        with settings(warn_only=True):
            result = sudo('ls -l current', user=as_user)
            if result.failed:
                return None
            else:
                return os.path.join(path, result.split('-> ')[-1])

def clone_buildout(release_path, timestamp, deploy_key_path, git_url, git_branch, as_user):
    """
    Clone buildout switch to branch and return HEAD rev hash.
    """
    with cd(release_path):
        if deploy_key_path:
            sudo("ssh-agent sh -c 'ssh-add %s && git clone %s %s'" % (deploy_key_path, git_url, timestamp), user=as_user)
        else:
            sudo("git clone %s %s" % (git_url, timestamp), user=as_user)
        with cd(timestamp):
            # Switch to a branch if needed.
            if git_branch:
                sudo('git checkout -b %s origin/%s' % (git_branch, git_branch), user=as_user)
            return sudo('git rev-parse HEAD', user=as_user)

def copy_shared_resources(current_release_path, new_release_path, shared_resources, as_user):
    if current_release_path and shared_resources:
        for shared_resource in shared_resources:
            path = os.path.join(current_release_path, shared_resource)
            with cd(new_release_path):
                dir_path = os.path.split(shared_resource)[0]
                if dir_path != '':
                    sudo('mkdir -p %s' % dir_path, user=as_user)
                with settings(warn_only=True):
                    if dir_path != '':
                        sudo('cp -r %s %s' % (path, dir_path), user=as_user)
                    else:
                        sudo('cp -r %s .' % path, user=as_user)

def run_buildout(new_release_path, conf_file, python_exec, as_user):
    with cd(new_release_path):
        sudo('%s bootstrap.py -c %s' % (python_exec, conf_file), user=as_user)
        sudo('./bin/buildout -v -c %s' % conf_file, user=as_user)

def disconnect():
    for key in connections.keys():
        connections[key].close()
        del connections[key]

def script(host, root_path, git_url, as_user='www-data', python_exec='python', git_branch=None, conf_file='buildout.cfg', deploy_key_path=None, shared_resources=[], initd_commands=[], update_supervisor=False, cron_commands=[]):
    """
    Args:
    host: Hostname on which to perform deploy. Required.
    root_path: Root path in which to perform the deploy. current/release path structure will be created within this path. Required.
    git_url: Git repo with which to perform the deploy. Required.
    as_user: User as which to perform the deploy. Used to setup permissions appropriately and to clone from github. Defaults to 'www-data'.
    python_exec: Python command with which to boostrap Buildout. Defaults to 'python'.
    git_branch: Git repo branch with which to perform the deploy. Not required.
    conf_file: Buildout cfg file with which to run boostrap and buildout. Defaults to 'buildout.cfg'.
    deploy_key_path: Path on host to key to use when cloning the repo. Not required.
    shared_resources: Resource paths to copy accross from the current release to the new release on each deploy. Not required.
    initd_commands: init.d commands to run after a completed deploy. i.e. nginx restart.
    update_supervisor: Whether or not to update supervisor. Defaults to False.
    cron_commands: Commands to add to the as_users user's crontab.

    The script creates a new deploy as follows:
        * A new release path structure is created using this pattern: <root_path>/releases/<release_timestamp>.
        * The git repo as specified in git_url is cloned.
        * The newly cloned repo's branch is switched to the branch as specified in git_branch. If git_branch is not specified no switch occurs. 
        * Shared resources as specified in shared_resources are copied from the current release(if present) to the new created release.
        * The Buildout's boostrap.py is run using the python executable as specified in python_exec and a Buildout configuration file as specified in conf_file. 'python' is used by default if python_exec is not specified, 'buildout.cfg' is used by default if conf_file is not specified.
        * The Buildout is run using a Buildout configuration file as specified in conf_file. 'buildout.cfg' is used by default if conf_file is not specified.
        * The <root_path>/current symlink is updated to point to newly created release.
        * Supervisor is updated(supervisorctl update) if update_supervisor is specified as True.
        * Each command specified in initd_commands is run in order.
    """
    release_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    parser = OptionParser()
    parser.add_option("-H", "--host", dest="host", default=None,
                  help="Hostname on which to perform deploy", metavar="<[user@]hostname>")
    parser.add_option("-s", "--ssh-user", dest="ssh_user", default=None,
                  help="SSH username to use during deploy", metavar="<user>")
    parser.add_option("-i", "--ignore-deploy-key", action="store_true", dest="ignore_deploy_key", default=False,
                  help="Don't use deploy key specified in buildout configuration's 'deploy_key_path' parameter.")

    options, parsed_args = parser.parse_args()
    if options.host:
        host = options.host

    if options.ssh_user:
        if '@' not in host:
            host = "%s@%s" % (options.ssh_user, host)

    if options.ignore_deploy_key:
        deploy_key_path = None 

    # Build paths.
    release_path = os.path.join(root_path, 'releases')
    with settings(host_string=host):
        current_release_path = get_current_release_path(root_path, as_user)
        new_release_path = os.path.join(release_path, release_timestamp)
    
        # Ask for deploy confirmation and kickoff process or abort.
        if confirm("This will buildout %s's %s branch in %s's %s path using %s and run the following commands:\n%s\nContinue?" % (
                git_url,
                git_branch if git_branch else 'default',
                env.host_string,
                new_release_path,
                conf_file,
                '\n'.join((['supervisorctl update',] if update_supervisor else []) + ['/etc/init.d/%s' % initd_command for initd_command in initd_commands]),
            )):

            # Confirm continue when no previous release is found.
            if not current_release_path and shared_resources:        
                if not confirm('It looks like there is no current release. This means no shared resources can be copied to this new release. Continue anyway?'):
                    abort("No current release found. Aborting at user request.")

            # Create release path. 
            sudo('mkdir -p %s' % release_path, user=as_user)

            # Clone buildout.
            rev = clone_buildout(release_path=release_path, timestamp=release_timestamp, deploy_key_path=deploy_key_path, git_url=git_url, git_branch=git_branch, as_user=as_user)

            # Copy shared resources.
            copy_shared_resources(current_release_path=current_release_path, new_release_path=new_release_path, shared_resources=shared_resources, as_user=as_user)

            # Run buildout.
            run_buildout(new_release_path=new_release_path, conf_file=conf_file, python_exec=python_exec, as_user=as_user)
    
            # Set current to new release.
            with cd(root_path):
                with settings(warn_only=True):
                    sudo('rm current')
                sudo('ln -s %s current' % new_release_path)

            # Set cron commands.
            if cron_commands:
                sudo('crontab -u %s -l > /tmp/%s_crontab' % (as_user, as_user))
                # Append misses some commands, do our own retarded check.
                result = sudo('cat /tmp/%s_crontab' % as_user)
                for cron_command in cron_commands:
                    if cron_command not in result:
                        append(cron_command, '/tmp/%s_crontab' % as_user, use_sudo=True)
                sudo('crontab -u %s /tmp/%s_crontab' % (as_user, as_user))
                sudo('rm /tmp/%s_crontab' % as_user)
        
            # Update Supervisor.
            if update_supervisor:
                sudo('supervisorctl update')
    
            # Run init.d commands.
            for initd_command in initd_commands:
                with settings(warn_only=True):
                    sudo('/etc/init.d/%s' % initd_command)

            disconnect()
