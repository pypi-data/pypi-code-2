from django import template
from django.template import Context, loader
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse

class NotaDuckError(BaseException):
	def __init__(self,value):
		self.value = value

	def render(self):
		print "bar is not actually a bar. [ {0} ]".format(self.value)

NAVIGATIONBARS = {}

class NavigationManager:

	def __init__(self):
		pass

	def bars(self):
		return NAVIGATIONBARS.items()

	def get_bar(self, name=None):
		found_bar = None
		for bar_name, bar in NAVIGATIONBARS.items() :
			if not found_bar and bar_name == name :
			 found_bar = bar

		if not found_bar :
			return None
		else :
			return found_bar

	def add_bar(self, name=None ):
		bar = self.get_bar(name)
		if not bar :
			bar = NavigationList( parent=self, name = name )
			NAVIGATIONBARS[name] = bar
		return bar

	def add_to_bar(self, name=None, buttons=None):
		try :
			bar = self.get_bar(name = name)
			if not hasattr(bar, "add_buttons"):
				raise NotaDuckError, "Returned bar was not actually a bar. :>"
		except :
			raise BaseException, "Bar %s not found" % name
			return None
		bar.add_buttons(buttons)

	def set_bar_attributes(self, name=None, attributes=None):
		bar = self.get_bar(name)
		bar.set_attributes(attributes)

	def set_bar_global(self, name=None, mode=True):
		if name :
			bar = self.get_bar(name)
			bar.set_global(mode)

	def get_global_bars(self):
		global_bars = []
		for bar in NAVIGATIONBARS.items():
			if bar.is_global() :
				global_bars.append(bar)
		return global_bars




class NavigationList :
	"""
		A bar of buttons
	"""
	def __init__(self, parent=None, name=None, attributes=None, buttons=None, is_global=False):
		self._name = name
		self._buttons = []
		self._is_global = False
		self._parent = None
		self._attributes = None
		self._name = None

		if attributes :
			self._attributes = attributes
		if buttons :
			self.add_buttons(buttons)
		self.set_global(is_global)

	def get_name(self):
		return self._name
	def set_name(self, value):
		self._name = value

	def get_attributes(self):
		return self._attributes
	def set_attributes(self, attributes=None):
		self._attributes = attributes

	def set_global(self, toggle):
		self._is_global = toggle
	def is_global(self):
		return self._is_global

	def add_button(self, button):
		#TODO: Render button html here, looking for children and rendering those too
			self._buttons.append( render_button(button) )

	def add_buttons(self, buttons=None):
		if buttons :
			for button in buttons :
				self.add_button(button)

	def get_buttons(self, context=None):
		user = context['request'].user
		buttons = []

		if user :
			user_permissions = user.get_all_permissions()
		else:
			user_permissions = ()

		for button in self._buttons :
			if "permissions" in button.keys() :
				try :
					if user and user.has_perms( button['permissions'] ) :
						buttons.append(button)
				except:
					pass
			else :
				buttons.append(button)

		return buttons

def render_button( button ):

	if not isinstance(button, dict):
		raise BaseException, "button data needs to be a dictionary."

	else :
		if not 'url' in button.keys() :
			try :
				viewname = button['viewname']
				urlconf = button['urlconf']
				if 'args' in button.keys():
					args = button['args']
				else:
					args = None
			except :
				raise BaseException, "Missing data from button dictionary"

			button['url'] = reverse( viewname, urlconf = urlconf, args= args )

		if button.has_key("children") and isinstance(button["children"],list) :
			children = []
			for child in button["children"] :
				children.append( render_button(child) )
			button['sub'] = children

	return button

