# -*- coding: utf-8 -*-
'''
lansite.apps.core.urls
'''

from django.conf.urls.defaults import *

urlpatterns = patterns('da.views',
	url(r'^$',			'index'),
	url(r'^node/c/$',		'node_add'),
	url(r'^node/(?P<id>\d+)/r/$',	'node_read'),
	url(r'^node/(?P<id>\d+)/rp/$',	'node_read_path'),
	url(r'^node/(?P<id>\d+)/rt/$',	'node_read_tree'),
	url(r'^node/(?P<id>\d+)/rg/$',	'node_read_graph'),
	url(r'^node/(?P<id>\d+)/u/$',	'node_edit'),
	url(r'^node/(?P<id>\d+)/d/$',	'node_del'),
	url(r'^file/c/$',		'file_create'),
	url(r'^file/(?P<id>\d+)/r/$',	'file_read'),
	url(r'^file/(?P<id>\d+)/u/$',	'file_update'),
	url(r'^file/(?P<id>\d+)/d/$',	'file_delete'),
	url(r'^filter/$',		'filter'),
)
