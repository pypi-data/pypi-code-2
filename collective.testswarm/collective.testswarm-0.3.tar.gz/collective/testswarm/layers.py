""" The TESTSWARM_LAYER is intended to be used as a base layer. It can
be configured via the environment section of the testrunner
configuration in the buildout.cfg (there is an example of this in the
buildout.cfg in the root). These settings can be overridden by shell
variables. The variable names are prefixed with 'ts_' the shell
variables use uppercase letters and the buildout variables use
lowercase:

$ TS_URL=http://localhost ./bin/test

this overrides the ts_url setting in the testrunner config
section of the buildout
"""
from os import environ
import time

from OFS.Application import AppInitializer
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import quickInstallProduct
from plone.app.testing.layers import PLONE_ZSERVER

import collective.testswarm
from utils import add_testswarm_job

def get_ts_env_var(var, default=""):
    """ Shell variables are in uppercase and take precedence over
    lowercase buildout variables."""
    ts_var = "ts_"+var
    return environ.get(ts_var.upper(), environ.get(ts_var, default))


class TestSwarmLayer(PloneSandboxLayer):
    """ To be used as a base layer """
    defaultBases = (PLONE_ZSERVER, )

    def setUpZope(self, app, configurationContext):
        """ Virtual hosting is not installed by default but may be
        needed for making the test instance accessible e.g. from a
        subdirectory of the TestSwarm instance."""
        self.loadZCML(package=collective.testswarm)
        app_init = AppInitializer(app)
        app_init.install_virtual_hosting()

    def setUpPloneSite(self, portal):
        """ Registers the TestSwarm inject.js from the TestSwarm
        instance running the tests."""
        quickInstallProduct(portal, "collective.testswarm")
        self["ts_url"]  = get_ts_env_var("url")
        portal.portal_javascripts.registerScript(cacheable="False",
              compression="none", conditionalcomment="", cookable="False",
              enabled="True", expression="",
              id=self["ts_url"]+"/js/inject.js", inline="False")

    def testSetUp(self):
        """ Collects the environment variables and adds the test job
        with those parameters. When the timeout is finished the actual
        tests which use this layer would be run. There should be no
        reason to have anything in those tests (that I can think
        of)."""
        ts_args = []
        for arg in ["url", "user", "auth", "job_name", "urls", "suites",
                    "browsers", "max_jobs"]:
            ts_args.append(get_ts_env_var(arg))
        job_url = add_testswarm_job(*ts_args)
        print("TestSwarm job: %s" % job_url)

        timeout = float(get_ts_env_var("timeout"))
        time.sleep(timeout)


TESTSWARM_LAYER = TestSwarmLayer()


class TestTestSwarmLayer(PloneSandboxLayer):
    """ For testing the TestSwarmLayer, also serves as an example of
    how to use the layer """
    defaultBases = (TESTSWARM_LAYER, )

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'collective.testswarm:test')

TESTTESTSWARM_LAYER = TestTestSwarmLayer()
