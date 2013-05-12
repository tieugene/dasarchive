from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.views.generic import TemplateView

import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$',			            views.index, name='index'),
	url(r'^help/$',	                views.help, name='help'),
	url(r'^inbox/(?P<path>.*)$',	views.inbox, name='inbox'),
	url(r'^file_add/(?P<path>.*)$',	views.file_add, name='file_add'),
	url(r'^filter/$',			    views.file_filter, name='file_filter'),
	url(r'^resettags/$',			views.resettags, name='resettags'),
	url(r'^file/$',			        views.file_list, name='file_list'),
	url(r'^file/(?P<pk>\d+)/$',	    views.file_detail, name='file_detail'),
	url(r'^file/(?P<pk>\d+)/e/$',	views.file_edit, name='file_edit'),
	url(r'^file/(?P<pk>\d+)/r/$',	views.FileDeleteView.as_view(), name='file_remove'),
	url(r'^file/(?P<pk>\d+)/d/$',	views.file_mark_deleted, name='file_delete'),
	url(r'^file/(?P<pk>\d+)/u/$',	views.file_mark_undeleted, name='file_undelete'),
	url(r'^file/(?P<pk>\d+)/g/$',	views.file_download, name='file_download'),
	url(r'^dav/(?P<path>.*)$',	    views.dav, name='dav'),
	# service
	url(r'^admin/',			include(admin.site.urls)),
	url(r'^login$',			login),
	url(r'^logout$',		logout),
)
