from django.template import Library, TemplateSyntaxError
from django.template.loader_tags import BlockNode
from django.utils import simplejson as json
from django.utils.safestring import mark_safe
from django_partial_page.middleware import _thread_locals, capture_blocks

register = Library()


@register.simple_tag
def partial_js_data():
	if len(_thread_locals.partial['data']) == 0:
		return ''

	return mark_safe('<script>require(["partial"], function (p) {{ p.data = {0}; }})</script>'.format(json.dumps(_thread_locals.partial['data'])))


class DelayedBlockNode(BlockNode):
	"""
	DelayedBlockNode can have a stub part:
	{% delayed_block block1 %}
		real content that's too big to send immediately
	{% delayed_stub %}
		stub content that's short and can be shown right away
	{% enddelayed_block %}

	If the request is normal, delayed block will render the stub content, if present. If the request is partial, it will render the normal content.

	You can mix delayed blocks with those normal, the end result will be what is rendered in the lowermost level. The {{ block.super }} context variable will be different depending on what request is sent.
	"""
	def __init__(self, name, nodelist, nodelist_stub):
		self.nodelist_real = nodelist
		self.nodelist_stub = nodelist_stub
		super(DelayedBlockNode, self).__init__(name, nodelist)

	@capture_blocks
	def render(self, context):
		if self.name in getattr(_thread_locals.request, 'partials', []):
			self.nodelist = self.nodelist_real
			return super(DelayedBlockNode, self).render(context)
		
		self.nodelist = self.nodelist_stub
		return mark_safe('<div id="partial_{0}" class="partial_delayed">{1}</div>'.format(self.name, super(DelayedBlockNode, self).render(context)))


@register.tag
def delayed_block(parser, token):
	"""
	Define a block that can be overridden by child templates and delayed (rendered later).

	This code is a mix of django.template.loader_tags.do_block and django.template.default_tags.do_for.
	"""
	bits = token.contents.split()
	if len(bits) != 2:
		raise TemplateSyntaxError("'%s' tag takes only one argument" % bits[0])
	block_name = bits[1]

	# Keep track of the names of BlockNodes/DelayedBlockNodes found in this template, so we can
	# check for duplication.
	try:
		if block_name in parser.__loaded_blocks:
			raise TemplateSyntaxError("'%s' tag with name '%s' appears more than once" % (bits[0], block_name))
		parser.__loaded_blocks.append(block_name)
	except AttributeError: # parser.__loaded_blocks isn't a list yet
		parser.__loaded_blocks = [block_name]

	nodelist = parser.parse(('delayed_stub', 'enddelayed_block', 'enddelayed_block %s' % block_name))
	token = parser.next_token()

	if token.contents == 'delayed_stub':
		nodelist_stub = parser.parse(('enddelayed_block',))
		parser.delete_first_token()
	else:
		nodelist_stub = None

	parser.delete_first_token()
	return DelayedBlockNode(block_name, nodelist, nodelist_stub)
