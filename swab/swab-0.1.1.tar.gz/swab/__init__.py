"""
Simple WSGI A/B testing.

(c) 2010 Oliver Cope.

See ``README.txt`` for usage instructions etc.
"""

import os
from math import sqrt, exp
from random import Random
from struct import unpack_from
from time import time
from datetime import datetime
from collections import defaultdict
from hashlib import md5
from functools import partial
from pesto import to_wsgi
from pesto.response import Response
from pesto.request import Request
from pesto.cookie import Cookie
from pesto.wsgiutils import static_server, mount_app
from pestotools.genshi import genshi, render_docstring

from genshi.template.loader import TemplateLoader
templateloader = TemplateLoader(os.path.join(os.path.dirname(__file__), 'templates'))

class Swab(object):
    """
    Simple WSGI A/B testing
    """
    def __init__(self, datadir, debug=False):
        """
        Create a new Swab test object

        datadir
            Path to directory for data storage
        debug
            If ``True``, show_variant can be forced to display to return a set
            result by addition of a querystring parameter of the form
            ``?swab.<experiment-name>=<variant>`` to the URL.
        """
        self.datadir = datadir
        self.experiments = {}
        self.experiments_by_goal = {}
        self.debug = debug
        makedir(self.datadir)

        # Function evaluted to determine whether to include a user in experiments.
        # Users not included will always see the default variant (ie the first listed)
        self.include_test = lambda experiment, environ: True
        self.exclude_test = lambda experiment, environ: False

    def include(self, experiment, environ):
        return self.include_test(experiment, environ) and not self.exclude_test(experiment, environ)

    def middleware(self, app, mountpoint='/swab', cookie_domain=None):
        """
        Middleware that sets a random identity cookie for tracking users.

        The identity can be overwritten by setting ``environ['swab.id']``
        before start_response is called. On egress this middleware will then
        reset the cookie if required.

            app
                The WSGI application to wrap

            mountpoint
                The path swab-specific views and resources will be served from.
                Make sure that this does not conflict with paths used by your
                application.

            cookie_domain
                The domain to use when setting cookies. If ``None`` this will not be
                set and the browser will default to the domain used for the request.
        """

        swabapp = mount_app({
            '/results': self.results_app,
            '/static': static_server(os.path.join(os.path.dirname(__file__), 'static')),
        })

        def middleware(environ, start_response):

            if environ['PATH_INFO'][:len(mountpoint)] == mountpoint:
                environ['SCRIPT_NAME'] += mountpoint
                environ['PATH_INFO'] = environ['PATH_INFO'][len(mountpoint):]
                return swabapp(environ, start_response)

            environ['swab.swab'] = self
            initswabid = getswabid(environ)

            def my_start_response(status, headers, exc_info=None):
                swabid = getswabid(environ)
                if swabid == initswabid and swabid is not None:
                    return start_response(status, headers, exc_info)

                if swabid is None:
                    swabid = generate_id()
                    environ['swab.id'] = swabid

                cookie_path = environ.get('SCRIPT_NAME') or '/'
                cookie = Cookie(
                    'swab', swabid, path=cookie_path,
                    domain=cookie_domain, http_only=True
                )
                return start_response(
                    status,
                    list(headers) + [("Set-Cookie", str(cookie))],
                    exc_info
                )

            return app(environ, my_start_response)

        return middleware

    def addexperiment(self, name, variants=None, goal=None):
        exp = self.experiments[name] = Experiment(name)
        if variants:
            exp.add(*variants)

        goal = goal if goal is not None else name
        self.experiments_by_goal.setdefault(goal, []).append(exp)

        makedir(os.path.join(self.datadir, name))
        return self.experiments[name]

    @to_wsgi
    @genshi()
    @render_docstring()
    def results_app(self, request):
        """
        <html xmlns:py="http://genshi.edgewall.org/">
            <head>
                <link rel="stylesheet" href="static/swab.css"/>
            </head>
            <body class="pageFullWidth">
            <h1>A/B test results summary</h1>
            <section py:for="exp in experiments">
                <h2>Experiment: $exp.name</h2>
                <?python
                expdata = data[exp.name]
                goals = data[exp.name]['goals']
                control = data[exp.name]['control']
                control_data = data[exp.name]['variants'][control]
                ?>
                <h3>Summary</h3>
                <div py:for="variant, vdata in sorted(data[exp.name]['variants'].items())">
                    <py:if test="variant != data[exp.name]['control']">
                        <py:for each="goal in goals">
                            <py:choose>
                                <py:when test="control_data['r'][goal] == 0">
                                    Insufficient data
                                </py:when>
                                <py:otherwise>
                                    <?python
                                    difference = vdata['r'][goal] / control_data['r'][goal]
                                    ?>
                                    <p>
                                        For the <strong>$goal</strong> goal, the <strong>$variant</strong> variant resulted in
                                        <py:choose>
                                            <span py:when="difference &gt;= 1" class="better">${'{0:.2%}'.format(difference - 1)} more conversions than the $control variant</span>
                                            <span py:otherwise="" class="worse">${'{0:.2%}'.format(difference - 1)} fewer conversions than the $control variant</span>
                                        </py:choose>
                                    </p>

                                    <ul class="simpleList">
                                        <py:choose>
                                            <div class="confident99" py:when="vdata['confidence'][goal] &gt;= 0.99">
                                                <li>
                                                    You have now collected enough data to be 99% certain that this conclusion is valid.
                                                </li>
                                                <li class="recommendation">
                                                    <py:choose>
                                                        Recommendation:
                                                        <span py:when="difference &gt;= 1">adopt $variant variant.</span>
                                                        <span py:otherwise="">adopt $control variant.</span>
                                                    </py:choose>
                                                </li>
                                            </div>
                                            <div class="confident95" py:when="vdata['confidence'][goal] &gt;= 0.95">
                                                <li>
                                                    You have collected enough data to be 95% sure that this difference is not simply due to chance factors.
                                                </li>
                                                <li class="recommendation">
                                                    Recommendation: <strong>let the test run for longer to be completely certain</strong>.
                                                </li>
                                            </div>
                                            <div class="unconfident" py:otherwise="">
                                                <li>
                                                    You don't have enough data to be sure yet that this difference is due to the variant you are testing or purely chance factors.
                                                </li>
                                                <li class="recommendation">
                                                    Recommendation: <strong>let the test run to collect more data</strong>.
                                                </li>
                                            </div>
                                        </py:choose>
                                    </ul>
                                </py:otherwise>
                            </py:choose>
                        </py:for>
                    </py:if>
                </div>


                <h3>Data</h3>
                <table class="data">
                    <tr>
                        <th rowspan="2">Variant</th>
                        <th rowspan="2">Number of tests</th>
                        <th py:for="goal in goals" colspan="4">Goal: $goal</th>
                    </tr>
                    <tr>
                        <py:for each="goal in goals">
                            <th>conversions</th>
                            <th>rate</th>
                            <th>z-score</th>
                            <th>confidence</th>
                        </py:for>
                    </tr>
                    <tr
                        py:for="variant, vdata in sorted(data[exp.name]['variants'].items())"
                        class="${'control' if variant==control else None}"
                    >
                        <th>
                            <a href="${request.make_uri(query={'control.{0}'.format(exp.name): variant})}">$variant</a>
                            <span class='control' title="This variant is selected as the control: the performance of other variants will be measured against this one" py:if="variant==control">control</span>
                        </th>
                        <td>${vdata['t']}</td>
                        <py:for each="goal in goals">
                            <py:if test="not vdata['t']">
                                <td colspan="3">no data yet</td>
                            </py:if>
                            <py:if test="vdata['t']">
                                <td>${vdata['c'][goal]}</td>
                                <td>${'{0:.1%}'.format(vdata['r'][goal])}</td>
                                <td><py:if test="variant != control">${'{0:.3g}'.format(vdata['z'][goal])}</py:if></td>
                                <td><py:if test="variant != control">${'{0:.1%}'.format(vdata['confidence'][goal])}</py:if></td>
                            </py:if>
                        </py:for>
                    </tr>
                </table>
            </section>
            </body>
        </html>
        """
        data = self.collect_experiment_data()
        for exp in data:

            # Take the first listed variant as the control - though ideally the
            # user would be able to select which variant is the control.
            vdata = data[exp]['variants']

            control = request.get('control.' + exp, self.experiments[exp].control)
            control_total = vdata[control]['t']
            control_rates = vdata[control]['r']
            data[exp]['control'] = control

            for variant in vdata:
                total = vdata[variant]['t']
                rates = vdata[variant]['r']
                vdata[variant]['z'] = {}
                vdata[variant]['confidence'] = {}
                for goal in rates:
                    vdata[variant]['z'][goal] = zscore(rates[goal], total, control_rates[goal], control_total)
                    vdata[variant]['confidence'][goal] = cumulative_normal_distribution(vdata[variant]['z'][goal])

        return {
            'experiments': self.experiments.values(),
            'data': data,
        }

    def collect_experiment_data(self):
        """
        Return collected experiment data from the log files
        """
        data = {}

        for exp in self.experiments.values():
            expdir = os.path.join(self.datadir, exp.name)
            goals = sorted([goal for goal, experiments in self.experiments_by_goal.items() if exp in experiments])
            data[exp.name] = {
                'goals': goals,
                'variants': {},
            }

            for variant in exp.variants:
                path = partial(os.path.join, expdir, variant)
                data[exp.name]['variants'][variant] = {
                    # Total tests
                    't': 0,

                    # Counts for each goal
                    'c': {},

                    # Rate for each goal
                    'r': {},
                }
                total = data[exp.name]['variants'][variant]['t'] = count_entries(path('__all__'))
                for goal in goals:
                    count = count_entries(path(goal))
                    data[exp.name]['variants'][variant]['c'][goal] = count
                    data[exp.name]['variants'][variant]['r'][goal] = float(count) / total if total else float('nan')
        return data

class Experiment(object):
    def __init__(self, name):
        assert '/' not in name
        self.name = name
        self.variants = []

    def add(self, *variants):
        for v in variants:
            assert '/' not in v
            self.variants.append(v)

    @property
    def control(self):
        """
        The control variant for this experiment, will always be the first listed
        """
        return self.variants[0]

def getswabid(environ):
    """
    Return the unique identifier from the WSGI environment if present,
    otherwise return ``None``.
    """
    try:
        return environ['swab.id']
    except KeyError:
        pass
    cookie = Request(environ).cookies.get('swab')
    if cookie:
        environ['swab.id'] = cookie.value
        return cookie.value
    return None

def generate_id():
    """
    Return a unique id
    """
    return md5(
            str(os.getpid())
        + str(time())
        + str(Random().random())
    ).digest().encode('base64').strip()

def show_variant(experiment, environ, record=True):
    """
    Return the variant name that ``environ`` is assigned to within ``experiment``

    If ``record`` is true, write a line to the log file indicating that the
    variant was shown. (No deduping is done - the log line is always written. A
    page with ``show_variant`` might record multiple hits on reloads etc)
    """
    swabid = getswabid(environ)
    swab = environ['swab.swab']
    variants = swab.experiments[experiment].variants
    if not swab.include(experiment, environ):
        return variants[0]

    if swab.debug:
        request = Request(environ)
        variant = request.query.get('swab.' + experiment)
        if variant is not None and variant in variants:
            return variant

    r = Random()
    r.seed(unpack_from('l', swabid.decode('base64')))
    variant = r.choice(variants)
    if not record:
        return variant

    path = os.path.join(swab.datadir, experiment, variant, '__all__')
    try:
        f = open(path, 'a')
    except IOError:
        makedir(os.path.dirname(path))
        f = open(path, 'a')

    try:
        f.write(_logline(getswabid(environ)))
    finally:
        f.close()
    return variant

def _logline(swabid):
    return '%-14.2f:%s\n' % (time(), swabid)

def _logentries(path):
    with open(path, 'r') as f:
        for line in f:
            t, id = line.strip().split(':')
            yield float(t.strip()), id

def record_goal(goal, environ, experiment=None):
    """
    Record a goal conversion by adding a record to the file at
    ``swab-path/<experiment>/<variant>/<goal>``.

    If experiment is not specified, all experiments linked to the named goal
    are looked up.

    This doesn't use any file locking, but we should be safe on any posix
    system as we are appending each time to the file.
    See http://www.perlmonks.org/?node_id=486488 for a discussion of the issue.
    """

    swab = environ['swab.swab']
    if experiment is None:
        experiments = swab.experiments_by_goal[goal]
    else:
        experiments = [swab.experiments[experiment]]
    for experiment in experiments:
        if not swab.include(experiment.name, environ):
            return

        variant = show_variant(experiment.name, environ)
        path = os.path.join(swab.datadir, experiment.name, variant, goal)
        try:
            f = open(path, 'a')
        except IOError:
            makedir(os.path.dirname(path))
            f = open(path, 'a')

        try:
            f.write(_logline(getswabid(environ)))
        finally:
            f.close()

def makedir(path):
    """
    Create a directory at ``path``. Unlike ``os.makedirs`` don't raise an error if ``path`` already exists.
    """
    try:
        os.makedirs(path)
    except OSError, e:
        # Path already exists or cannot be created
        if not os.path.isdir(path):
            raise

def count_entries(path):
    """
    Count the number of entries in ``path``. Entries are deduplicated so that
    only one conversion is counted per identity.
    """
    if not os.path.isfile(path):
        return 0

    seen = set()
    count = 0
    for t, identity in _logentries(path):
        if identity in seen:
            continue
        seen.add(identity)
        count += 1
    return count

def zscore(p, n, pc, nc):
    """
    Calculate the zscore of probability ``p`` over ``n`` tests, compared to control probability ``pc`` over ``nc`` tests

    See http://20bits.com/articles/statistical-analysis-and-ab-testing/.
    """
    try:
        return (p - pc) / sqrt(
            (p * (1 - p) / n)
            + (pc * (1 - pc) / nc)
        )
    except ZeroDivisionError:
        return float('nan')

def cumulative_normal_distribution(z):
    """
    Return the confidence level from calculating of the cumulative normal
    distribution for the given zscore.

    See http://abtester.com/calculator/ and http://www.sitmo.com/doc/Calculating_the_Cumulative_Normal_Distribution
    """

    b1 =  0.319381530
    b2 = -0.356563782
    b3 =  1.781477937
    b4 = -1.821255978
    b5 =  1.330274429
    p  =  0.2316419
    c  =  0.39894228

    if z >= 0.0:
        t = 1.0 / (1.0 + p * z)
        return 1.0 - c * exp(-z * z / 2.0) * t * (t * (t * (t * (t * b5 + b4) + b3) + b2) + b1)
    else:
        t = 1.0 / (1.0 - p * z)
        return c * exp(-z * z / 2.0) * t * (t *(t * (t * (t * b5 + b4) + b3) + b2) + b1)

