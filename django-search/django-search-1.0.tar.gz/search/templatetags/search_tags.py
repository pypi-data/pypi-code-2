from django import template
from django.template.loader import render_to_string

from search.search import raw_search

register = template.Library()

def do_search(parser, token):

    contents = token.split_contents()

    try:
        context_var = contents[2]
    except IndexError:
        raise template.TemplateSyntaxError("%r tag requires at least 2 arguments, " +
            "in the form of {%% %r object.example_set.all field1 field2 %%}" % contents[0])
    
    return SearchNode(contents[1], contents[2:])
        
class SearchNode(template.Node):
    def __init__(self, queryset_var, fields):
        self.queryset_var = template.Variable(queryset_var)
        self.fields = fields
        
    def render(self, context):

        getvars = context['request'].GET.copy()
        

        if 'search' in getvars: # A seach was done before, filter the context queryset
            
            search_terms = getvars['search']
        
            queryset_name = self.queryset_var.var
            queryset = self.queryset_var.resolve(context)
            queryset = raw_search(queryset,self.fields,search_terms)
            
            context[queryset_name] = queryset
            
            # Delete search GET parameter in order to allow search over other user filters
            
            del getvars['search']

            # Set a variable in context with the link to remove the search

            if len(getvars.keys()) > 0:
                link = "?%s" % getvars.urlencode()
            else:
                link= context['request'].path      

            context['remove_search_link'] = link

            # Set a variable in context with the search terms

            context['search_terms'] = search_terms

        return render_to_string('search/form.html',{'getvars':getvars})

register.tag('search', do_search)

