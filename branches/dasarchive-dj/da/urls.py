# -*- coding: utf-8 -*-
'''
lansite.apps.core.urls
'''

from django.conf.urls.defaults import *

urlpatterns = patterns('da.views',
	url(r'^$',			'index'),
	url(r'^node/(?P<id>\d+)/p/$',	'node_path'),
	url(r'^node/(?P<id>\d+)/t/$',	'node_tree'),
	url(r'^node/(?P<id>\d+)/g/$',	'node_graph'),
	url(r'^node/add/$',		'node_add'),
)
