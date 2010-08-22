#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module handling network evolution.

It handles evolution models and measurements.

"""

from __future__ import division

import os
import shelve
import sys
sys.path.insert(0, "..")

import settings
if settings.use_igraph_module:
    import igraph_network as network
else:
    import networkx_network as network

import models

import random
from time import localtime, time, strftime
hms = lambda : ".".join("%02d" % i for i in localtime()[:3]) + " " +  ":".join("%2.2d" % i for i in localtime()[3:6])


class NetworkEvolution:
    """Main class of the NetworkEvolution program.

    max_time: maximal running time in minutes.
    max_nodes: maximal nodes, if None it runs as long as max_time.

    See the database structure in analyze.py.

    """

    def __init__(self, measurements, run_group, max_time = 10*60, max_nodes=None, message=None, to_screen=False, directory="Runs", command= None):
        self.measurements = measurements
        self.run_group = run_group
        self.max_nodes = max_nodes
        self.max_time = max_time

        self.directory = directory
        if not os.path.isdir(directory):
            os.mkdir(directory)

        self.file = []
        if to_screen:
            self.file.append(sys.stdout)

        i = 1
        while True:
            self.dbname = os.path.join(directory, "%s_%03d_%s.db" % (run_group, i, os.uname()[1]))
            i += 1
            if not os.path.isfile(self.dbname):
                self.write( "*** Database name: %s ***" % self.dbname )
                break

        f = open("../.bzr/branch/last-revision")
        line = f.readline()
        f.close()
        revision = int(line.split()[0])

        self.properties = {
                            "measurements": measurements,
                            "max_nodes": max_nodes,
                            "max_time": max_time,
                            "uname": os.uname(),
                            "graphmodule_version": network.graphmodule_version,
                            "bzr_revision": revision,
                          }
        if isinstance(command, basestring):
            self.properties["command"] = command
        if isinstance(message, basestring):
            self.properties["message"] = message 
            self.write("Message: %s" % message)
        db = shelve.open(self.dbname)
        for key in self.properties.keys():
            db[key] = self.properties[key]
        db.close()

    def running_condition(self):
        runtime = (time() - self.starttime) /60
        time_condition = (runtime < self.max_time)
        if self.max_nodes is not None:
            node_condition = \
                self.minimum_nodes <= len(self.network) < self.max_nodes
        else:
            node_condition = self.minimum_nodes <= len(self.network)
        return time_condition and node_condition and self.model_level_running_condition 

    def run(self, name, initial_network, models, save_graph=None):

        self.write("Start at %s" % hms())
        self.starttime = time()

        self.minimum_nodes = 0
        is_epidemic = False
        for model, p in models:
            if model.minimum_nodes() > self.minimum_nodes:
                self.minimum_nodes = model.minimum_nodes()
            if model.is_epidemic:
                is_epidemic == True

        if isinstance(initial_network, int):
            self.network = network.Network(name=name, is_epidemic=is_epidemic)
            model = models[0][0]
            model.initial(self.network)
            for i in range(initial_network):
                model.step(self.network)
        else:
            self.network = initial_network

        runproperties = {
            "models": [(str(model), prob) for (model, prob) in models],
            "save_graph" : save_graph,
            }
        values = {}

        for (measurement, params, frequency) in self.measurements:
            if frequency == 0:
                exec("props =  self.network.m_%s(params)" % measurement)
                for property in props.keys():
                    values[property] = (frequency, props[property])
            elif frequency > 0:
                exec("props =  self.network.m_%s(params)" % measurement)
                for property in props.keys():
                    values[property] = (frequency, [props[property]])

        self.network.period = 0

        self.model_level_running_condition = True
        # It turns into False if one of the model level running condition (the
        # return value of the run method of the model object) is False.

        while self.running_condition():
            self.network.period += 1
            for (model, prob) in models:
                if random.random() < prob:
                    self.model_level_running_condition &= model.step(self.network)
            for (measurement, params, frequency) in self.measurements:
                if frequency > 0 and self.network.period % frequency == 0:
                    exec("props =  self.network.m_%s(params)" % measurement)
                    for property in props.keys():
                        values[property][1].append(props[property])

        for (measurement, params, frequency) in self.measurements:
            if frequency == -1:
                exec("props =  self.network.m_%s(params)" % measurement)
                for property in props.keys():
                    values[property] = (frequency, props[property])

        runproperties["values"] = values
        runproperties["last_period"] = self.network.period
        runtime = time() - self.starttime
        runproperties["running_time_minutes"] = runtime/60
        db = shelve.open(self.dbname)
        db[name] = runproperties
        db.close()

        self.write("It took %f seconds = %f minutes" % (runtime, runtime/60))
        self.write("Stop at %s" % hms())
        if save_graph:
            self.network.write_dot("%s_%s.dot" % (self.run_group, name))

        return self.properties

    def write(self, text):
        for file in self.file:
            print >>file, text

