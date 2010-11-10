import sys

try:
    import argparse

    parser = argparse.ArgumentParser(prog='handcrank',
        description='Hand crank static site generator using reStructuredText')
    parser.add_argument('actions', choices=('generate', 'startsite',),
        help='`generate` will create html from the rST files, `startsite` will '
        'build a new site directory you can start with')
    parser.add_argument('--keepgoing', dest='daemon', action='store_true',
        help='Runs a daemon, re-generating when files change',
        default=False)
    parser.add_argument('--sitedir', dest='site_dir', metavar='SITE_DIR',
        help='Specify the site directory %(metavar)s, should contain a config.cfg')
except:
    pass


def main():
    """
    Called from the handcrank script, this is the main entry point.

    See setup.py for the path that's taken to this function.
    """
    from handcrank.runner import Runner, MissingConfigFile

    if not parser:
        print 'Parser not available, cannot continue'
        sys.exit(1)

    try:
        options = parser.parse_args()
        runner = Runner(options)
        runner.begin()
    except MissingConfigFile as mcf:
        print '%s' % mcf
        sys.exit(1)
