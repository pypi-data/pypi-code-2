from fabric.api import *

from fab_deploy.deploy import *
from fab_deploy.commands import touch, mysqldump, pip_install, pip_update, restart_apache
from fab_deploy.django_commands import migrate, manage, syncdb, compress, test, coverage
from fab_deploy.utils import run_as, update_env


