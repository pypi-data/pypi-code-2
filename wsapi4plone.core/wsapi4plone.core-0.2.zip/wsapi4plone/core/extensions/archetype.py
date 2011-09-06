# -*- coding: utf-8 -*-
from zope.interface import implements, Attribute
from zope.component import adapts
from wsapi4plone.core.interfaces import ICallbackExtension, IWriteExtension
from wsapi4plone.core.extension import BaseExtension
from wsapi4plone.core.extensions.plone import BaseContentQuery


class IATTopicCriteria(IWriteExtension):
    """An extension to work with Archetypes Topic criteria."""

    types = Attribute("A list of available criteria types.")
    fields = Attribute("A list of available index fields.")
    type_to_fields = Attribute("A dictionary of type to fields "
                               "relationships.")
    field_to_types = Attribute("A dictionary of field to types "
                               "relationships.")

class ATTopicCriteria(BaseExtension):
    implements(IATTopicCriteria)

    def update(self):
        context = self.context
        self.types = [t['name'] for t in context.listCriteriaTypes()]
        self.fields = [f[0] for f in context.listAvailableFields()]
        self.type_to_fields = [(t, [f for f in self.fields
                                    if context.validateAddCriterion(f,t)
                                    ]
                                ,)
                               for t in self.types]
        self.field_to_types = dict([(f, context.allowedCriteriaForField(f),)
                                for f in self.fields
                                ])

    def get(self):
        """
        """
        formatted_criteria = {}
        for crit in self.context.listCriteria():
            crit_key = (crit.field, crit.meta_type,)
            id = 'crit__%s_%s' % crit_key
            assert id == crit.getId(), "%s != %s" % (id, crit.getId(),)
            formatted_criteria[crit_key] = {}
            for name in crit.schema.keys():
                formatted_criteria[crit_key][name] = crit[name]
        return formatted_criteria

    def set(self, **kwargs):
        # TODO ...
        pass

    def get_skeleton(self):
        critters = {}
        for type, fields in self.type_to_fields:
            if not fields:
                continue # can't create it without a field
            crit = self.context.addCriterion(fields[0], type)
            critters[type] = {}
            # criteria schema apparently does not have an items method
            fields = zip(crit.schema.keys(), crit.schema.values())
            for name, field in fields:
                critters[type][field.getName()] = {
                    'type': field.type,
                    'required': bool(field.required)}
        return [self.field_to_types, critters]


class ATTopicContents(BaseContentQuery):

    def arguments(self):
        query_arg = self.context.buildQuery()
        return (query_arg,)
