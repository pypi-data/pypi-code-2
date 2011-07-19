#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Roles in this namespace are meant to provide Apache web server utility methods for centos distributions.
'''

from provy.core import Role
from provy.more.centos.package.yum import YumRole


class NginxRole(Role):
    '''
    This role provides Apache web server management utilities for centos distributions.
    <em>Sample usage</em>
    <pre class="sh_python">
    from provy.core import Role
    from provy.more.centos import ApacheRole

    class MySampleRole(Role):
        def provision(self):
            with self.using(ApacheRole) as role:
                role.ensure_conf(path='/path/to/conf', conf_template='apache.conf')
                role.ensure_conf(path='/path/to/conf', conf_template='site.conf')
                role.ensure_conf(path='/path/to/conf', conf_template='virtual-host.conf')
    </pre>
    '''

    def provision(self):
        '''
        Installs Apache dependencies. This method should be called upon if overriden in base classes, or Apache won't work properly in the remote server.
        If you want to install a specific package of Apache, include a context variable called apache-package.
        <em>Sample usage</em>
        <pre class="sh_python">
        from provy.core import Role
        from provy.more.centos import ApacheRole

        class MySampleRole(Role):
            def provision(self):
                self.context['apache-package'] = 'my-custom-apache'
                self.provision_role(ApacheRole) # does not need to be called if using with block.
        </pre>
        '''
        package = 'apache-package' in self.context and self.context['apache-package'] or 'apache'
        with self.using(YumRole) as role:
            role.ensure_up_to_date()
            role.ensure_package_installed(package)

    def cleanup(self):
        '''
        Restarts apache if any changes have been made.
        There's no need to call this method manually.
        '''
        if 'must-restart-apache' in self.context and self.context['must-restart-apache']:
            self.restart()

    def ensure_conf(self, path, conf_template, options={}, owner=None):
        '''
        Ensures that the given configuration file is up-to-date with the specified template.
        <em>Parameters</em>
        path - Remote path of the given conf file.
        conf_template - Name of the template for nginx.conf.
        options - Dictionary of options passed to template. Extends context.
        owner - User that owns this file. Defaults to the last created user.
        <em>Sample usage</em>
        <pre class="sh_python">
        from provy.core import Role
        from provy.more.centos import ApacheRole

        class MySampleRole(Role):
            def provision(self):
                with self.using(ApacheRole) as role:
                    role.ensure_conf('/path/to/site.conf', conf_template='site.conf')
        </pre>
        '''

        if not owner:
            owner = self.context['owner']

        result = self.update_file(conf_template,
                                  path,
                                  options=options,
                                  sudo=True,
                                  owner=owner)
        if result:
            self.log('%s conf updated!' % path)
            self.ensure_restart()

    def ensure_restart(self):
        '''
        Ensures that apache gets restarted on cleanup. There's no need to call this method as any changes to apache config files will trigger it.
        <em>Sample usage</em>
        <pre class="sh_python">
        from provy.core import Role
        from provy.more.debian import ApacheRole

        class MySampleRole(Role):
            def provision(self):
                with self.using(ApacheRole) as role:
                    role.ensure_restart()
        </pre>
        '''
        self.context['must-restart-apache'] = True

    def restart(self):
        '''
        Forcefully restarts apache.
        <em>Sample usage</em>
        <pre class="sh_python">
        from provy.core import Role
        from provy.more.centos import ApacheRole

        class MySampleRole(Role):
            def provision(self):
                with self.using(ApacheRole) as role:
                    role.restart()
        </pre>
        '''
        command = '/etc/init.d/apache restart'
        self.execute(command, sudo=True)

