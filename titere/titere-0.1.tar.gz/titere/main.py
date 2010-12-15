import argparse
from titere import Titere
from termcolor import colored


def main():
    """
    Main command-line execution loop.
    """

    # Create command-line parser.
    parser = argparse.ArgumentParser(
        description="Run a titere configuration.")

    # Define arguments.
    parser.add_argument('start_filename', type=str, nargs=1, help='Start file.')

    # Parse arguments.
    args = parser.parse_args()

    # Open Start file
    titere = Titere(filename=args.start_filename[0])

    # Apply configuration.
    try:
        titere.apply()
    except Exception, e:
        print colored(e, 'red')
