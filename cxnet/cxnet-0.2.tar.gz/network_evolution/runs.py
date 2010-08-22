#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Main programm.

We define here the measurements, models and so on,
and run the evolution
(usually in an outer cycle changing the parameters of the run).

For commandline options:
runs.py --help

See ../doc/cn_edu/network_evolution.pdf for details.

"""

from __future__ import division

from optparse import OptionParser
import sys
from settings import database_directory

#TODO  It works only if this file is in this directory.
import network_evolution
import models
#import measurements

usage = "%prog [options]"
parser = OptionParser()
parser.add_option("-d", "--database", metavar="DB",
    help = "the name of the database will be DB_ddd.db (ddd is decimal number)")
parser.add_option("-t", "--test", action="store_true", default=False,
    help="runs with shorter maxtime and databasefiles like *_test_ddd.db")
parser.add_option("-T", "--max_time", metavar="MT",
    type = "float",
    help = "set the maximum running time to MT minutes")
parser.add_option("-N", "--max_nodes", metavar="MN",
    type = "int",
    help = "set the maximum nodes for the runs to MN")
parser.add_option("-g", "--group", metavar="GRP",
    dest = "run_group_number",
    type = "int",
    help = "set run_group_number to GRP")
parser.add_option("-R", "--R_list", metavar="LIST",
    help = "set the R values to as given in LIST. Format of LIST is a comma separated list (without space) like '1.5,2,2.5,3'.")
parser.add_option("-b", "--beta_list", metavar="LIST",
    help = "set the beta values to as given in LIST. Format of LIST is a comma separated list (without space) like '0.01,0.02,0.05'.")
parser.add_option("-m", "--message", metavar="MSG",
    default = None,
    type = "str",
    help = "store the message for the run in the database")
parser.add_option("-q", "--quiet", action="store_false", default=True,
    dest = "to_screen",
    help="the program writes (almost) nothing to screen")

(options, args) = parser.parse_args()

def easy_run(run_group, R_list, type=None, name_format=None, max_nodes=1000, max_time=30, m=3, initial_network = None):
    """It sets the parameters for the run group.
    run_group
    R_list: list of R-s it will go through
    type (string or None):
         "barabasi_albert",
         "node_failure",
         "infective_random_failure",
         None=it uses the name of run_group
    name_format: see in run method
    m: the parameter of Barabasi-Albert model
    """

    if options.max_nodes is not None:
        max_nodes = options.max_nodes
    if options.max_time is not None:
        max_time = options.max_time
    if options.test is True:
        max_time = 0.5
        run_group += "_test"
    if options.R_list is not None:
        R_list = [float(R) for R in options.R_list.split(',')]
    if options.beta_list is not None:
        beta_list = [float(beta) for beta in options.beta_list.split(',')]
    else:
        beta_list = [0.01]

    list_of_types = ["barabasi_albert", "node_failure", "infective_node_failure"]
    if type is None:
        if run_group in list_of_types:
            type = run_group
        for i in list_of_types:
            if run_group.startswith(i):
                type = i

    if type is None:
        raise ValueError( "I do not know the type '%s' and can not state from run_group '%s'." %
            (type, run_group) )


    evolution = network_evolution.NetworkEvolution(measurements = measurements_, run_group = run_group, max_nodes=max_nodes, max_time=max_time, to_screen= options.to_screen, message= options.message, directory=database_directory, command= " ".join(sys.argv))
## There are max_nodes and max_time (in  minutes) arguments.

    variations = [(R, beta) for R in R_list for beta in beta_list]
    for R, beta in variations:
        d = {
            "R": R,
            "p_g" : R/(R+1),
            "p_d" : 1/(R+1),
            "p_g0" : (R-1)/(R+1),
            "m": m,
        }

        if type == "barabasi_albert":
            models_ = [
            (models.BarabasiAlbertModel(d["m"]), d["p_g0"]),
            ]
            name_format0 = "p_g0=%(p_g0)g, m=%(m)d, (R=%(R)g)" % d
        elif type == "node_failure":
            models_ = [
            (models.BarabasiAlbertModel(d["m"]), d["p_g"]),
            (models.NodeFailureModel(), d["p_d"]),
            ]
            name_format0 = "R=%(R)g, m=%(m)d" % d
        elif type == "infective_node_failure":
            d["beta"] = beta
            models_ = [
            (models.BarabasiAlbertModel(3), d["p_g"]),
            (models.InfectiveFailureModel(), d["p_d"]),
            (models.SI_Model(d["beta"]), 1)
            ]
            name_format0 = "R=%(R)g, m=%(m)d, beta=%(beta)g" % d
            initial_network = network_evolution.network.epidemic_BA_network()
        else:
            raise ValueError('There is no type "%s".' % type)

        for key in d.keys():
            print "%20s: %s" % (key, d[key])


        if name_format is None:
            name = name_format0
        else:
            name = name_format % name_format0

        if initial_network is None:
            initial_network = 100
        evolution.run(name = name, initial_network = initial_network, models = models_) 

run_group_number = 2
if options.run_group_number is not None:
    run_group_number = options.run_group_number

if run_group_number == 0:
    measurements_ = [
        ("component_properties", {}, 10),
        ("degree_distribution", {}, 10),
        ("diameter", {}, 250),
        #("write_dot", {"file": "proba"}, -1),
        ]
    easy_run(run_group="barabasi_albert", R_list=[1.5, 3], max_nodes=1500)
elif run_group_number == 1:
    measurements_ = [
        ("component_properties", {}, 10),
        ("diameter", {}, 250),
        ]
    easy_run(run_group="node_failure", R_list=[1, 1.5, 3], max_nodes=1500)
elif run_group_number == 2:
    measurements_ = [
        ("component_properties", {}, 10),
        ("degree_distribution", {}, 10),
        ("diameter", {}, 250),
        ("states", {}, 10),
        ]
    easy_run(run_group="infective_node_failure", R_list=[1.5, 3], max_nodes=1500)
else:
    raise ValueError( "There is no group number %d." % run_group_number )

