# Copyright (c) 2010 by Yaco Sistemas <lgs@yaco.es>
#
# This file is part of hghooks.
#
# hghooks is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# hghooks is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with hghooks.  If not, see <http://www.gnu.org/licenses/>.

import re

from hghooks import CheckerManager, re_options

from trac.env import open_environment

ticket_catcher = re.compile(
    '(?:close|closed|closes|fix|fixed|fixes|addresses|references|refs|re|see)'
    '.?(#[0-9]+(?:(?:[, &]+| *and *)#[0-9]+)*)',
    re_options)


class TicketChecker(object):

    error_msg = 'At least one open ticket must be mentioned in the log message'

    def __init__(self, trac_env, ui):
        self.trac_env = trac_env
        self.ui = ui

    def __call__(self, files_to_check, msg):
        # copied from
        # http://trac.edgewall.org/browser/trunk/contrib/trac-pre-commit-hook
        warnings = 0

        tickets = []
        for tmp in ticket_catcher.findall(msg):
            tickets += re.findall('#([0-9]+)', tmp)

        if tickets == []:
            self.ui.warn(self.error_msg)
            warnings += 1
        else:
            env = open_environment(self.trac_env)
            db = env.get_db_cnx()

            cursor = db.cursor()
            cursor.execute("SELECT COUNT(id) FROM ticket WHERE "
                           "status <> 'closed' AND id IN (%s)" %
                           ','.join(tickets))
            row = cursor.fetchone()
            if not row or row[0] < 1:
                self.ui.warn(self.error_msg)
                warnings += 1

        return warnings


def tickethook(ui, repo, hooktype, node, pending, **kwargs):
    checker_manager = CheckerManager(ui, repo, node)
    trac_env = ui.config('trac', 'environment')
    if trac_env is None:
        ui.warn('You must set the environment option in the [trac] section'
                ' of the repo configuration to use this hook')
        return True  # failure

    return checker_manager.check(TicketChecker(trac_env, ui))
