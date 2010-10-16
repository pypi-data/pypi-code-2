from cProfile import run
from pstats import Stats
from os import path
import glob

from regression_tests import run_test

## Configuration ##

# How many line to show
LIMIT = 10

# Extra module filtering. Can Be: A name of a module, Empty String for All,
#	None for htmllist modules only.
EXTRA = None

# The name of the test to run (from regression tests)
TEST = "ebay"

# Sort columns by: time, calls, cumulative, file...
SORT = "time"

################################################################################

if EXTRA is None:
	modules = [path.basename(module) for module in glob.glob("../*.py") \
		if "__" not in module]
	reg = "(" + "|".join(modules) + "):"
else:
	reg = None

run("run_test('" + TEST + "', 0, for_profiling=True)", "stats")
stats = Stats("stats")
stats.strip_dirs()
stats.sort_stats(SORT)

stats.print_stats(reg, EXTRA, LIMIT)
stats.print_callees(reg, EXTRA, LIMIT)
stats.print_callers(reg, EXTRA, LIMIT)

