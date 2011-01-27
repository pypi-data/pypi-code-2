"""Main cifit library code."""
from cifitlib.classes import classes
import cifitlib.appadm
import cifitlib.files
import cifitlib.network
import cifitlib.pkgs
import cifitlib.procs
import cifitlib.state

#Make everything userfriendly here, to get exposed.
# THIS IS 'bad magic', but it makes things friendlier to user
sysadm = cifitlib.appadm.SysADM()
mysql = cifitlib.appadm.MysqlADM() 
mailman = cifitlib.appadm.MailmanADM()
pg = cifitlib.appadm.PostgresADM()
cifitlib.pear = cifitlib.pkgs.pearPKG()
cifitlib.state = cifitlib.state.State
cifitlib.runs = cifitlib.state('cifit_runs')

#Make sure I use distribute instead of setuptools tho... 
#XXX: UPDATE THIS.
try:
	import setuptools
	__version__ = setuptools.pkg_resources.get_distribution('cifitlib').version
except:
	import version
	__version__ = version.version

cifitlib.runs.add(__version__)
