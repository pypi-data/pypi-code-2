from pkg_resources import get_distribution
version = get_distribution("ckanrdf").version
del get_distribution
