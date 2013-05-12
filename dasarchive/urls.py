from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.views.generic import TemplateView

import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$',			views.index, name='index'),
	url(r'^inbox/(?P<path>.*)$',	views.inbox, name='inbox'),
	url(r'^file_add/(?P<path>.*)$',	views.file_add, name='file_add'),
	#url(r'^file/$',			views.FileListView.as_view(), name='file_list'),
	url(r'^file/$',			views.file_list, name='file_list'),
	url(r'^file/(?P<pk>\d+)/$',	views.FileDetailView.as_view(), name='file_detail'),
	url(r'^file/(?P<pk>\d+)/e/$',	views.FileUpdateView.as_view(), name='file_edit'),
	url(r'^file/(?P<pk>\d+)/r/$',	views.FileDeleteView.as_view(), name='file_remove'),
	url(r'^file/(?P<pk>\d+)/d/$',	views.file_mark_deleted, name='file_delete'),
	url(r'^file/(?P<pk>\d+)/u/$',	views.file_mark_undeleted, name='file_undelete'),
	url(r'^file/(?P<pk>\d+)/g/$',	views.file_download, name='file_download'),
	url(r'^dav/(?P<path>.*)$',	views.dav, name='dav'),
	#url(r'^dav$',			302),
	#url(r'^dav/$',			OPTIONS, PROPFIND(empty list),
	#url(r'^dav/<id>$',		302),
	#url(r'^dav/<id>/$',		OPTIONS, PROPFIND(1 file)),
	#url(r'^dav/<id>/<path>$',	GET/PUT),
	# service
	url(r'^admin/',			include(admin.site.urls)),
	url(r'^login$',			login),
	url(r'^logout$',		logout),
)
