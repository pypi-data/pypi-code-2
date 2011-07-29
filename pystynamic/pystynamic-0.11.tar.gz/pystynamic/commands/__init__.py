import os
import sys
import argparse
import logging


def run_command(args):
    args = parser.parse_args()
    if not isinstance(args, argparse.Namespace):
        sys.exit(1)

    logger = logging.getLogger('pystynamic')
    level = logging.DEBUG if args.verbose else logging.INFO
    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    try:
        args.func(args)
    except KeyboardInterrupt:
        pass

# The functions that run when a specific command is used.
def serve(args):
    from pystynamic.commands.serve import serve_command
    current_directory = os.path.abspath(os.curdir)
    serve_command(current_directory, port=args.port)

def generate(args):
    from pystynamic.commands.generate import generate_command
    current_directory = os.path.abspath(os.curdir)
    output_directory = os.path.join(current_directory, args.directory)
    generate_command(current_directory, output_directory, force=args.force)
    
# Create the parser for the command line arguments.
parser = argparse.ArgumentParser(description='Create static pages through dynamic content')
parser.add_argument('-v', '--verbose', action='store_true', help='More verbose output', default=False)
subparsers = parser.add_subparsers(help='Commands')
    
serve_subparser = subparsers.add_parser('serve', help='Serve the site for debugging purposes.',
    epilog='Serve the site for debuggin purposes.')
serve_subparser.set_defaults(func=serve)
serve_subparser.add_argument('-p',  '--port', type=int, help='The port to host the site on (default 8000)', default=8000)

generate_subparser = subparsers.add_parser('generate', help='Generate a full version of the site at a specific directory.',
    epilog='Generate a full version of the site into a specific directory.')
generate_subparser.set_defaults(func=generate)
generate_subparser.add_argument('-f', '--force', action='store_true', help='Do not warning user about overwriting directory', default=False)
generate_subparser.add_argument('directory', help='The directory to output the website to.')

