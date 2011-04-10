from django import template
from django.template import Template, Context, loader
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from ..lib.manager import NavigationManager

register = template.Library()

navigation_manager = NavigationManager()


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
		bar = navigation_manager.get_bar( self.bar_name )
		if bar :
			return render_to_string("navigation_bar.html", {
				#TODO : move html rendering into the manager so that it happens
				# on application start up instead of every time the tag is used.
				"Bar"	: {
					"buttons" : bar.get_buttons(context),
					"attributes" : bar.get_attributes(),
					"name" : bar.get_name()
				}
			})
		else :
			return """<!--Bar "%s" Not Found-->""" % self.bar_name

Template_NavigationBars = Template("""<div class="global-bars">
  {% for Bar in Bars %}
    {{ Bar }}
  {% endfor %}
</div>""")

@register.tag
def global_navigationbars ( parser, token ):
	return GlobalNavigationBarNode()


class GlobalNavigationBarNode ( template.Node ):
	def __init__(self):
		pass

	def render ( self, context ):
		output = []
		for name, bar in navigation_manager.bars() :
			if bar.is_global() :
				output.append( render_to_string("navigation_bar.html", {
					"Bar"	: {
						"buttons" : bar.get_buttons(context),
						"attributes" : bar.get_attributes(),
						"name" : bar.get_name()
					}
				}) )
		return Template_NavigationBars.render( Context({"Bars" : output }) )

