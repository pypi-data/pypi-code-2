import optparse
import os
import pkg_resources
import subprocess
import sys
import tempfile


for dist in pkg_resources.working_set:
    if dist.project_name == "zc.sbo":
        version = dist.version
assert version


parser = optparse.OptionParser("""\
Usage: %prog [options] application [configuration]

Configure or unconfigure an application defined by a buildout
configuration file.  By default, an application is configured.  If the
-u option is provided, then the application is unconfigured.  An
optional configuration name may be given.  If not given, the
configuration name defaults to the application name.

The buildout configuration path is computed as:

   /etc/${application}/${configuration}.cfg

During configuration, the file:

   /etc/${application}/${configuration}.configured

will be created, which records information about what was configured to
support unconfiguring.

To perform it's work, the script will run:

   /opt/${application}/bin/buildout

So the named application must be installed in /opt.
""", version=("%%prog %s" % version))

parser.add_option(
    '-a', '--all', action="store_true", dest="all",
    help="Operate on all configurations.",
    )

parser.add_option(
    '-i', '--installation', action="store", dest="installation",
    help="""Installation directory of the application.""",
    )

parser.add_option(
    '-l', '--list', action="store_true", dest="list",
    help="""List available configurations.""",
    )

parser.add_option("-q", action="count", dest="quiet",
                  help="Decrease the verbosity")

parser.add_option('--test-root', dest="test_root",
                  help="""\
The location of an alternate root directory for testing.

If this is used then the given directory will be used rather than / to
find the opt and etc directories.
""")

parser.add_option(
    '-u', '--unconfigure', action="store_true", dest="unconfigure",
    help="""\
Remove any configuration artifacts for the given configuration file.
This option reads the associated installation database to discover what
to unconfigure.""")

parser.add_option("-v", action="count", dest="verbosity",
                  help="Increase the verbosity")

def error(message):
    print 'Error:\n%s\n' % message
    try:
        parser.parse_args(['-h'])
    except SystemExit:
        pass
    sys.exit(1)

def assert_exists(label, path):
    if not os.path.exists(path):
        error("%s, %r, doesn't exist." % (label, path))

def configs(config_dir):
    return sorted(
        name[:-4] for name in os.listdir(config_dir)
        if name.endswith('.cfg')
        )

def main(args=None):
    if args is None:
        args = sys.argv[1:]
    options, args = parser.parse_args(args)

    root = options.test_root or '/'

    if not args:
        error("No application was specified.")
    application = args.pop(0)

    if options.installation:
        app_dir = options.installation
    else:
        app_dir = os.path.join(root, 'opt', application)
    assert_exists("The application directory", app_dir)

    buildout = os.path.join(app_dir, 'bin', 'buildout')
    assert_exists("The application buildout script", buildout)

    config_dir = os.path.join(root, 'etc', application)
    assert_exists("The application configuration directory", config_dir)

    if options.list:
        print '\n'.join(configs(config_dir))
        sys.exit(0)

    if options.all:
        configurations = list(configs(config_dir))
        if not configurations:
            error("There aren't any configurations")
    elif args:
        configurations = [args.pop(0)]
    else:
        configurations = [application]

    base_options = [
        "buildout:directory=%s" % app_dir,
        "-oU",
        ]
    verbosity = (options.verbosity or 0) - (options.quiet or 0)
    if verbosity > 0:
        base_options[-1] += 'v'*verbosity
    elif verbosity < 0:
        base_options[-1] += 'q'*(-verbosity)

    base_options[-1] += 'c'

    for configuration in configurations:
        configured = os.path.join(config_dir, '%s.configured' % configuration)

        sbooptions = ([buildout] + args + ["buildout:installed=%s" % configured]
                      + base_options)
        if options.unconfigure:
            if not os.path.exists(configured):
                print "%r doesn't exist.\nNothing to unconfigure." % configured
                sys.exit(0)
            fd, configfile = tempfile.mkstemp("buildout")
            os.write(fd, "[buildout]\nparts=\n")
            os.close(fd)
            if verbosity >= 0:
                print "Unconfiguring:", configuration
            proc = subprocess.Popen(sbooptions + [configfile]
                )
            proc.wait()
            os.remove(configfile)
        else:
            configfile = os.path.join(config_dir, "%s.cfg" % configuration)
            assert_exists("The configuration file", configfile)
            if verbosity >= 0:
                print "Configuring:", configuration
            proc = subprocess.Popen(sbooptions + [configfile])
            proc.wait()
