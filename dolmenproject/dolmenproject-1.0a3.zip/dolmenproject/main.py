from grokproject.main import main as grokmain
from grokproject import GrokProject


def main():
    grokmain(vars=GrokProject.vars, template_name='dolmen')
