# setup the import machinery, necessary in dev environment
from cubes import narval, apycot

import apycotlib
from apycotlib import atest, writer

from narvalbot.prototype import EXPR_CONTEXT, action, input, output
from narvalbot.elements import FilePath


def _apycot_cleanup(plan):
    if hasattr(plan, 'apycot'):
        if plan.state != 'done':
            plan.apycot.global_status = apycotlib.ERROR
        plan.apycot.clean()
    # XXX clean_env

def _make_test_runner_action(runner):
    @output('coverage.data', 'isinstance(elmt, FilePath)', optional=True)
    @apycotlib.apycotaction(runner, 'INSTALLED in elmt.done_steps')
    def act_runtests(inputs, runner=runner):
        from apycotlib.checkers import python # trigger registration
        test = inputs['apycot']
        options = inputs.get('options')
        checker, status = test.run_checker(runner, options=options)
        if options.get('pycoverage') and hasattr(checker, 'coverage_data'):
            return {'coverage.data': FilePath(checker.coverage_data,
                                              type='coverage.data')}
        return {}
    return act_runtests


STEP_CHECKEDOUT, STEP_INSTALLED, STEP_COVERED, STEP_DEBIANPKG = range(4)

EXPR_CONTEXT['Test'] = atest.Test
EXPR_CONTEXT['CHECKEDOUT'] = STEP_CHECKEDOUT
EXPR_CONTEXT['INSTALLED']  = STEP_INSTALLED
EXPR_CONTEXT['COVERED']    = STEP_COVERED
EXPR_CONTEXT['DEBIANPKG']  = STEP_DEBIANPKG

# base actions #################################################################

@input('plan', 'isinstance(elmt, Plan)')
@output('apycot',)
@output('projectenv',)
@action('apycot.init', finalizer=_apycot_cleanup)
def act_apycot_init(inputs):
    plan = inputs['plan']
    w = writer.TestDataWriter(plan.memory.cnxh, plan.cwplan.eid)
    test = plan.apycot = atest.Test(plan.cwplan, w, plan.options)
    test.setup()
    test.done_steps = set()
    return {'apycot': test, 'projectenv': test.environment}


@input('apycot', 'isinstance(elmt, Test)')
@output('projectenvs', list=True)
@action('apycot.get_dependancies')
def act_get_dependancies(inputs):
    """Checkout repository for a test configuration"""
    tconfig = inputs['apycot'].tconfig
    environment = inputs['apycot'].environment
    return {'projectenvs': [environment] + tconfig.dependencies(environment)}


@input('apycot', 'isinstance(elmt, Test)')
@input('projectenv', 'getattr(elmt, "__regid__", None) == "ProjectEnvironment"')
@action('apycot.checkout')
def act_checkout(inputs):
    """Checkout repository for a test configuration"""
    test = inputs['apycot']
    test.checkout(inputs['projectenv'])
    test.done_steps.add(STEP_CHECKEDOUT)
    return {}


@input('projectenv', 'getattr(elmt, "__regid__", None) == "ProjectEnvironment"')
@input('apycot', 'isinstance(elmt, Test)', 'CHECKEDOUT in elmt.done_steps')
@action('apycot.install')
def act_install(inputs):
    from apycotlib import preprocessors
    test = inputs['apycot']
    test.call_preprocessor('install', inputs['projectenv'])
    if inputs['projectenv'] is test.environment: # XXX
        test.done_steps.add(STEP_INSTALLED)
    return {}


# checker actions ##############################################################

# @input('projectenv', 'getattr(elmt, "__regid__", None) == "ProjectEnvironment"')
# @output('changes-file', 'isinstance(elmt, FilePath)', 'elmt.type == "debian.changes"', list=True)
# @apycotlib.apycotaction('lgp.build', 'CHECKEDOUT in elmt.done_steps')
# def act_lgp_build(inputs):
#     test = inputs['apycot']
#     checker, status = test.run_checker('lgp.build', inputs.get('options'))
#     changes = []
#     for distrib, dchanges in checker.debian_changes.iteritems():
#         for change in dchanges:
#             changes.append(FilePath(dchange, type="debian.changes", distribution=distrib))
#     if status:
#         test.done_steps.add(STEP_DEBIANPKG)
#     return {'changes-file': changes}


act_pyunit = _make_test_runner_action('pyunit')
act_pytest = _make_test_runner_action('pytest')


@apycotlib.apycotaction('pylint', 'INSTALLED in elmt.done_steps')
def act_pylint(inputs):
    from apycotlib.checkers import python # trigger registration
    test = inputs['apycot']
    checker, status = test.run_checker('pylint', inputs.get('options'))
    return {}


@input('coverage.data', 'isinstance(elmt, FilePath)', 'elmt.type == "coverage.data"')
@apycotlib.apycotaction('pycoverage')
def act_pycoverage(inputs):
    from apycotlib.checkers import python # trigger registration
    test = inputs['apycot']
    options = inputs.get('options') # from apycotaction
    options['coverage.data'] = inputs['coverage.data'].path
    checker, status = test.run_checker('pycoverage', options=options)
    return {}


# @apycotlib.apycotaction('lgp.check')
# def act_lgp_check(inputs):
#     test = inputs['apycot']
#     checker, status = test.run_checker('lgp.check', inputs.get('options'))
#     return {}


# @apycotlib.apycotaction('piuparts', 'DEBIANPKG in elmt.done_steps')
# def act_piuparts(inputs):
#     test = inputs['apycot']
#     checker, status = test.run_checker('piuparts', inputs.get('options'))
#     return {}


# @apycotlib.apycotaction('lintian', 'DEBIANPKG in elmt.done_steps')
# def act_lintian(inputs):
#     test = inputs['apycot']
#     checker, status = test.run_checker('lintian', inputs.get('options'))
#     return {}
