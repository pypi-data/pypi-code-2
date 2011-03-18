# -*- coding: utf-8 -*-

import haystack
from haystack import indexes
from haystack.indexes import SearchIndex

# TODO: Import loop beim syncen?

#from issues.models import Issue

#from inhouse.models import Booking, Project


haystack.autodiscover()

# TODO: Import from models causes import loop!
# TODO: ProjectStep, Customer, Company, Contact, Issue
# TODO: Filter objects by user


#class BookingIndex(SearchIndex):

    #text = indexes.CharField(document=True, use_template=True)
    #title = indexes.CharField(model_attr='title')


#class IssueIndex(SearchIndex):

    #text = indexes.CharField(document=True, use_template=True)
    #title = indexes.CharField(model_attr='title')
    #description = indexes.CharField(model_attr='description')
    #no = indexes.IntegerField(model_attr='no')


#class ProjectIndex(SearchIndex):

    #text = indexes.CharField(document=True, use_template=True)
    #title = indexes.CharField(model_attr='name')
    #key = indexes.CharField(model_attr='key')
    #description = indexes.CharField(model_attr='description')


#haystack.site.register(Booking, BookingIndex)
#haystack.site.register(Issue, IssueIndex)
#haystack.site.register(Project, ProjectIndex)

