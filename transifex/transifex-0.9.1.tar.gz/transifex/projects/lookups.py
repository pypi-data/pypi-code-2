from django.db.models import Q
from projects.models import Project, Component

class ProjectsLookup(object):
    """A lookup class, used by django-ajax-select app to search Project objects."""

    def get_query(self, q, request):
        """
        Return a query set.

        You also have access to request.user if needed.
        """
        return Project.objects.filter(Q(slug__istartswith=q) |
                                      Q(name__istartswith=q))

    def format_item(self, project):
        """Simple display of an project object when displayed in the list."""
        return unicode(project)

    def format_result(self, project):
        """
        A more verbose display, used in the search results display.

        It may contain html and multi-lines.
        """
        return u"%s" % (project)

    def get_objects(self, ids):
        """Given a list of ids, return the projects ordered."""
        return Project.objects.filter(pk__in=ids).order_by('name')


class ComponentsLookup(object):
    """
    A lookup class, used by django-ajax-select app to search Component 
    objects.
    """

    def get_query(self, q, request):
        """
        Return a query set.

        You also have access to request.user if needed.
        """
        return Component.objects.filter(Q(slug__istartswith=q) |
                                        Q(name__istartswith=q) |
                                        Q(project__slug__istartswith=q) |
                                        Q(project__name__istartswith=q))

    def format_item(self, component):
        """Simple display of an component when displayed in the list."""
        return unicode(component)

    def format_result(self, component):
        """
        A more verbose display, used in the search results display.

        It may contain html and multi-lines.
        """
        return u"%s" % (component)

    def get_objects(self, ids):
        """Given a list of ids, return the components ordered."""
        return Component.objects.filter(pk__in=ids).order_by('name')
