import re
try:
    from xml.etree import cElementTree as etree
except ImportError:
    from xml.etree import ElementTree as etree

from django.conf import settings
from django.db import models

from jqtouch.exceptions import CircularError, RenderingError



_panel_expression = re.compile('^/(?P<identifier>[\w\-_]{1,64})/$')

class Panel(models.Model):
    identifier = models.SlugField(max_length=64, primary_key=True)
    body = models.TextField()
    embed = models.BooleanField(default=True)
    
    def __unicode__(self):
        return self.identifier
    
    def render(self, parents=None, string=True):
        if parents is None:
            parents = []
        
        if self.identifier in parents:
            raise CircularError(parents)
        
        parents.append(self.identifier)
        nodes = []
        
        try:
            node = etree.fromstring('<div id="%s">%s</div>' % (self.identifier,
                                                               self.body))
        except:
            raise RenderingError('Error parsing body of %s' % (self.identifier,))
        
        nodes.append(node)
        
        try:
            for link in etree.ElementTree(node).findall('//a'):
                href = _panel_expression.match(link.get('href',''))
                if href is None:
                    continue
                
                identifier = href.group('identifier')
                
                for resolver in settings.JQTOUCH_PANEL_RESOLVERS:
                    ref = resolver(identifier)
                    if ref is not None:
                        break
                
                if ref is None:
                    continue
                
                if not getattr(ref,'embed', True):
                    continue
                
                try:
                    if hasattr(ref,'render') and callable(ref.render):
                        results = ref.render(parents)
                    else:
                        results = ref
                    
                    if isinstance(results, basestring):
                        nodes.append(results)
                    elif ((hasattr(ref,'__iter__') and callable(ref.__iter__)) or 
                          (hasattr(ref,'next') and callable(ref.next))):
                        nodes.extend(results)
                except CircularError:
                    pass
                
                link.set('href', '#%s' % (identifier,))
            
        except:
            pass
        
        if string:
            return '\n'.join(map(lambda n: isinstance(n, basestring) and n or etree.tostring(n),nodes))
        
        return nodes
