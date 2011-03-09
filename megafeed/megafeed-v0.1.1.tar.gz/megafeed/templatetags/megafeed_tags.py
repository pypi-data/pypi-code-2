from django.template import Library, TemplateSyntaxError, Node, Variable
import megafeed

register = Library()

class MegaFeedNode(Node):
	def __init__(self, model, variable, **kwargs):
		self.model    = model
		self.variable = variable
		self.kwargs   = kwargs
	def render(self, context):
#		print self.kwargs
		feed = {}
		for k,v in self.kwargs.iteritems():
			feed[k] = v.resolve(context)
		model = megafeed.load_model(self.model.lower())
		if not model: raise Exception('Feed not found')
		context[self.variable] = megafeed.megafeed(model,
				params=feed, to_dict=None)[self.model.lower()]
		return ''

def megafeed_tag(parser, token):
	"""
	Usage::
		{% megafeed [feed_name] ([key] [value]) as [variable] %}
	"""
	args = token.split_contents()
	kwargs = dict(zip(map(str,args[2:-2:2]),
		(Variable(a) for a in args[3:-2:2])))
	return MegaFeedNode(args[1], args[-1], **kwargs)

register.tag('megafeed', megafeed_tag)
