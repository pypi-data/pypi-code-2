# -*- coding: utf-8 -*-

"""
Has the different commands used by the application.
"""

import argparse
import logging

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(choices=['web', 'initialize'],
                        dest='program')

    args = parser.parse_args()
    if args.program == 'initialize':
        logging.basicConfig(level=logging.INFO, filename = 'initialize.log', filemode='w')
        from pywebuml.initialize.initialize_database import ParserExecuter
        parser = ParserExecuter()
        parser.parse('.')
    if args.program == 'web':
        # TODO encontrar alguna solucion mejor que este hack feo al logging
        logging.basicConfig(level=logging.INFO)
        from pywebuml.web import start_app
        start_app()


