# -*- coding: utf-8 -*-

'''
Has some custom filters.
'''

from jinja2 import contextfilter



def get_final_rigth_edge_name(package_name, class_name = None):
    if class_name:
        return class_name

    if '.' in package_name:
        return package_name.rsplit('.')[1]
    else:
        return package_name


@contextfilter
def create_edge(context, current_package, related_package,
                related_classname = None, reverse = False):
    ''' Returns the edge of the graph.

    It the related_package exists in the clases that will be detailed
    then it will create the edge using the package. If not it will use
    the class name if avialable. If it isn't available, it will take
    it form the package.


    By default, it will create and edge from `current_package` to
    `related_package`. Unless the reverse is setted.

    :parameters:
        context:
            the current context jinja of the file
        current_package: str
            the package of the current class that was detailed in the
            dot file.
        related_package: str
            the package of the class that is related to the current class.
            Basically, it is related by inheritence, interface, inner or an
            attribute.
        related_classname: str
            if available, the name of the class that is related.
        reverse: boolean
            if the edge should be reversed or not.

    :returns:
        the edge as defined in graphiz (but it won't end with ;)
    '''
    left = None
    right = None
    if reverse:
        right = current_package.replace('.', '')
    else:
        left = current_package.replace('.', '')

    if related_package in context['class_packages']:
        if reverse:
            left = related_package.replace('.', '')
        else:
            right = related_package.replace('.', '')
    else:
        if reverse:
            left = get_final_rigth_edge_name(related_package, related_classname)
        else:
            right = get_final_rigth_edge_name(related_package, related_classname)

    if left == 'globalSplineV' and right == 'globalDebugCamera':
        import pdb; pdb.set_trace()
    return '%s -> %s' % (left, right)


