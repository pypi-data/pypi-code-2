from grokproject.main import main as grokmain
from grokproject import GrokProject
import sys


def main():
    if sys.argv[1] == 'dolmen_basic':
        template_name = 'dolmen_basic'
        sys.argv = [sys.argv[0]] + sys.argv[2:]
    else:
        template_name = 'dolmen'

    grokmain(vars=GrokProject.vars, template_name=template_name)
