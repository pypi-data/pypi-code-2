from django.core.urlresolvers import reverse
from django.utils.functional import lazy


reverse_lazy = lambda name=None, *args, **kwargs: lazy(reverse, str)(name, args=args, kwargs=kwargs)
