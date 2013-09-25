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
	# acu
	#url(r'^(?P<uuid>[0-9A-Z]{32})/a/$',	'doc_a'),	# anon (GET/POST=>print))	TODO: POST>view
	#url(r'^(?P<uuid>[0-9A-Z]{32})/c/$',	'doc_c'),	# create (GET/POST=>save)	TODO: POST=>print/view
	#url(r'^(?P<id>\d+)/u/$',		'doc_u'),	# update (GET/POST=>save)	TODO: POST=>print/view
	# rvp
	#url(r'^(?P<id>\d+)/r/$',		'doc_r'),	# read (GET)
	#url(r'^(?P<id>\d+)/v/$',		'doc_v'),	# [pre]view (GET)
	#url(r'^(?P<id>\d+)/p/$',		'doc_p'),	# print (GET)
	#
	#url(r'^(?P<id>\d+)/d/$',		'doc_d'),	# delete (GET)
)
