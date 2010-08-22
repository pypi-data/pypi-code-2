#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Useful functions for find databases and plotting.

It can be imported into ipython as
%ed analyse.py
or as
%run analyse.py
"""

import glob, fnmatch
import shelve
import os
import sys
import re
import pylab
from settings import database_directory

if __name__ == "__main__":
    from optparse import OptionParser
    usage = "%prog [options]"
    parser = OptionParser()
    parser.add_option("-d", "--db_regex", metavar="DB",
	help = "select only the database names matching the pattern. .db is omitted. Example: *test*")

    (options, args) = parser.parse_args()

directory = "Runs"

"""The tree of keys in the databases:

database
    +- command
    +- message
    +- starting_time (as time.time() gives)???
    +- max_time (float, minutes)
    +- max_nodes (int)
    +- measurements (list of 3-tuples
             (str measurement_name, dict params, freq))
    +- uname (list)
    +- networkx_version (str)
    +- bzr_revision (int)
    +- <run>...
        +- values
            +- <measured_value>... (tuple: int frequency, list values)
        +- running_time_minutes
        +- last_period
        +- models (list of 2-tuples:
            (str name_of_model_with_parameters, float probability_in_period))
        +- save_graph ?? should be boolean

"""


class Databases:
    """List and plot databases."""

    def __init__(self, db_regex='*', directory=database_directory):
        """Get the databases matching the db_regex.

        db_regex: regular expression to narrow the list of databases
           It will match the name without path and the ".db" extension.

        regular expressions are shell-like expressions like barabasi*.db

        """
        self.directory = directory
        self.databases = sorted(glob.glob(os.path.join(directory, db_regex+".db")))
        print "I have found %d databases." % len(self.databases)
        self.ignored_keys = [
            "max_time", "max_nodes",
            "uname", "measurements",
            "graphmodule_version", "networkx_version",
            "bzr_revision",
            "command", "message",
            ]
        self.value_order = ["number_of_nodes",
                    "number_of_components",
                    "number_of_edges",
                    'diameter_of_biggest_component',
                    'order_of_biggest_component',
                    'average_order_of_other_components',
                    'exponent',
                    'exponent_sigma',
                    'i',
                    's',
                    'r',
                    'state_infective',
                    'state_susceptible',
                    'state_recovered',
                    'number_of_infected_components',
                    'number_of_infective_components',
                ]
        print """Some hints:
        d=Database("inf*")
        d.list_databases()
        db, run, values = d.get_values("*035", "R=1.5*")
        d.plot_formula("state_infective/number_of_nodes")
        pylab.show()
        """
        self.last_database = self.last_run = None


    def matching_databases(self, db_regex):
        """Returns the name of databases matching the regular expression db_regex.

        It will match the name without path and the ".db" extension.
        """
        
        if db_regex.endswith(".db"):
            db_regex = db_regex[:-3]
        database_names = [ os.path.split(d)[1][:-3] for d in self.databases ]
        return [ os.path.join(self.directory, d+".db") for d in database_names if fnmatch.fnmatch(d, db_regex) ]

    def get_database(self, db_regex):
        """Returns the databases matching the regular expression db_regex.
        """
        matching_databases = self.matching_databases(db_regex)

        if len(matching_databases) > 1:
            print "There are several databases matching the expression listed below."
            if self.last_database:
                db = self.last_database
            else:
                print "There are several databases matching the expression listed below,\nI use the first one."
                for i in matching_databases:
                    print " - %s" % i
                db = matching_databases[0]
                self.last_database = db
        elif len(matching_databases) == 0: 
            print "There is no database matching the expression."
            return

        try:
            d = shelve.open(db)
        except anydbm.error:
            print "Database %s has failed to open."
        matching_runs = self.matching_runs(d.keys(), "*")

        if len(matching_runs) >= 1:
            print "There are several runs matching the expression listed below"
            for i in matching_runs:
                print " - %s" % i
        elif len(matching_runs) == 0: 
            print "There is no run matching the expression."
            return

        return d
        

    def matching_runs(self, keys, run_regex="*"):
        return [key for key in keys
            if (key not in self.ignored_keys and
                fnmatch.fnmatch(key, run_regex))
            ]

    def get_values(self, db_regex="*", run_regex="*"):
        """Get values of a run of a database.
        
        db_regex: regular expression to narrow the list of databases
           It will match the name without path and the ".db" extension.
        run_regex: regular expression to narrow the list of runs

        Return:
         A tuple with (database_name, run_name, values).

        regular expressions are shell-like expressions like barabasi*.db

        """
        matching_databases = self.matching_databases(db_regex)

        if len(matching_databases) > 1:
            print "There are several databases matching the expression listed below,\nI use the first one."
            for i in matching_databases:
                print " - %s" % i
        elif len(matching_databases) == 0: 
            print "There is no database matching the expression."
            return

        db = matching_databases[0]
        self.last_database = db
        try:
            d = shelve.open(db)
        except anydbm.error:
            print "Database %s has failed to open."
        matching_runs = self.matching_runs(d.keys(), run_regex)

        if len(matching_runs) > 1:
            print "There are several runs matching the expression listed below,\nI use the first one."
            for i in matching_runs:
                print " - %s" % i
        elif len(matching_runs) == 0: 
            print "There is no run matching the expression."
            return
        
        run=matching_runs[0]
        self.last_run = run
        m = d[run]
        values=m["values"]

        print "\nDatabase: %s\nRun: %s" % (db, run)
        print "-"*62
        print "|            VALUE NAME             | LAST VALUE | FREQUENCY |"
        print "-"*62

        keys = [i for i in self.value_order if i in values.keys()]
        keys +=  [i for i in sorted(values.keys()) if i not in self.value_order]

        for i in keys:
            print "| %-33s | %10.10s | % 5d     |" % (i, values[i][1][-1], values[i][0])
            print "-"*62
        return db, run, values

    def list_databases(self, db_regex='*', min_periods=100, write_hidden=False):
        """List the main properties of the databases.

        db_regex: regular expression to narrow the list of databases
           It will match the name without path and the ".db" extension.

        regular expressions are shell-like expressions like barabasi*.db

        """

        hidden_databases = 0
        for db in sorted(self.matching_databases(db_regex)):
            try:
                d = shelve.open(db)
            except anydbm.error:
                print "Database %s has failed to open."
                continue
            hide_database = True
            output = "\n*** %s ***\n" % db
            if d.has_key("command"):
                output += "Command: %s\n" % d["command"]
            if d.has_key("message"):
                output += "Message: %s\n" % d["message"]
            runs = [k for k in d.keys() if k not in self.ignored_keys]
            runs.sort()
            for r in runs:
                    output += "- %s:\n" % r
                    try:
                        run = d[r]
                        values = run["values"]
                        freq, number_of_nodes = values["number_of_nodes"]

                        if run.has_key("last_period"):
                            last_period =  run["last_period"]
                            if last_period < min_periods:
                                break
                            elif hide_database:
                                hide_database = False
                            output += "  number of periods = %d\n" % last_period
                        else:
                            l = len(number_of_nodes)
                            output += "  %d <= number of periods < %d\n" %  ( (l-1) * freq, l*freq )
                            if (l-1) * freq < min_periods:
                                break
                            elif hide_database:
                                hide_database = False

                        output += "  number of nodes in the end: %d\n" % number_of_nodes[-1]
                        freq, number_of_components = values["number_of_components"]
                        output += "  number of components in the end: %d\n" % number_of_components[-1]
                    except:
                        output += "  some values can not be stated\n"
            if not hide_database:
                print output[:-1]
            else:
                hidden_databases += 1
                if write_hidden:
                    print "\n*** %s is hidden ***" % db
        if hidden_databases:
            print "\n*** There were %d hidden databases ***\nuse the option write_hidden=True to see them.\n" % hidden_databases


    def calculate(self, formula, values=None):
        """Calculate a formula for the values available."""

        if values is None:
            d = shelve.open(self.last_database)
            values = d[self.last_run]["values"]
        variables = get_variables(formula)
        vardict = {}
        for var in variables:
            vardict[var] = self.make_dict(values[var])
        possible_x = vardict[variables[0]].keys()
        points = {}
        for x in possible_x:
            try:
                for var in variables:
                    exec "%s = float(vardict[var][x])" % var
            except KeyError:
                continue
            exec "points[x] = %s" % formula
        return points

    def plot_points(self, points, normed=False, **kwargs):
        """Plot the points given as key: value pairs.

        You can use the parameters of the pylab.plot function.
        """
        x = sorted(points.keys())
        y = [points[xx] for xx in x]
	fmt = kwargs.get("fmt")
        if fmt is not None:
	    del kwargs["fmt"]
            pylab.plot(x,y, fmt, **kwargs)
        else:
            pylab.plot(x,y, **kwargs)

    def plot_formula(self, formula, normed=False, **kwargs):
        """Plot a formula calculated from the measured values.

        Example:
        >>> d = Database("infe*001*")
        >>> d.plot_formula("2*number_of_edges/number_of_nodes", normed=True)

        You can use the parameters of the pylab.plot function.
        """
        points = self.calculate(formula)
        if normed:
            maxval = max(points.values())
            for key in points.keys():
                points[key] /= float(maxval)
	if not kwargs.has_key("label"):
	    kwargs["label"] = formula
        self.plot_points(points, **kwargs)


    #TODO Do not work. Perhaps we should use value name aliases instead.
    def rename_key(self, name, new_name, db_regex="*", place="run/values"):
        """Rename the name of a key in all matching databases."""

        place = place.split('/')
        for db in self.matching_databases(db_regex):
            d = shelve.open(db)
            if place and place[0] == "run":
                for run in  self.matching_runs(d.keys()):
                    place[0] = run
                    self.rename_key(name, new_name,
                        db_regex=db, place = "/".join(place))
            pointer = d
            for i in place:
                if not pointer.has_key(i):
                    continue
                pointer = pointer[i]
            if pointer.has_key(name):
                if pointer.has_key(new_name):
                    raise ValueError('I can not rename the old name to an existing new name\n(old=%s, new=%s)' % (name, new_name))
                pointer[new_name] = pointer[name]
                del pointer[name]
                print db, "/".join(place)


    def make_dict(self, values_item):
        """Make a dictionary with x: y pairs.

        None values for y are ignored.
        """

        freq, value_list = values_item
        x=freq*pylab.arange(len(value_list))
        tuples =  zip(x, value_list)
        tuples = [ t for t in tuples if t[1] is not None ]
        return dict(tuples)


def get_variables(formula, verbose = 0):
    "Returns with the variables in the formula."

    var_pattern = re.compile('''
	(
       [a-zA-Z] # first letter
       \w*      # alphanumeric characters
       )
       (
         [^(\w]   # not opening bracket at the end (not a function)
           |
         $        # it can be at the end of the string
       )
       ''', re.VERBOSE)

    vars = formula[:]
    variables = []
    scan_from = 0
    while 1:
      var1 = var_pattern.search(vars[scan_from:])
      if verbose > 0: print " "*(5-verbose),  '**sm  Scanned in "%s".' % vars[scan_from:]
      if var1:
        var = var1.group(1)
	if var not in variables:
            variables.append(var1.group(1))
            if verbose > 1: print " "*(5-verbose),  '**sm   Variables in the formula: %s' % variables
        scan_from += var1.end()
        if verbose > 1: print " "*(5-verbose),  '**sm   Scan from: %s' % scan_from

      else:
        if verbose > 0: print " "*(5-verbose),  '**sm   Variables in the formula: %s' % variables
        break

    return variables

#clf()
plotted = [
[0, "number_of_nodes", 1, "x"],
[0, "order_of_biggest_component", 1, "+"],
[0, "number_of_components", 50, "v"],
[0, "i", 1, "."],
[0, 'exponent', 100, "o"],
[0, 'exponent_sigma', 1000, "*"],
]

plotted1 = [
[0, "number_of_components", 1, "+"],
[1, "number_of_components", 1, "x"],
[2, "number_of_components", 1, "."],
]

def plot_(values_, plotted, pos=2):
    l=[]
    for run, p, multiplier, fmt in plotted:
        #p = p.replace(" ", "_")
        freq, values = values_[run][p]
        x=freq*arange(len(values));print x[:20], len(x), len(multiplier*values)
        plot(x,multiplier*array(values), fmt)
        p_space = p.replace("_", " ")
        if multiplier == 1:
            l.append(p_space)
        else:
            l.append("%d*%s" % (multiplier, p_space))
        
    legend(l, pos)
    xlabel("period")

#axis([0,800,0,710])
#title(u"Infective random failure model, R=3, m=3, beta=0.01")
#savefig("Runs/Infective_failure_R3_3.pdf")

if __name__ == "__main__":
    kwargs = {}

    d = Databases()
    if options.db_regex:
        print "re '%s'" %  options.db_regex
        kwargs["db_regex"] = options.db_regex
    d.list_databases(write_hidden=True, **kwargs)

