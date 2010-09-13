"""this module contains server side hooks for notification about test status
changes

:organization: Logilab
:copyright: 2009-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

from datetime import datetime, timedelta

from cubicweb.selectors import is_instance
from cubicweb.uilib import text_cut
from cubicweb.server import hook
from cubicweb.hooks import notification as notifhooks
from cubicweb.sobjects import notification as notifviews

from cubes.vcsfile.entities import _MARKER

def start_period_tests(session, period):
    rset = session.execute(
        'Any TC,TCN,TCS,S WHERE '
        'TC computed_start_mode %(sm)s, TC in_state S, S name "activated", '
        'TC name TCN, TC start_rev_deps TCS', {'sm': period})
    for i in xrange(rset.rowcount):
        tc = rset.get_entity(i, 0)
        for env in tc.iter_environments():
            branch = tc.apycot_configuration(env).get('branch', _MARKER)
            if branch is _MARKER:
                # check every active branch if no branch specified
                heads = env.repository.heads_rset().entities()
            else:
                head = env.repository.branch_head(branch)
                if head is None:
                    # No head found for this branch, skip
                    continue
                heads = (head,)
            for head in heads:
                # only start test if the config hasn't been executed against
                # current branch head
                if session.execute(
                    'Any TE WHERE TE using_revision REV, REV eid %(rev)s, '
                    'TE using_config TC, TC eid %(tc)s',
                    {'rev': head.eid, 'tc': tc.eid}):
                    # This rev have already been tested
                    continue
                tc.start(env, head.branch)


def start_tests_if_match(session, revision, pe):
    rql = ('Any TC, PE, PEN, TCN, TCS WHERE TC use_environment PE, REV eid %(rev)s,'
           'PE name PEN, PE eid %(pe)s, PE vcs_path PEP, TC name TCN, '
           'TC start_rev_deps TCS, '
           'TC computed_start_mode %(sm)s, TC in_state S, S name "activated", '
           'VC from_revision REV, '
           'VC content_for VF, VF directory ~= PEP + "%"'
           )
    rset = session.execute(rql, {'sm': 'on new revision',
                                 'rev': revision.eid,
                                 'pe': pe.eid})
    if rset:
        branch = revision.branch
        for i, row in enumerate(rset):
            tc = rset.get_entity(i, 0)
            pe = rset.get_entity(i, 1)
            tc.start(pe, revision.branch)


class ComputeStartModeHook(hook.Hook):
    __regid__ = 'apycot.compute_start_mode'
    __select__ = hook.Hook.__select__ & is_instance('TestConfig')
    events = ('before_add_entity', 'before_update_entity')

    def __call__(self):
        if self.entity.get('start_mode') == u'inherited':
            ComputeStartModeOp(self._cw, tc=self.entity)

class ComputeStartModeOp(hook.Operation):
    def precommit_event(self):
        tc = self.tc
        if tc.start_mode == u'inherited':
            if tc.config_parent:
                tc.set_attributes(start_mode=tc.config_parent.start_mode)
            else:
                msg = self.session._('Inherited start mode can only be used if the '
                                     'configuration refines another one')
                raise ValidationError(tc.eid, {'start_mode': msg})


# automatic test launching #####################################################

class ServerStartupHook(hook.Hook):
    """add looping task to automatically start tests
    """
    __regid__ = 'apycot.startup'
    events = ('server_startup',)
    def __call__(self):
        if not self.repo.config['test-master']:
            return
        # XXX use named args and inner functions to avoid referencing globals
        # which may cause reloading pb
        def check_test_to_start(repo, datetime=datetime,
                                start_period_tests=start_period_tests):
            now = datetime.now()
            session = repo.internal_session()
            try:
                # XXX only start task for environment which have changed in the
                # given interval
                start_period_tests(session, 'hourly')
                if now.hour == 1:
                    start_period_tests(session, 'daily')
                if now.isoweekday() == 1:
                    start_period_tests(session, 'weekly')
                if now.day == 1:
                    start_period_tests(session, 'monthly')
                session.commit()
            finally:
                session.close()
        self.repo.looping_task(60*60, check_test_to_start, self.repo)


class StartTestAfterAddRevision(hook.Hook):
    __regid__ = 'apycot.start_test_on_new_rev'
    __select__ = hook.Hook.__select__ & is_instance('Revision')
    events = ('after_add_entity',)

    def __call__(self):
        vcsrepo = self.entity.repository
        for basepe in vcsrepo.reverse_local_repository:
            for pe in basepe.iter_refinements():
                if not pe.vcs_path:
                    for tc in pe.reverse_use_environment:
                        if tc.computed_start_mode == 'on new revision' \
                               and tc.match_branch(pe, self.entity.branch):
                            tc.start(pe, self.entity.branch)
                else:
                    start_tests_if_match(self._cw, revision=self.entity, pe=pe)
        # when a test is started, it may use some revision of dependency's
        # repositories that may not be already imported by vcsfile. So when it
        # try to create a link between the execution and the revision, it
        # fails. In such case the information is kept as a CheckResultInfo
        # object, use it to create the link later when the changeset is
        # imported.
        for cri in self._cw.execute(
            'Any CRI, X WHERE CRI for_check X, CRI type "revision", '
            'CRI label ~= %(repo)s, CRI value %(cs)s',
            {'cs': self.entity.changeset,
             # safety belt in case of duplicated short changeset. XXX useful?
             'repo': '%s:%s%%' % (vcsrepo.type, vcsrepo.source_url or vcsrepo.path)
             }).entities():
            cri.check_result.set_relations(using_revision=self.entity)
            cri.delete()


# notifications ################################################################

class ExecStatusChangeView(notifviews.NotificationView):
    __regid__ = 'exstchange'
    __select__ = is_instance('TestExecution')

    content = '''The following changes occured between executions on branch %(branch)s:

%(changelist)s

Imported changes occured between %(ex1time)s and %(ex2time)s:
%(vcschanges)s

URL: %(url)s
'''

    def subject(self):
        entity = self.cw_rset.get_entity(0, 0)
        changes = entity.status_changes()
        testconfig = '%s/%s' % (entity.environment.name,
                                entity.configuration.name)
        if entity.branch:
            testconfig = u'%s#%s' % (testconfig, entity.branch)
        if len(changes) == 1:
            name, (fromstate, tostate) = changes.items()[0]
            fromstate, tostate = fromstate.status, tostate.status
            subject = '%s: %s -> %s (%s)' % (
                testconfig, self._cw._(fromstate), self._cw._(tostate), name)
        else:
            count = {}
            for fromstate, tostate in entity.status_changes().values():
                fromstate, tostate = fromstate.status, tostate.status
                try:
                    count[tostate] += 1
                except KeyError:
                    count[tostate] = 1
            resume = ', '.join('%s %s' % (num, self._cw._(state))
                               for state, num in count.items())
            subject = self._cw._('%(testconfig)s now has %(resume)s') % {
                'testconfig': testconfig, 'resume': resume}
        return '[%s] %s' % (self._cw.vreg.config.appid, subject)

    def context(self):
        entity = self.cw_rset.get_entity(0, 0)
        prevexec = entity.previous_execution()
        ctx  = super(ExecStatusChangeView, self).context()
        ctx['ex1time'] = prevexec.printable_value('starttime')
        ctx['ex2time'] = entity.printable_value('starttime')
        ctx['branch'] = entity.branch
        chgs = []
        _ = self._cw._
        for name, (fromstate, tostate) in sorted(entity.status_changes().items()):
            name = _(name)
            fromstate, tostate = _(fromstate.status), _(tostate.status)
            chg = _('%(name)s status changed from %(fromstate)s to %(tostate)s')
            chgs.append('* ' + (chg % locals()))
        ctx['changelist'] = '\n'.join(chgs)
        vcschanges = []
        tconfig = entity.configuration
        environment = entity.environment
        for env in [environment] + tconfig.dependencies(environment):
            if env.repository:
                vcsrepo = env.repository
                vcsrepochanges = []
                lrev1 = prevexec.repository_revision(env.repository)
                lrev2 = entity.repository_revision(env.repository)
                if lrev1 and lrev2:
                    for rev in self._cw.execute(
                        'Any REV, REVA, REVD, REVR, REVC ORDERBY REV '
                        'WHERE REV from_repository R, R eid %(r)s, REV branch %(branch)s, '
                        'REV revision > %(lrev1)s, REV revision <= %(lrev2)s, '
                        'REV author REVA, REV description REVD, '
                        'REV revision REVR, REV changeset REVC',
                        {'r': env.repository.eid,
                         'branch': lrev2.branch or env.repository.default_branch(),
                         'lrev1': lrev1.revision, 'lrev2': lrev2.revision}).entities():
                        msg = text_cut(rev.description)
                        vcsrepochanges.append('  - %s by %s:%s' % (
                            rev.dc_title(), rev.author, msg))
                    if vcsrepochanges:
                        vcschanges.append('* in repository %s: \n%s' % (
                            env.repository.path, '\n'.join(vcsrepochanges)))
        if vcschanges:
            ctx['vcschanges'] = '\n'.join(vcschanges)
        else:
            ctx['vcschanges'] = self._cw._('* no change found in known repositories')
        return ctx


class TestExecutionUpdatedHook(hook.Hook):
    __regid__ = 'apycot.te.status_change'
    __select__ = hook.Hook.__select__ & is_instance('TestExecution')
    events = ('before_update_entity',)

    def __call__(self):
        # end of test execution : set endtime
        entity = self.entity
        if 'endtime' in entity.edited_attributes and entity.status_changes():
            view = self._cw.vreg['views'].select(
                'exstchange', self._cw, rset=entity.cw_rset, row=entity.cw_row,
                col=entity.cw_col)
            notifhooks.RenderAndSendNotificationView(self._cw, view=view)
        if 'execution_status' in entity.edited_attributes and \
               entity.status == 'waiting execution':
            entity['status'] = entity.execution_status


try:
    from cubes.nosylist import hooks as nosylist
except ImportError:
    pass
else:
    # XXX that does not mean the nosylist cube is used by the instance, but it
    # shouldn't matter anyway
    nosylist.S_RELS |= set(('has_apycot_environment',))
    nosylist.O_RELS |= set(('use_environment', 'using_config'))
