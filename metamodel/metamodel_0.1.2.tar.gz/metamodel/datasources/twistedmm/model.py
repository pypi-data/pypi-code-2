"""
Some extra models for twistedmm.
"""

from metamodel.basemodel import SubscribableModel
from metamodel.properties import Property

class NetworkedModel(SubscribableModel):
    builds = ["SubscribableModel"]

class NetworkedDataSource(SubscribableModel):
    builds = ["SubscribableModel"]
