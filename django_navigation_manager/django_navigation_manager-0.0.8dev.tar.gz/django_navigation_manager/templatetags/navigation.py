from django import template
from django.template import Context, loader
from django.template.loader import render_to_string
from django_navigation_manager.lib.manager import NavigationManager

register = template.Library()


navigation_manager = NavigationManager()
template_path = "navigation_bar.html"

@register.tag
def navigationbar ( parser, token ):
	try:
		tag_name, bar_name = token.split_contents()
	except ValueError:
		raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents[0]
	return NavigationBarNode( bar_name )

class NavigationBarNode ( template.Node ):
	def __init__ ( self, bar_name ):
		self.bar_name = bar_name

	def render ( self, context ):
		try :
			bar = navigation_manager.get_bar( self.bar_name )
			return render_to_string(template_path,{
				"Bar"	: self.items,
				"Name" : self.name
			})
		except :
			return """<!--Bar "%s" Not Found-->""" % self.bar_name

@register.tag
def navigationbar_count ( parser, token = None):
	return NavigationBarCountNode( )

class NavigationBarCountNode ( template.Node ):
	def render ( self, context=None):
		try :
			return len(navigation_manager.bars())
		except :
			return ""

@register.tag
def navigationbar_items ( parser, token = None):
	return NavigationBarItemsNode( )

class NavigationBarItemsNode ( template.Node ):
	def render ( self, context=None):
		try :
			return ".".join([ bar_name for bar_name, bar in navigation_manager.bars().items() ])
		except :
			return ""

