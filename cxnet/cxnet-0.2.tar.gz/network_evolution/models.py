#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Classes for Models
Main model types: growth, random remove, attack, spread of infection

Both have:
- step() method.
- name parameter including the important parameters.
- minimum_nodes method returning with the minimum nodes required the model.
- is_epidemic parameter which is True if the model needs states of nodes.

The step() method returns with the model level running condition.
If it is False, running will be discarded.

"""

import settings
if settings.use_igraph_module:
    from igraph_models import *
else:
    from networkx_models import *

