from django.conf.urls.defaults import *
import re
import kforge.regexps

urlpatterns = patterns('kforge.django.apps.kui.views',

    #
    ##  Application Home Page

    (r'^$',
        'kui.welcome'),

    #
    ##  Feed 

    (r'^feed/$',
        'kui.feed'),

    #
    ##  User Authentication

    (r'^login/(?P<returnPath>(.*))$',
        'accesscontrol.login'),
    (r'^logout(?P<redirect>(.*))$',
        'accesscontrol.logout'),

    #
    ##  Administration
    
    (r'^admin/model/create/(?P<className>(\w*))/$',
        'admin.create'),

    (r'^admin/model/update/(?P<className>(\w*))/(?P<objectKey>([^/]*))/$',
        'admin.update'),

    (r'^admin/model/delete/(?P<className>(\w*))/(?P<objectKey>([^/]*))/$',
        'admin.delete'),

    (r'^admin/model/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/(?P<hasMany>([^/]*))/$',
        'admin.listHasMany'),

    (r'^admin/model/create/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/(?P<hasMany>([^/]*))/$',
        'admin.createHasMany'),

    (r'^admin/model/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/(?P<hasMany>([^/]*))/(?P<attrKey>([^/]*))/$',
        'admin.readHasMany'),

    (r'^admin/model/update/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/(?P<hasMany>([^/]*))/(?P<attrKey>([^/]*))/$',
        'admin.updateHasMany'),

    (r'^admin/model/delete/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/(?P<hasMany>([^/]*))/(?P<attrKey>([^/]*))/$',
        'admin.deleteHasMany'),

    (r'^admin/model/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/$',
        'admin.read'),

    (r'^admin/model/(?P<className>([^/]*))/$',
        'admin.list'),

    (r'^admin/model/$',
        'admin.model'),

    (r'^admin/$',
        'admin.index'),

    #
    ##  Access Control
    
    (r'^accessDenied/(?P<deniedPath>(.*))$',
        'kui.accessDenied'),

    #
    ##  Person

    (r'^person/create/(?P<returnPath>(.*))$',
        'person.create'),
        
    (r'^person/$',
        'person.list'),
        
    (r'^person/find/(?P<startsWith>[\w\d]+)/$',
        'person.search'),
        
    (r'^person/find/$',
        'person.search'),
        
    (r'^person/search/$',
        'person.search'),
        
    (r'^person/home/$',
        'person.read'),
        
    (r'^person/(?P<personName>%s)/$' % kforge.regexps.personName,
        'person.read'),
        
    (r'^person/(?P<personName>%s)/home/$' % kforge.regexps.personName,
        'person.read'),
        
    (r'^person/(?P<personName>%s)/edit/$' % kforge.regexps.personName,
        'person.update'),
        
    (r'^person/(?P<personName>%s)/delete/$' % kforge.regexps.personName,
        'person.delete'),

    #
    ## SSH Key 
    
    (r'^person/(?P<personName>%s)/sshKeys/$' % kforge.regexps.personName,
        'sshKey.list'),

    (r'^person/(?P<personName>%s)/sshKeys/create/$' % kforge.regexps.personName,
        'sshKey.create'),

    (r'^person/(?P<personName>%s)/sshKeys/(?P<sshKeyId>(\d*))/delete/$' % (
        kforge.regexps.personName),  
        'sshKey.delete'),

    (r'^person/(?P<personName>%s)/sshKeys/(?P<sshKeyId>(\d*))/$' % (
        kforge.regexps.personName),  
        'sshKey.read'),

    #
    ##  Project

    (r'^project/create/(?P<returnPath>(.*))$',
        'project.create'),
        
    (r'^project/$',
        'project.list'),
        
    (r'^project/find/(?P<startsWith>[\w\d]+)/$',
        'project.search'),
        
    (r'^project/find/$',
        'project.search'),
        
    (r'^project/search/$',
        'project.search'),
        
    (r'^project/home/$',
        'project.read'),
        
    (r'^project/(?P<projectName>%s)/$' % kforge.regexps.projectName,
        'project.read'),
        
    (r'^project/(?P<projectName>%s)/home/$' % kforge.regexps.projectName,
        'project.read'),
        
    (r'^project/(?P<projectName>%s)/edit/$' % kforge.regexps.projectName,
        'project.update'),
        
    (r'^project/(?P<projectName>%s)/delete/$' % kforge.regexps.projectName,
        'project.delete'),

    (r'^project/(?P<projectName>%s)/join/$' % kforge.regexps.projectName,
        'project.join'),
        

    #
    ##  Member

    (r'^project/(?P<projectName>%s)/members/$' % kforge.regexps.projectName,
        'member.list'),
        
    (r'^project/(?P<projectName>%s)/members/create/$' % kforge.regexps.projectName,
        'member.create'),
        
    (r'^project/(?P<projectName>%s)/members/(?P<personName>%s)/edit/$' % (
        kforge.regexps.projectName, kforge.regexps.personName),  
        'member.update'),
        
    (r'^project/(?P<projectName>%s)/members/(?P<personName>%s)/delete/$' % (
        kforge.regexps.projectName, kforge.regexps.personName),  
        'member.delete'),

    (r'^project/(?P<projectName>%s)/members/(?P<personName>%s)/approve/$' % (
        kforge.regexps.projectName, kforge.regexps.personName),  
        'member.approve'),

    (r'^project/(?P<projectName>%s)/members/(?P<personName>%s)/reject/$' % (
        kforge.regexps.projectName, kforge.regexps.personName),  
        'member.reject'),

    #
    ##  Service
    
    (r'^project/(?P<projectName>%s)/services/$' % kforge.regexps.projectName,
        'service.list'),

    (r'^project/(?P<projectName>%s)/services/create/$' % kforge.regexps.projectName,
        'service.create'),

    (r'^project/(?P<projectName>%s)/services/(?P<serviceName>%s)/edit/$' % (
        kforge.regexps.projectName, kforge.regexps.serviceName),  
        'service.update'),

    (r'^project/(?P<projectName>%s)/services/(?P<serviceName>%s)/delete/$' % (
        kforge.regexps.projectName, kforge.regexps.serviceName),  
        'service.delete'),

    (r'^project/(?P<projectName>%s)/services/(?P<serviceName>%s)/$' % (
        kforge.regexps.projectName, kforge.regexps.serviceName),  
        'service.read'),

    #
    ##  Not Found

    (r'^.*/$',
        'kui.pageNotFound'),
)

